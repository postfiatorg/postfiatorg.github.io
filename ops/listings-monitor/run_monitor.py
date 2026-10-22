#!/usr/bin/env python3
"""Post Fiat listings monitor.

Each run checks freshness and consistency, scores with the Text Improvement
Harness (TIH), and runs an adversarial red-team review of the Coinbase
listing package. The package is the https://postfiat.org/listings/ site
section plus the docs/listings/coinbase/ documents in
postfiatorg/postfiatl1v2. See README.md next to this file.

Exit codes: 0 = no hard failure, 1 = at least one hard failure,
3 = the monitor itself could not run (bad arguments, lock held, crash).
"""

from __future__ import annotations

import argparse
import concurrent.futures as futures
import contextlib
import datetime as dt
import fcntl
import hashlib
import http.client
import json
import os
import pathlib
import posixpath
import re
import shutil
import socket
import sqlite3
import statistics
import subprocess
import sys
import threading
import time
import traceback
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from html.parser import HTMLParser

HERE = pathlib.Path(__file__).resolve().parent
HOME = pathlib.Path.home()

UPSTREAM_REPO = "postfiatorg/postfiatl1v2"
UPSTREAM_GIT_URL = f"https://github.com/{UPSTREAM_REPO}"
CANONICAL_ORIGIN = "https://postfiat.org"
CANONICAL_HOSTS = {"postfiat.org", "www.postfiat.org"}
LISTINGS_PATH = "/listings/"
CHAIN_STATE_PATH = "docs/status/chain-state-current.md"
USER_AGENT = "postfiat-listings-monitor/1.0 (+https://postfiat.org/listings/)"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"
DEFAULT_STATE_DIR = HOME / ".local" / "share" / "postfiat-listings-monitor"
DEFAULT_TIH_DIR = HOME / "repos" / "text-improvement-harness-codex-plugin"

# key -> (path in postfiatl1v2, local file name used for scoring and archiving)
SOURCE_DOCS = {
    "integration_plan": ("docs/listings/coinbase/integration-plan.md", "integration-plan.md"),
    "comparisons": ("docs/listings/coinbase/comparisons.md", "comparisons.md"),
    "reviewer_guide": ("docs/listings/coinbase/reviewer-agent-guide.md", "reviewer-agent-guide.md"),
    "readme": ("README.md", "README.md"),
    "docs_index": ("docs/index.md", "docs-index.md"),
    "whitepaper": ("docs/whitepaper.md", "whitepaper.md"),
}
LISTING_DOC_KEYS = ("integration_plan", "comparisons", "reviewer_guide")
FULL_LANES = ("gpt", "fable", "glm")
SCORE_TARGETS = ("plan", "landing")


# ---------------------------------------------------------------------------
# Adversarial response schema (keep in sync with adversarial_prompt.md)
# ---------------------------------------------------------------------------


def _obj(props: dict) -> dict:
    return {"type": "object", "additionalProperties": False, "required": list(props), "properties": props}


_STR = {"type": "string"}
_SEV = {"type": "string", "enum": ["high", "medium", "low"]}
ADVERSARIAL_TOPICS = [
    "audit_status", "validator_decentralization", "privacy", "navcoin_reserve_proofs",
    "quantum_claims", "tokenomics", "network_status", "regulatory", "other",
]
REQUIRED_TOPICS = ADVERSARIAL_TOPICS[:5]
ADVERSARIAL_SCHEMA = _obj({
    "overall_assessment": _STR,
    "listing_readiness": {"type": "string", "enum": ["ready", "ready_with_fixes", "not_ready"]},
    "unsupported_or_contradicted_claims": {"type": "array", "items": _obj({
        "claim_quote": _STR,
        "source_document": _STR,
        "status": {"type": "string", "enum": ["unsupported", "contradicted", "needs_repo_check"]},
        "problem": _STR,
        "repo_file_to_check": _STR,
        "severity": _SEV,
        "suggested_fix": _STR,
    })},
    "misleading_framing_or_omissions": {"type": "array", "items": _obj({
        "topic": {"type": "string", "enum": ADVERSARIAL_TOPICS},
        "kind": {"type": "string", "enum": ["misleading", "omission", "no_issue"]},
        "quote": _STR,
        "source_document": _STR,
        "problem": _STR,
        "severity": _SEV,
        "suggested_fix": _STR,
    })},
    "broken_or_circular_references": {"type": "array", "items": _obj({
        "reference": _STR,
        "source_document": _STR,
        "kind": {"type": "string", "enum": ["broken", "unpinned", "circular", "dangling"]},
        "problem": _STR,
        "severity": _SEV,
    })},
    "top_coinbase_questions": {"type": "array", "items": _obj({
        "question": _STR,
        "why_it_matters": _STR,
        "where_answer_should_live": _STR,
    })},
    "hostile_journalist_headlines": {"type": "array", "items": _obj({
        "headline": _STR,
        "supporting_quote": _STR,
        "best_available_rebuttal": _STR,
    })},
})
ADVERSARIAL_LIST_KEYS = [k for k, v in ADVERSARIAL_SCHEMA["properties"].items() if v.get("type") == "array"]


# ---------------------------------------------------------------------------
# Small utilities
# ---------------------------------------------------------------------------


def utcnow() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def iso(t: dt.datetime) -> str:
    return t.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_iso(value: str) -> dt.datetime:
    return dt.datetime.fromisoformat(value.strip().replace("Z", "+00:00"))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def md_cell(value, limit: int | None = 240) -> str:
    text = " ".join(str(value if value is not None else "").split())
    if limit and len(text) > limit:
        text = text[: limit - 1] + "…"
    return text.replace("|", "\\|") or " "


def git_identity(repo: pathlib.Path) -> dict:
    def run(*argv: str) -> str:
        res = subprocess.run(["git", "-C", str(repo), *argv], capture_output=True, text=True, timeout=30)
        return res.stdout.strip() if res.returncode == 0 else ""

    sha = run("rev-parse", "HEAD")
    return {
        "path": str(repo),
        "commit": sha or None,
        "branch": run("rev-parse", "--abbrev-ref", "HEAD") or None,
        "dirty": bool(run("status", "--porcelain")) if sha else None,
    }


def short_identity(ident: dict | None) -> str:
    if not ident or not ident.get("commit"):
        return "unknown"
    text = f"{ident['commit'][:9]}"
    if ident.get("branch"):
        text = f"{ident['branch']}@{text}"
    if ident.get("dirty"):
        text += " (uncommitted changes)"
    return text


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def http_fetch(url: str, *, method: str = "GET", headers: dict | None = None, data: bytes | None = None,
               timeout: float = 30.0, max_bytes: int = 25_000_000):
    """Return (status, final_url, body, headers). Raises URLError on transport failure."""
    hdrs = {"User-Agent": USER_AGENT, "Accept": "*/*"}
    hdrs.update(headers or {})
    req = urllib.request.Request(url, data=data, method=method, headers=hdrs)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = b"" if method == "HEAD" else resp.read(max_bytes)
            return resp.status, resp.geturl(), body, {k.lower(): v for k, v in resp.headers.items()}
    except urllib.error.HTTPError as exc:
        hdr = {k.lower(): v for k, v in (exc.headers or {}).items()}
        try:
            body = exc.read(65536)
        except Exception:
            body = b""
        return exc.code, url, body, hdr


# ---------------------------------------------------------------------------
# Findings
# ---------------------------------------------------------------------------


class Findings:
    """hard = exit nonzero; warn = flagged in the report; info = context."""

    def __init__(self, strict: bool):
        self.items: list[dict] = []
        self.strict = strict
        self._lock = threading.Lock()

    def add(self, level: str, check: str, message: str, *, escalate: bool = False, **detail) -> None:
        if escalate and self.strict and level == "warn":
            level = "hard"
            message += " (escalated by --strict)"
        item = {"level": level, "check": check, "message": message}
        if detail:
            item["detail"] = detail
        with self._lock:
            self.items.append(item)

    def hard(self, check: str, message: str, **detail) -> None:
        self.add("hard", check, message, **detail)

    def warn(self, check: str, message: str, *, escalate: bool = False, **detail) -> None:
        self.add("warn", check, message, escalate=escalate, **detail)

    def info(self, check: str, message: str, **detail) -> None:
        self.add("info", check, message, **detail)

    def of(self, level: str) -> list[dict]:
        return [f for f in self.items if f["level"] == level]


# ---------------------------------------------------------------------------
# GitHub access (public data; token from env or `gh auth token` only raises
# the API rate limit and is never written anywhere)
# ---------------------------------------------------------------------------


class GitHub:
    def __init__(self) -> None:
        self._token = self._discover_token()
        self.api_calls = 0
        self.raw_calls = 0

    @staticmethod
    def _discover_token() -> str | None:
        for name in ("GITHUB_TOKEN", "GH_TOKEN"):
            value = os.environ.get(name, "").strip()
            if value:
                return value
        if shutil.which("gh"):
            try:
                res = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, timeout=15)
                if res.returncode == 0 and res.stdout.strip():
                    return res.stdout.strip()
            except (OSError, subprocess.SubprocessError):
                pass
        return None

    @property
    def auth_mode(self) -> str:
        return "token" if self._token else "anonymous"

    def api(self, path: str, params: dict | None = None, timeout: float = 30.0):
        url = "https://api.github.com/" + path.lstrip("/")
        if params:
            url += "?" + urllib.parse.urlencode(params)
        headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        status = None
        body = b""
        for attempt in range(3):
            self.api_calls += 1
            try:
                status, _, body, _ = http_fetch(url, headers=headers, timeout=timeout)
            except (urllib.error.URLError, TimeoutError, OSError, http.client.HTTPException):
                status = None
            if status in (None, 500, 502, 503, 504):
                time.sleep(2 * (attempt + 1))
                continue
            break
        if status == 200:
            return status, json.loads(body.decode("utf-8"))
        return status, None

    def raw(self, ref: str, path: str, timeout: float = 60.0):
        url = f"https://raw.githubusercontent.com/{UPSTREAM_REPO}/{ref}/{urllib.parse.quote(path)}"
        status = None
        body = b""
        for attempt in range(3):
            self.raw_calls += 1
            try:
                status, _, body, _ = http_fetch(url, timeout=timeout)
            except (urllib.error.URLError, TimeoutError, OSError, http.client.HTTPException):
                status = None
            if status in (None, 429, 500, 502, 503, 504):
                time.sleep(2 * (attempt + 1))
                continue
            break
        return status, (body if status == 200 else None)


def ls_remote_main() -> str:
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0")
    res = subprocess.run(["git", "ls-remote", UPSTREAM_GIT_URL, "refs/heads/main"],
                         capture_output=True, text=True, timeout=120, env=env)
    if res.returncode != 0 or not res.stdout.strip():
        raise RuntimeError(f"git ls-remote failed: {res.stderr.strip()[:300]}")
    sha = res.stdout.split()[0]
    if not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise RuntimeError(f"unexpected ls-remote output: {res.stdout[:120]!r}")
    return sha


# ---------------------------------------------------------------------------
# HTML parsing
# ---------------------------------------------------------------------------


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.links: list[tuple[str, str]] = []
        self.ids: set[str] = set()
        self._in_title = False
        self._anchors: list[list] = []

    def handle_starttag(self, tag, attrs):
        attr = {k: (v or "") for k, v in attrs}
        if attr.get("id"):
            self.ids.add(attr["id"])
        if tag == "a":
            if attr.get("name"):
                self.ids.add(attr["name"])
            if "href" in attr:
                self._anchors.append([attr["href"], []])
        elif tag == "title":
            self._in_title = True

    def handle_endtag(self, tag):
        if tag == "a" and self._anchors:
            href, parts = self._anchors.pop()
            self.links.append((href.strip(), " ".join("".join(parts).split())))
        elif tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        for anchor in self._anchors:
            anchor[1].append(data)

    def close(self):
        super().close()
        while self._anchors:
            href, parts = self._anchors.pop()
            self.links.append((href.strip(), " ".join("".join(parts).split())))


def parse_html(html: str) -> PageParser:
    parser = PageParser()
    parser.feed(html)
    parser.close()
    return parser


# ---------------------------------------------------------------------------
# Chain-state facts
# ---------------------------------------------------------------------------

NUMBER_WORDS = {w: i for i, w in enumerate(
    "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen "
    "fifteen sixteen seventeen eighteen nineteen twenty".split())}
NUM_ALT = r"\d{1,3}|" + "|".join(sorted(NUMBER_WORDS, key=len, reverse=True))
NETWORK_RE = re.compile(r"\bpostfiat-[a-z0-9-]*?(?:devnet|testnet|mainnet)(?:-[a-z0-9]+)*\b", re.I)
VALIDATOR_CLAIM_RES = [
    re.compile(rf"\b(?P<n>{NUM_ALT})-validator\b(?!-)", re.I),
    re.compile(rf"\b(?P<n>{NUM_ALT}) validator (?:devnet|network|fleet|set|chain|cluster|deployment)\b", re.I),
    re.compile(rf"\ball (?P<n>{NUM_ALT}) (?:of the )?(?:[A-Za-z]+[- ])?validators\b", re.I),
    re.compile(rf"\b(?P<n>{NUM_ALT}) (?:Foundation|project|permissioned|known|devnet|L1)[- ]?"
               rf"(?:administered |operated |run |controlled |hosted )?validators\b", re.I),
    re.compile(r"\bvalidators?(?: count)?\s*[:|]\s*(?P<n>\d{1,3})\b", re.I),
]
OTHER_NETWORK_RE = re.compile(r"testnet|postfiatd|\bVHS\b|validator history|legacy|XRPL|XRP Ledger|\bUNL\b|Ethereum", re.I)
CURRENT_NETWORK_HINT_RE = re.compile(r"devnet|postfiatl1v2|L1v2|new L1", re.I)
HISTORICAL_RE = re.compile(r"\b(previous|former|formerly|retired|historical|old|earlier|until)\b", re.I)
HYPOTHETICAL_RE = re.compile(r"\b(example|hypothetical|would|could|if|suppose|target|planned|future|e\.g)\b", re.I)


def to_int(token: str) -> int | None:
    token = token.lower()
    return int(token) if token.isdigit() else NUMBER_WORDS.get(token)


def parse_chain_state(text: str) -> dict:
    facts: dict = {"network": None, "validators": None, "validators_basis": None, "updated": None}
    m = re.search(r"^Updated:\s*`([^`]+)`", text, re.M)
    if m:
        facts["updated"] = m.group(1)
    m = re.search(r"^\|\s*Chain\s*\|\s*`([^`]+)`", text, re.M)
    if m:
        facts["network"] = m.group(1)
    else:
        common = Counter(x.lower() for x in NETWORK_RE.findall(text)).most_common(1)
        facts["network"] = common[0][0] if common else None
    head = "\n".join(text.splitlines()[:60])
    m = re.search(rf"\ball ({NUM_ALT}) validators\b", head, re.I)
    if m:
        facts["validators"] = to_int(m.group(1))
        facts["validators_basis"] = f"latest status headline: {m.group(0)!r}"
    else:
        m = re.search(r"^\|\s*Validators\s*\|\s*(\d+)", text, re.M)
        if m:
            facts["validators"] = int(m.group(1))
            facts["validators_basis"] = "first `| Validators |` table row"
    return facts


def sentence_around(text: str, start: int, end: int) -> str:
    left = max(text.rfind(c, 0, start) for c in ".!?\n")
    rights = [i for i in (text.find(c, end) for c in ".!?\n") if i != -1]
    right = min(rights) if rights else len(text)
    return " ".join(text[left + 1: right + 1].split())


def extract_chain_claims(label: str, text: str) -> list[dict]:
    claims: list[dict] = []
    for m in NETWORK_RE.finditer(text):
        claims.append({"kind": "network", "value": m.group(0), "page": label,
                       "sentence": sentence_around(text, m.start(), m.end())})
    seen_spans: set[tuple[int, int]] = set()
    for rx in VALIDATOR_CLAIM_RES:
        for m in rx.finditer(text):
            span = (m.start("n"), m.end("n"))
            if span in seen_spans:
                continue
            seen_spans.add(span)
            claims.append({"kind": "validators", "value": to_int(m.group("n")), "match": m.group(0), "page": label,
                           "sentence": sentence_around(text, m.start(), m.end())})
    return claims


def judge_chain_claims(claims: list[dict], facts: dict) -> None:
    current_net = (facts.get("network") or "").lower()
    for c in claims:
        sentence = c["sentence"]
        if c["kind"] == "network":
            if not current_net:
                c["verdict"] = "unknown (no current network parsed)"
            elif c["value"].lower() == current_net:
                c["verdict"] = "match"
            elif HISTORICAL_RE.search(sentence):
                c["verdict"] = "historical mention"
            elif "testnet" in c["value"].lower() and OTHER_NETWORK_RE.search(sentence.replace(c["value"], "")):
                c["verdict"] = "other network (testnet/postfiatd/external), not compared"
            else:
                c["verdict"] = "MISMATCH"
        else:
            if OTHER_NETWORK_RE.search(sentence) and not CURRENT_NETWORK_HINT_RE.search(sentence):
                c["verdict"] = "other network (testnet/postfiatd/external), not compared"
            elif facts.get("validators") is None:
                c["verdict"] = "unknown (no current count parsed)"
            elif c["value"] == facts["validators"]:
                c["verdict"] = "match"
            elif HISTORICAL_RE.search(sentence):
                c["verdict"] = "historical mention"
            elif HYPOTHETICAL_RE.search(sentence):
                c["verdict"] = "example or hypothetical, not compared"
            else:
                c["verdict"] = "MISMATCH"


# ---------------------------------------------------------------------------
# Front matter / mirrors
# ---------------------------------------------------------------------------

GH_BLOB_RE = re.compile(r"^https?://github\.com/postfiatorg/postfiatl1v2/(?:blob|tree)/([^/]+)/([^#?]+)", re.I)


def parse_front_matter(text: str) -> dict:
    out: dict = {}
    if text.startswith("---"):
        end = text.find("\n---", 3)
        block = text[3:end] if end != -1 else ""
        pattern = re.compile(r"^([A-Za-z0-9_]+):\s*(.*?)\s*$")
    elif text.startswith("+++"):
        end = text.find("\n+++", 3)
        block = text[3:end] if end != -1 else ""
        pattern = re.compile(r"^([A-Za-z0-9_]+)\s*=\s*(.*?)\s*$")
    else:
        return out
    for line in block.splitlines():
        m = pattern.match(line)
        if m:
            out[m.group(1)] = m.group(2).strip().strip('"').strip("'")
    return out


def scan_site_repo_mirrors(site_repo: pathlib.Path) -> list[dict]:
    mirrors = []
    content = site_repo / "content"
    for md in sorted(content.rglob("*.md")) if content.exists() else []:
        try:
            head = md.read_text(encoding="utf-8", errors="replace")[:8000]
        except OSError:
            continue
        fm = parse_front_matter(head)
        commit, path = fm.get("source_commit"), fm.get("source_path")
        if not commit or not path:
            continue
        repo = (fm.get("source_repo") or UPSTREAM_REPO).strip().rstrip("/")
        if repo.split("github.com/")[-1].lower() != UPSTREAM_REPO:
            continue
        rel = md.relative_to(site_repo).as_posix()
        url = fm.get("url") or "/" + re.sub(r"(_?index)?\.md$", "", rel[len("content/"):]).strip("/") + "/"
        mirrors.append({"page": rel, "url": url, "source_path": path.lstrip("/"), "source_commit": commit,
                        "page_status": fm.get("status") or "published",
                        "source_dirty": fm.get("source_dirty", "").lower() == "true",
                        "source_branch": fm.get("source_branch") or None, "found_in": "site front matter"})
    return mirrors


def walk_json_strings(node, path="$"):
    if isinstance(node, dict):
        for k, v in node.items():
            yield from walk_json_strings(v, f"{path}.{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk_json_strings(v, f"{path}[{i}]")
    elif isinstance(node, str):
        yield path, node


def walk_json_dicts(node):
    if isinstance(node, dict):
        yield node
        for v in node.values():
            yield from walk_json_dicts(v)
    elif isinstance(node, list):
        for v in node:
            yield from walk_json_dicts(v)


# ---------------------------------------------------------------------------
# Markdown link extraction (for the listing docs)
# ---------------------------------------------------------------------------

MD_LINK_RE = re.compile(r"\[[^\]\n]*\]\(\s*<?([^)\s>]+)>?(?:\s+[\"'][^\"'\n]*[\"'])?\s*\)")
MD_REF_RE = re.compile(r"^\s{0,3}\[[^\]\n]+\]:\s*<?(\S+?)>?(?:\s|$)", re.M)
FENCE_RE = re.compile(r"^(```|~~~).*?^\1", re.M | re.S)


def markdown_links(text: str) -> list[str]:
    body = FENCE_RE.sub("", text)
    return MD_LINK_RE.findall(body) + MD_REF_RE.findall(body)


# ---------------------------------------------------------------------------
# Adversarial helpers
# ---------------------------------------------------------------------------


def parse_json_lenient(text: str):
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?", "", stripped).strip()
        stripped = re.sub(r"```$", "", stripped).strip()
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        start, end = stripped.find("{"), stripped.rfind("}")
        if start == -1 or end <= start:
            raise
        return json.loads(stripped[start: end + 1])


_QUOTE_MAP = str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"', "–": "-",
                            "—": "-", "−": "-", " ": " ", "‑": "-", "…": "..."})


def normalize_for_match(text: str) -> str:
    text = text.translate(_QUOTE_MAP)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)  # markdown links -> text
    text = re.sub(r"[*`]+", "", text)
    text = re.sub(r"^\s{0,3}#{1,6}\s+", "", text, flags=re.M)
    return " ".join(text.lower().split())


def quote_status(quote: str, corpus_norm: str) -> str:
    q = normalize_for_match(quote).strip(" .\"'")
    if not q:
        return "empty"
    if q in corpus_norm:
        return "verified"
    if len(q) > 60:
        mid = len(q) // 2
        for seg in (q[:50], q[mid - 25: mid + 25], q[-50:]):
            if seg in corpus_norm:
                return "partial"
    return "not_found"


def clean_repo_path(value: str) -> list[str]:
    paths = []
    for part in re.split(r",\s*|\s+and\s+|;\s*|\s+or\s+", value or ""):
        p = part.strip().strip("`'\"")
        m = GH_BLOB_RE.match(p)
        if m:
            p = urllib.parse.unquote(m.group(2))
        p = re.sub(r"^(?:https?://github\.com/)?(?:postfiatorg/)?postfiatl1v2/", "", p)
        p = re.sub(r"\s*\(.*$", "", p)
        p = p.split("#", 1)[0]
        p = re.sub(r":\d+(?:-\d+)?$", "", p)
        p = p.lstrip("./").strip().rstrip("/")
        if p and " " not in p:
            paths.append(p)
    return paths


def path_status(path: str, tree: dict | None, docs_repo: pathlib.Path | None) -> str:
    if tree is not None and (path in tree["blobs"] or path in tree["dirs"]):
        return "exists at main"
    if docs_repo is not None and (docs_repo / path).exists():
        return "local checkout only"
    if tree is None:
        return "unknown (no repo tree)"
    return "NOT FOUND"


def empty_adversarial_result() -> dict:
    return {
        "overall_assessment": "",
        "listing_readiness": "",
        **{k: [] for k in ADVERSARIAL_LIST_KEYS},
    }


def shape_problems(result) -> list[str]:
    problems = []
    if not isinstance(result, dict):
        return ["response is not a JSON object"]
    for key in ADVERSARIAL_SCHEMA["required"]:
        if key not in result:
            problems.append(f"missing key {key}")
    for key in ADVERSARIAL_LIST_KEYS:
        if key in result and not isinstance(result[key], list):
            problems.append(f"{key} is not a list")
    questions = result.get("top_coinbase_questions")
    if isinstance(questions, list) and len(questions) != 5:
        problems.append(f"top_coinbase_questions has {len(questions)} items, expected 5")
    topics = {i.get("topic") for i in result.get("misleading_framing_or_omissions") or [] if isinstance(i, dict)}
    missing = [t for t in REQUIRED_TOPICS if t not in topics]
    if missing:
        problems.append("framing review skipped required topics: " + ", ".join(missing))
    return problems


def annotate_adversarial(result: dict, corpus_norm: str, tree: dict | None, docs_repo: pathlib.Path | None) -> dict:
    stats = {"quotes_checked": 0, "quotes_verified": 0, "quotes_partial": 0, "quotes_not_found": 0,
             "paths_checked": 0, "paths_found": 0, "paths_missing": 0}
    for item in result.get("unsupported_or_contradicted_claims") or []:
        if not isinstance(item, dict):
            continue
        qs = quote_status(str(item.get("claim_quote", "")), corpus_norm)
        item["_quote_check"] = qs
        stats["quotes_checked"] += 1
        stats[{"verified": "quotes_verified", "partial": "quotes_partial"}.get(qs, "quotes_not_found")] += 1
        checks = []
        for p in clean_repo_path(str(item.get("repo_file_to_check", ""))):
            st = path_status(p, tree, docs_repo)
            checks.append({"path": p, "status": st})
            stats["paths_checked"] += 1
            stats["paths_found" if st != "NOT FOUND" else "paths_missing"] += 1
        item["_path_check"] = checks
    for item in result.get("broken_or_circular_references") or []:
        if not isinstance(item, dict):
            continue
        ref = str(item.get("reference", "")).strip().strip("`")
        source = str(item.get("source_document", ""))
        if ref.startswith(("../", "./")) and source.startswith("repo:"):
            ref = posixpath.normpath(posixpath.join(posixpath.dirname(source[len("repo:"):]), ref.split("#", 1)[0]))
        if (re.match(r"^https?://", ref) and not GH_BLOB_RE.match(ref)) or (source.startswith("site:") and ref.startswith("/")):
            continue  # web URLs and site paths are covered by the link check, not the repository tree
        checks = [{"path": p, "status": path_status(p, tree, docs_repo)} for p in clean_repo_path(ref)
                  if ("/" in p or "." in p) and "@" not in p]
        if checks:
            item["_path_check"] = checks
            if item.get("kind") in ("broken", "dangling") and all(c["status"] != "NOT FOUND" for c in checks):
                stats["refs_contradicted_by_tree"] = stats.get("refs_contradicted_by_tree", 0) + 1
    for key, field in (("misleading_framing_or_omissions", "quote"), ("hostile_journalist_headlines", "supporting_quote")):
        for item in result.get(key) or []:
            if isinstance(item, dict) and str(item.get(field, "")).strip():
                item["_quote_check"] = quote_status(str(item[field]), corpus_norm)
    return stats


# ---------------------------------------------------------------------------
# Pricing / usage
# ---------------------------------------------------------------------------


class Pricing:
    def __init__(self, cache_path: pathlib.Path):
        self.table: dict[str, dict] = {}
        self.source = "none"
        try:
            if cache_path.exists() and time.time() - cache_path.stat().st_mtime < 86400:
                self.table = json.loads(cache_path.read_text())
                self.source = f"cache {cache_path}"
            else:
                status, _, body, _ = http_fetch(OPENROUTER_MODELS_URL, timeout=30)
                if status == 200:
                    for m in json.loads(body).get("data", []):
                        p = m.get("pricing") or {}
                        try:
                            self.table[m["id"]] = {"prompt": float(p.get("prompt", 0)),
                                                   "completion": float(p.get("completion", 0))}
                        except (TypeError, ValueError):
                            continue
                    cache_path.write_text(json.dumps(self.table))
                    self.source = OPENROUTER_MODELS_URL
        except Exception as exc:  # pricing is best effort
            self.source = f"unavailable ({exc.__class__.__name__})"

    def rate(self, provider: str, model: str) -> dict | None:
        key = model if "/" in model else f"{provider}/{model}"
        return self.table.get(key)

    def cost(self, provider: str, model: str, tokens_in: int, tokens_out: int) -> float | None:
        rate = self.rate(provider, model)
        if not rate:
            return None
        return tokens_in * rate["prompt"] + tokens_out * rate["completion"]


def usage_tokens(usage: dict) -> tuple[int, int]:
    tin = usage.get("prompt_tokens", usage.get("input_tokens", 0)) or 0
    tout = usage.get("completion_tokens", usage.get("output_tokens", 0)) or 0
    return int(tin), int(tout)


def summarize_receipts(usage_dir: pathlib.Path, pricing: Pricing) -> list[dict]:
    rows: dict[tuple, dict] = {}
    for path in sorted(usage_dir.glob("*.json")) if usage_dir.exists() else []:
        try:
            rec = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        usage = rec.get("usage") or {}
        tin, tout = usage_tokens(usage)
        cost = usage.get("cost")
        source = "provider"
        if not isinstance(cost, (int, float)):
            cost = pricing.cost(rec.get("provider", ""), rec.get("model", ""), tin, tout)
            source = "list price"
        key = (rec.get("provider"), rec.get("model"))
        row = rows.setdefault(key, {"provider": key[0], "model": key[1], "calls": 0, "completed": 0,
                                    "tokens_in": 0, "tokens_out": 0, "cost_usd": 0.0, "cost_basis": set()})
        row["calls"] += 1
        row["completed"] += 1 if rec.get("state") == "RECEIVED" else 0
        row["tokens_in"] += tin
        row["tokens_out"] += tout
        if cost is not None:
            row["cost_usd"] += float(cost)
            row["cost_basis"].add(source)
    out = []
    for row in rows.values():
        row["cost_basis"] = ", ".join(sorted(row["cost_basis"])) or "unknown"
        out.append(row)
    return out


# ---------------------------------------------------------------------------
# The monitor
# ---------------------------------------------------------------------------


class Monitor:
    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.started = utcnow()
        self.mode = args.mode
        if self.mode == "auto":
            self.mode = "full" if self.started.weekday() == 0 else "cheap"
        self.run_id = f"{self.started:%Y%m%dT%H%M%SZ}-{self.mode}"
        self.state = args.state_dir.expanduser().resolve()
        self.db = (args.db or self.state / "tih.sqlite3").expanduser().resolve()
        self.run_dir = self.state / "runs" / self.run_id
        self.reports_dir = self.state / "reports"
        self.usage_dir = self.run_dir / "usage"
        self.F = Findings(args.strict)
        self.gh = GitHub()
        self.base_url = args.base_url if args.base_url.endswith("/") else args.base_url + "/"
        self.build_dir: pathlib.Path | None = args.build_dir.resolve() if args.build_dir else None
        self.site_repo: pathlib.Path | None = args.site_repo.expanduser().resolve() if args.site_repo else None
        self.docs_repo: pathlib.Path | None = args.docs_repo.expanduser().resolve() if args.docs_repo else None
        self.tih_dir: pathlib.Path = args.tih_dir.expanduser().resolve()
        self.target_kind = "live"
        self.main_sha: str | None = None
        self.main_date: str | None = None
        self.tree: dict | None = None
        self.chain_text: str | None = None
        self.data: dict = {"checks": {}}
        self.pages: dict[str, dict] = {}
        self.mirror_urls: dict[str, str] = {}
        self.index_json = None
        self.docs: dict[str, dict] = {}
        self.history = self._load_history()
        self.tih_site = None
        self.tih_game = None
        self.tih_keys = None

    # -- setup -------------------------------------------------------------

    def _load_history(self) -> list[dict]:
        path = self.state / "history.jsonl"
        rows = []
        if path.exists():
            for line in path.read_text().splitlines():
                with contextlib.suppress(json.JSONDecodeError):
                    rows.append(json.loads(line))
        return rows

    def import_tih(self) -> None:
        if not (self.tih_dir / "text_improvement_harness").is_dir():
            raise SystemExit(f"TIH not found at {self.tih_dir} (use --tih-dir)")
        sys.path.insert(0, str(self.tih_dir))
        from text_improvement_harness import game as tih_game  # noqa: E402
        from text_improvement_harness import model_clients as tih_keys  # noqa: E402
        from text_improvement_harness import site as tih_site  # noqa: E402
        self.tih_site, self.tih_game, self.tih_keys = tih_site, tih_game, tih_keys

    def is_local_target(self) -> bool:
        host = urllib.parse.urlparse(self.base_url).hostname or ""
        return host in ("127.0.0.1", "localhost", "::1")

    def to_target(self, url: str) -> str:
        """Map canonical postfiat.org URLs onto the target when the target is a local build."""
        p = urllib.parse.urlparse(url)
        base = urllib.parse.urlparse(self.base_url)
        if p.scheme in ("http", "https") and (p.hostname or "").lower() in CANONICAL_HOSTS \
                and (base.hostname or "").lower() not in CANONICAL_HOSTS:
            return urllib.parse.urlunparse((base.scheme, base.netloc, p.path or "/", p.params, p.query, p.fragment))
        return url

    def is_target_url(self, url: str) -> bool:
        return urllib.parse.urlparse(url).netloc == urllib.parse.urlparse(self.base_url).netloc

    def hugo_build(self, dest: pathlib.Path, base_url: str | None) -> None:
        hugo = self.args.hugo
        if dest.exists():
            shutil.rmtree(dest)
        cmd = [hugo, "--gc", "--minify", "--source", str(self.site_repo), "-d", str(dest)]
        if base_url:
            cmd += ["--baseURL", base_url]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        (self.run_dir / "logs").mkdir(parents=True, exist_ok=True)
        (self.run_dir / "logs" / "hugo-build.log").write_text(
            "$ " + " ".join(cmd) + f"\nexit={res.returncode}\n\n{res.stdout}\n{res.stderr}")
        if res.returncode != 0:
            raise RuntimeError(f"hugo build failed (exit {res.returncode}); see logs/hugo-build.log")

    @contextlib.contextmanager
    def target(self):
        """Prepare the site target: optional local build + server for the run's lifetime."""
        a = self.args
        proc = None
        try:
            if a.serve_local:
                if not self.site_repo:
                    raise SystemExit("--serve-local needs --site-repo")
                port = free_port()
                self.base_url = f"http://127.0.0.1:{port}/"
                self.build_dir = self.state / "site-build-served"
                self.hugo_build(self.build_dir, self.base_url)
                proc = subprocess.Popen(
                    [sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1",
                     "--directory", str(self.build_dir)],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                deadline = time.time() + 20
                while time.time() < deadline:
                    try:
                        if http_fetch(self.base_url, timeout=2)[0] in (200, 404):
                            break
                    except (urllib.error.URLError, OSError):
                        time.sleep(0.3)
                self.target_kind = "local build served by the monitor"
            elif self.site_repo and not self.build_dir:
                self.build_dir = self.state / "site-build"
                self.hugo_build(self.build_dir, None)
                self.target_kind = "local build (served externally)" if self.is_local_target() else "live"
            else:
                self.target_kind = "local build (served externally)" if self.is_local_target() else "live"
            yield
        finally:
            if proc is not None:
                proc.terminate()
                try:
                    proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    proc.kill()

    # -- stage 1: upstream -------------------------------------------------

    def stage_upstream(self) -> None:
        F = self.F
        try:
            self.main_sha = ls_remote_main()
        except Exception as exc:
            F.hard("upstream", f"cannot read public main of {UPSTREAM_REPO}: {exc}")
            return
        status, commit = self.gh.api(f"repos/{UPSTREAM_REPO}/commits/{self.main_sha}")
        if commit:
            self.main_date = commit["commit"]["committer"]["date"]
        status, tree = self.gh.api(f"repos/{UPSTREAM_REPO}/git/trees/{self.main_sha}", {"recursive": "1"}, timeout=90)
        if tree:
            blobs = {e["path"] for e in tree.get("tree", []) if e.get("type") == "blob"}
            dirs = {e["path"] for e in tree.get("tree", []) if e.get("type") == "tree"}
            self.tree = {"blobs": blobs, "dirs": dirs, "truncated": bool(tree.get("truncated"))}
            if tree.get("truncated"):
                F.warn("upstream", "GitHub returned a truncated repository tree; path checks may miss files")
        else:
            F.warn("upstream", f"could not list the repository tree at main (HTTP {status}); path checks skipped")
        self.data["upstream"] = {"repo": UPSTREAM_REPO, "main_sha": self.main_sha, "main_commit_date": self.main_date,
                                 "tree_files": len(self.tree["blobs"]) if self.tree else None,
                                 "github_auth": self.gh.auth_mode}

    def stage_chain_state(self) -> None:
        F = self.F
        if not self.main_sha:
            return
        status, body = self.gh.raw(self.main_sha, CHAIN_STATE_PATH)
        if body is None:
            F.hard("chain-facts", f"{CHAIN_STATE_PATH} not readable at main (HTTP {status})")
            return
        self.chain_text = body.decode("utf-8", "replace")
        facts = parse_chain_state(self.chain_text)
        facts["source"] = f"{UPSTREAM_REPO}@{self.main_sha[:9]}:{CHAIN_STATE_PATH}"
        if not facts["network"] or facts["validators"] is None:
            F.warn("chain-facts", "could not parse network name and validator count from chain-state-current.md",
                   facts=facts)
        if facts.get("updated"):
            with contextlib.suppress(ValueError):
                age = (self.started - parse_iso(facts["updated"])).total_seconds() / 86400
                facts["updated_age_days"] = round(age, 1)
                if age > self.args.chain_state_stale_days:
                    F.warn("chain-facts", f"chain-state-current.md last updated {age:.0f} days ago ({facts['updated']})")
        self.data["chain_facts"] = facts

    # -- stage 2: site pages -----------------------------------------------

    def fetch_page(self, url: str) -> dict | None:
        try:
            status, final, body, hdr = http_fetch(url, timeout=self.args.link_timeout)
        except (urllib.error.URLError, OSError, http.client.HTTPException) as exc:
            return {"url": url, "status": None, "error": str(exc)}
        page = {"url": url, "status": status, "final_url": final, "content_type": hdr.get("content-type", "")}
        if status == 200 and "html" in page["content_type"]:
            html = body.decode("utf-8", "replace")
            refresh = re.search(r"http-equiv=[\"']?refresh[^>]*content=[\"']?\d+;\s*url=([^\"'>\s]+)", html, re.I)
            if refresh and len(html) < 4000:
                page["refresh"] = urllib.parse.urljoin(url, refresh.group(1))
                return page
            parsed = parse_html(html)
            path = urllib.parse.urlparse(url).path or "/"
            page.update({
                "path": path,
                "title": parsed.title.strip(),
                "links": parsed.links,
                "ids": parsed.ids,
                "text": self.tih_site.extract_page_snapshot(html, path),
                "html_sha256": sha256_bytes(body),
            })
        return page

    def stage_site(self) -> None:
        F = self.F
        start = urllib.parse.urljoin(self.base_url, LISTINGS_PATH.lstrip("/"))
        queue = [start]
        with contextlib.suppress(Exception):
            status, _, body, _ = http_fetch(urllib.parse.urljoin(self.base_url, "sitemap.xml"), timeout=30)
            if status == 200:
                for loc in re.findall(r"<loc>\s*(.*?)\s*</loc>", body.decode("utf-8", "replace")):
                    loc = self.to_target(loc)
                    if self.is_target_url(loc) and urllib.parse.urlparse(loc).path.startswith(LISTINGS_PATH):
                        queue.append(loc)
        seen: set[str] = set()
        while queue and len(seen) < self.args.max_pages:
            url = urllib.parse.urldefrag(queue.pop(0))[0]
            if url in seen:
                continue
            seen.add(url)
            page = self.fetch_page(url)
            if url == start and (page is None or page.get("status") != 200):
                F.hard("listings-page", f"{start} is not serving (HTTP {page.get('status') if page else None}"
                       f"{'; ' + page['error'] if page and page.get('error') else ''})")
            if page and page.get("refresh"):
                target = urllib.parse.urldefrag(self.to_target(page["refresh"]))[0]
                if self.is_target_url(target) and target not in seen:
                    queue.append(target)
                continue
            if not page or "text" not in page:
                continue
            self.pages[url] = page
            for href, _text in page["links"]:
                absolute = urllib.parse.urldefrag(self.to_target(urllib.parse.urljoin(url, href)))[0]
                path = urllib.parse.urlparse(absolute).path
                last = path.rsplit("/", 1)[-1]
                if self.is_target_url(absolute) and path.startswith(LISTINGS_PATH) and \
                        ("." not in last or last.endswith(".html")) and absolute not in seen:
                    queue.append(absolute)
        pages_dir = self.run_dir / "pages"
        pages_dir.mkdir(parents=True, exist_ok=True)
        for page in self.pages.values():
            slug = re.sub(r"[^A-Za-z0-9._-]+", "-", page["path"].strip("/")) or "home"
            (pages_dir / f"{slug}.txt").write_text(page["text"])
        self.data["listings_pages"] = [
            {"url": p["url"], "path": p["path"], "title": p["title"], "links": len(p["links"]),
             "words": len(p["text"].split()), "html_sha256": p["html_sha256"]}
            for p in sorted(self.pages.values(), key=lambda p: p["path"])]
        if self.pages:
            F.info("listings-page", f"{len(self.pages)} /listings/ page(s) crawled")

        # /listings/index.json
        idx_url = urllib.parse.urljoin(self.base_url, "listings/index.json")
        check = {"url": idx_url}
        try:
            status, _, body, hdr = http_fetch(idx_url, timeout=30)
            check["status"] = status
            if status != 200:
                F.hard("listings-index-json", f"{idx_url} returned HTTP {status}")
            else:
                try:
                    self.index_json = json.loads(body.decode("utf-8"))
                    check["valid"] = True
                    check["top_level"] = type(self.index_json).__name__
                    if isinstance(self.index_json, dict):
                        check["keys"] = sorted(self.index_json)[:40]
                    check["sha256"] = sha256_bytes(body)
                except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                    check["valid"] = False
                    F.hard("listings-index-json", f"{idx_url} is not valid JSON: {exc}")
        except (urllib.error.URLError, OSError, http.client.HTTPException) as exc:
            F.hard("listings-index-json", f"{idx_url} unreachable: {exc}")
        self.data["checks"]["index_json"] = check

        # /llms.txt
        llms_url = urllib.parse.urljoin(self.base_url, "llms.txt")
        check = {"url": llms_url}
        try:
            status, _, body, _ = http_fetch(llms_url, timeout=30)
            check["status"] = status
            text = body.decode("utf-8", "replace") if status == 200 else ""
            check["mentions_listings"] = "/listings/" in text
            if status != 200:
                F.warn("llms-txt", f"{llms_url} returned HTTP {status}", escalate=True)
            elif not check["mentions_listings"]:
                F.warn("llms-txt", "/llms.txt does not mention /listings/", escalate=True)
        except (urllib.error.URLError, OSError, http.client.HTTPException) as exc:
            F.warn("llms-txt", f"{llms_url} unreachable: {exc}", escalate=True)
        self.data["checks"]["llms_txt"] = check

    # -- stage 3: mirrors / drift ------------------------------------------

    def raw_at_main(self, path: str):
        """Fetch a file at main, skipping the request when the tree says it is absent."""
        if self.tree is not None and not self.tree["truncated"] and path not in self.tree["blobs"]:
            return 404, None
        return self.gh.raw(self.main_sha, path)

    def discover_mirrors(self) -> list[dict]:
        mirrors = scan_site_repo_mirrors(self.site_repo) if self.site_repo else []
        # Rendered "Source" buttons on /whitepaper/ and the listings pages.
        pages = list(self.pages.values())
        wp = self.fetch_page(urllib.parse.urljoin(self.base_url, "whitepaper/"))
        if wp and "links" in wp:
            pages.append(wp)
        for page in pages:
            for href, text in page.get("links", []):
                m = GH_BLOB_RE.match(href)
                if m and text.strip().lower() == "source" and re.fullmatch(r"[0-9a-f]{7,40}", m.group(1)):
                    mirrors.append({"page": page["path"], "url": page["path"], "source_path": urllib.parse.unquote(m.group(2)),
                                    "source_commit": m.group(1), "found_in": "rendered Source link"})
        entries = []
        if isinstance(self.index_json, dict) and isinstance(self.index_json.get("pages"), list):
            entries = [e for e in self.index_json["pages"] if isinstance(e, dict) and e.get("kind", "mirror") == "mirror"]
        for node in entries:
            commit, path = node.get("source_commit"), node.get("source_path")
            if isinstance(commit, str) and isinstance(path, str) and path and re.fullmatch(r"[0-9a-f]{7,40}", commit):
                url = urllib.parse.urlparse(str(node.get("url") or "")).path
                mirrors.append({"page": f"index.json {url}", "url": url, "source_path": path.lstrip("/"),
                                "source_commit": commit, "page_status": node.get("status") or "published",
                                "source_dirty": bool(node.get("source_dirty")),
                                "source_branch": node.get("source_branch") or None,
                                "found_in": "listings/index.json"})
        self.mirror_urls = {m["url"]: m["source_path"] for m in mirrors
                            if m.get("page_status", "published") == "published"}
        return mirrors

    def stage_drift(self) -> None:
        F = self.F
        if not self.main_sha:
            return
        mirrors = self.discover_mirrors()
        if not any(m["source_path"] == "docs/whitepaper.md" for m in mirrors):
            F.warn("drift", "no whitepaper mirror found (expected source_commit in content/whitepaper.md "
                            "front matter or a Source link on /whitepaper/)")
        resolved: dict[str, tuple[str, str] | None] = {}
        records: dict[tuple, dict] = {}
        for m in mirrors:
            short = m["source_commit"]
            if short not in resolved:
                status, commit = self.gh.api(f"repos/{UPSTREAM_REPO}/commits/{short}")
                resolved[short] = (commit["sha"], commit["commit"]["committer"]["date"]) if commit else None
            info = resolved[short]
            key = (m["source_path"], info[0] if info else short)
            if key in records:
                records[key]["pages"].append(f"{m['page']} ({m['found_in']})")
                continue
            in_review = m.get("page_status") == "in-review"
            rec = {"source_path": m["source_path"], "source_commit": short, "page_status": m.get("page_status"),
                   "source_dirty": m.get("source_dirty"), "source_branch": m.get("source_branch"),
                   "pages": [f"{m['page']} ({m['found_in']})"]}
            records[key] = rec
            label = f"{m['source_path']} pinned at {short}"
            if m.get("source_dirty") and not in_review:
                F.warn("drift", f"{label}: the site copy was taken from uncommitted text (source_dirty: true); "
                                f"no public commit contains it")
            if not info:
                rec["status"] = "pinned commit not found"
                F.hard("drift", f"{label}: commit not found in {UPSTREAM_REPO}")
                continue
            full, pinned_date = info
            rec.update({"source_commit_full": full, "pinned_date": pinned_date})
            st, cmp = self.gh.api(f"repos/{UPSTREAM_REPO}/compare/{full}...{self.main_sha}", {"per_page": 1})
            if cmp:
                rec.update({"relation": cmp.get("status"), "main_ahead_by": cmp.get("ahead_by"),
                            "main_behind_by": cmp.get("behind_by")})
            st_a, a = self.gh.raw(full, m["source_path"])
            st_b, b = self.raw_at_main(m["source_path"])
            rec["at_pin"] = a is not None
            rec["at_main"] = b is not None
            if b is None:
                if in_review:
                    rec["status"] = "placeholder; source not on main yet"
                    F.warn("drift", f"{m['source_path']}: site shows an in-review placeholder and the document is "
                                    f"not on public main yet")
                else:
                    rec["status"] = "file missing at main"
                    F.hard("drift", f"{label}: the site mirrors {m['source_path']}, which does not exist at public "
                                    f"main (HTTP {st_b})")
                continue
            if a is not None and a == b and not in_review:
                rec["status"] = "in sync"
                rec["file_changed_since_pin"] = False
                continue
            rec["file_changed_since_pin"] = True
            st_c, commits = self.gh.api(f"repos/{UPSTREAM_REPO}/commits",
                                        {"sha": self.main_sha, "path": m["source_path"], "since": pinned_date,
                                         "per_page": 100})
            changes = [c for c in (commits or []) if c.get("sha") != full]
            since = changes[-1]["commit"]["committer"]["date"] if changes else pinned_date
            age = (self.started - parse_iso(since)).total_seconds() / 86400
            rec.update({"changed_on_main_since": since, "drift_age_days": round(age, 1),
                        "upstream_changes": len(changes),
                        "first_change": changes[-1]["sha"][:9] if changes else None})
            what = "published the document" if in_review or a is None else "changed this file"
            if age > self.args.drift_days:
                rec["status"] = "STALE"
                F.hard("drift", f"{label}: main {what} {age:.1f} days ago (limit {self.args.drift_days:g}); "
                                f"re-run the site sync")
            else:
                rec["status"] = "drifting"
                F.warn("drift", f"{label}: main {what} {age:.1f} days ago; re-run the site sync within "
                                f"{self.args.drift_days:g} days")
        self.data["mirrors"] = list(records.values())

    # -- stage 4: source docs ----------------------------------------------

    def stage_docs(self) -> None:
        F = self.F
        current = self.state / "sources" / "current"
        current.mkdir(parents=True, exist_ok=True)
        archive = self.run_dir / "sources"
        archive.mkdir(parents=True, exist_ok=True)
        prev_docs = next((h.get("docs") for h in reversed(self.history)
                          if h.get("docs") and bool(h.get("mock")) == bool(self.args.mock)), {}) or {}
        if self.docs_repo:
            ident = git_identity(self.docs_repo)
            origin = f"local checkout {self.docs_repo} ({short_identity(ident)})"
        else:
            ident = None
            origin = f"GitHub {UPSTREAM_REPO}@{(self.main_sha or '?')[:9]}"
        self.data["docs_origin"] = origin
        for key, (rel, fname) in SOURCE_DOCS.items():
            text = None
            if self.docs_repo:
                p = self.docs_repo / rel
                if p.exists():
                    text = p.read_text(encoding="utf-8", errors="replace")
            elif self.main_sha:
                st, body = self.raw_at_main(rel)
                text = body.decode("utf-8", "replace") if body is not None else None
            rec = {"key": key, "path": rel, "origin": origin, "present": text is not None}
            if text is None:
                (F.hard if key in LISTING_DOC_KEYS else F.warn)("source-docs", f"{rel} missing ({origin})")
            else:
                (current / fname).write_text(text)
                (archive / fname).write_text(text)
                rec.update({"sha256": sha256_text(text), "words": len(text.split()), "local_path": str(current / fname)})
                if self.tree is not None and rel not in self.tree["blobs"]:
                    rec["on_public_main"] = False
                    if key in LISTING_DOC_KEYS:
                        F.warn("source-docs", f"{rel} is not on public main yet (read from {origin})")
                prev = (prev_docs.get(key) or {}).get("sha256")
                rec["changed_since_last_run"] = None if prev is None else prev != rec["sha256"]
            self.docs[key] = {**rec, "text": text}
        # README / docs index should point readers at the listing docs.
        for key in ("readme", "docs_index"):
            text = self.docs[key]["text"]
            if text is not None and "listings/coinbase" not in text:
                F.warn("source-docs", f"{SOURCE_DOCS[key][0]} does not link docs/listings/coinbase/ ({origin})")
        self.data["docs"] = {k: {kk: vv for kk, vv in v.items() if kk != "text"} for k, v in self.docs.items()}
        self.stage_doc_links()

    def stage_doc_links(self) -> None:
        F = self.F
        results = []
        for key in LISTING_DOC_KEYS:
            doc = self.docs.get(key) or {}
            text = doc.get("text")
            if not text:
                continue
            rel = doc["path"]
            for target in sorted(set(markdown_links(text))):
                target = target.strip()
                m = GH_BLOB_RE.match(target)
                if m and m.group(1) == "main":
                    path = urllib.parse.unquote(m.group(2)).rstrip("/")
                    kind = "github main link"
                elif re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I) or target.startswith("#") or target.startswith("//"):
                    continue
                else:
                    raw = urllib.parse.unquote(target.split("#", 1)[0].split("?", 1)[0])
                    if not raw:
                        continue
                    path = raw.lstrip("/") if raw.startswith("/") else posixpath.normpath(
                        posixpath.join(posixpath.dirname(rel), raw))
                    path = path.rstrip("/")
                    kind = "relative link"
                if self.docs_repo and kind == "relative link":
                    exists = (self.docs_repo / path).exists()
                    status = "exists (local)" if exists else "NOT FOUND"
                else:
                    status = path_status(path, self.tree, self.docs_repo)
                    exists = status != "NOT FOUND"
                results.append({"doc": rel, "target": target, "resolved": path, "kind": kind, "status": status})
                if not exists:
                    F.hard("doc-links", f"{rel}: link target {target!r} -> {path} does not exist")
                elif status == "local checkout only":
                    F.warn("doc-links", f"{rel}: {target!r} exists only in the local checkout, not at public main")
        self.data["checks"]["doc_links"] = {"checked": len(results),
                                            "broken": sum(1 for r in results if r["status"] == "NOT FOUND"),
                                            "items": results}

    # -- stage 5: links on the listings pages ------------------------------

    def collect_links(self) -> dict[str, dict]:
        F = self.F
        entries: dict[str, dict] = {}

        def add(url: str, written: str, where: str) -> None:
            url, frag = urllib.parse.urldefrag(url)
            e = entries.setdefault(url, {"url": url, "written": set(), "pages": set(), "fragments": set()})
            e["written"].add(written)
            e["pages"].add(where)
            if frag:
                e["fragments"].add(frag)

        for page in self.pages.values():
            for href, _text in page["links"]:
                if not href or re.match(r"^(mailto|tel|javascript|data):", href, re.I):
                    continue
                if href.startswith("#"):
                    frag = urllib.parse.unquote(href[1:])
                    if frag and frag not in page["ids"]:
                        F.warn("links", f"{page['path']}: in-page anchor #{frag} has no target id")
                    continue
                add(self.to_target(urllib.parse.urljoin(page["url"], href)), href, page["path"])
        if self.index_json is not None:
            for jpath, value in walk_json_strings(self.index_json):
                v = value.strip()
                if re.match(r"^https?://\S+$", v) or re.match(r"^/[^\s]*$", v) and len(v) > 1:
                    add(self.to_target(urllib.parse.urljoin(self.base_url, v)), v, f"index.json {jpath}")
        return entries

    def link_expectations(self) -> list[dict]:
        if getattr(self, "_expect", None) is None:
            self._expect = []
            path = self.args.link_expectations
            if path and path.exists():
                for rule in json.loads(path.read_text()).get("rules", []):
                    self._expect.append({**rule, "_re": re.compile(rule["url_regex"])})
        return self._expect

    def check_crates_via_api(self, url: str) -> int | None:
        m = re.match(r"^https?://crates\.io/crates/([A-Za-z0-9_-]+)(?:/([^/?#]+))?/?$", url)
        if not m:
            return None
        api = f"https://crates.io/api/v1/crates/{m.group(1)}" + (f"/{m.group(2)}" if m.group(2) else "")
        try:
            return http_fetch(api, timeout=self.args.link_timeout, max_bytes=65536)[0]
        except (urllib.error.URLError, OSError, http.client.HTTPException):
            return None

    def check_github_via_api(self, url: str) -> int | None:
        m = re.match(r"^https?://github\.com/([^/]+)/([^/]+)/(?:blob|tree)/(.+)$", url)
        if not m:
            return None
        owner, repo, rest = m.groups()
        parts = urllib.parse.unquote(rest).split("/")
        for k in range(1, min(4, len(parts)) + 1):
            ref, path = "/".join(parts[:k]), "/".join(parts[k:])
            st, _ = self.gh.api(f"repos/{owner}/{repo}/contents/{urllib.parse.quote(path)}", {"ref": ref})
            if st == 200:
                return 200
        return 404

    def check_one_link(self, entry: dict, gh_sem: threading.Semaphore) -> dict:
        url = entry["url"]
        internal = self.is_target_url(url)
        host = (urllib.parse.urlparse(url).hostname or "").lower()
        is_github = host in ("github.com", "www.github.com")
        status, final, error, body, ctype = None, url, None, b"", ""
        dns_failure = False
        sem = gh_sem if is_github else contextlib.nullcontext()
        with sem:
            for attempt in range(4):
                try:
                    method = "GET" if internal or entry["fragments"] else "HEAD"
                    status, final, body, hdr = http_fetch(url, method=method, timeout=self.args.link_timeout,
                                                          max_bytes=8_000_000)
                    if method == "HEAD" and status != 200 and status != 429 and status < 500:
                        status, final, body, hdr = http_fetch(url, timeout=self.args.link_timeout, max_bytes=262144)
                    ctype = hdr.get("content-type", "")
                    error = None
                    if status == 429 or status >= 500:
                        wait = hdr.get("retry-after", "")
                        time.sleep(min(float(wait) if wait.isdigit() else 2.0 * 2 ** attempt, 30.0))
                        continue
                    break
                except urllib.error.URLError as exc:
                    error = str(exc.reason)
                    if isinstance(exc.reason, socket.gaierror):
                        dns_failure = True
                        break
                    time.sleep(2.0 * (attempt + 1))
                except (TimeoutError, OSError, http.client.HTTPException) as exc:
                    error = f"{exc.__class__.__name__}: {exc}"
                    time.sleep(2.0 * (attempt + 1))
        result = "ok" if status == 200 else None
        via = "http"
        if result is None:
            if status is not None and 200 < status < 300:
                result = "non-200"
            elif status in (401, 403):
                result = "unverified"
                error = "access denied to an automated client (bot protection?)"
            elif dns_failure or (status is not None and 400 <= status < 500 and status != 429):
                result = "broken"
            else:
                result = "unverified"
            if is_github and result in ("broken", "unverified"):
                api_status = self.check_github_via_api(url)
                if api_status is not None:
                    via = "github api"
                    result = "ok" if api_status == 200 else "broken"
            elif host == "crates.io" and result in ("broken", "unverified"):
                api_status = self.check_crates_via_api(url)
                if api_status in (200, 404):
                    via = "crates.io api"
                    result = "ok" if api_status == 200 else "broken"
            for rule in self.link_expectations():
                if status in rule.get("accept_status", []) and rule["_re"].search(url):
                    result, via = "ok", f"expected HTTP {status}: {rule.get('reason', '')}"
                    break
        missing_frags = []
        if result == "ok" and entry["fragments"] and "html" in ctype and not is_github:
            ids = parse_html(body.decode("utf-8", "replace")).ids
            missing_frags = sorted(f for f in entry["fragments"] if urllib.parse.unquote(f) not in ids)
        return {"url": url, "written": sorted(entry["written"]), "pages": sorted(entry["pages"]), "status": status,
                "final_url": final, "result": result, "via": via, "error": error, "internal": internal,
                "missing_fragments": missing_frags}

    def stage_links(self) -> None:
        F = self.F
        if self.args.skip_links:
            F.warn("links", "link checks skipped (--skip-links)")
            return
        entries = self.collect_links()
        gh_sem = threading.Semaphore(3)
        with futures.ThreadPoolExecutor(max_workers=max(1, self.args.link_workers)) as pool:
            results = list(pool.map(lambda e: self.check_one_link(e, gh_sem), entries.values()))
        results.sort(key=lambda r: (r["result"] != "broken", r["result"] != "unverified", r["url"]))
        counts = Counter(r["result"] for r in results)
        for r in results:
            where = ", ".join(r["pages"][:3])
            if r["result"] == "broken":
                F.hard("links", f"broken link {r['url']} (HTTP {r['status'] or r['error']}) on {where}")
            elif r["result"] == "unverified":
                why = f"HTTP {r['status']}" if r["status"] else ""
                why = "; ".join(x for x in (why, r["error"]) if x)
                F.warn("links", f"could not verify {r['url']} ({why}) on {where}")
            elif r["result"] == "non-200":
                F.warn("links", f"{r['url']} answered HTTP {r['status']} (not 200) on {where}")
            if r["missing_fragments"]:
                F.warn("links", f"{r['url']}: anchor(s) {', '.join('#' + f for f in r['missing_fragments'])} not found")
        self.data["checks"]["links"] = {"checked": len(results), "counts": dict(counts), "items": results}

    # -- stage 6: chain facts on the pages ---------------------------------

    def stage_chain_claims(self) -> None:
        F = self.F
        facts = self.data.get("chain_facts")
        if not facts or not self.pages:
            return
        claims = []
        for page in self.pages.values():
            claims += extract_chain_claims(page["path"], page["text"])
        if self.index_json is not None:
            for jpath, value in walk_json_strings(self.index_json):
                if jpath != "$.project.network":
                    claims += extract_chain_claims(f"index.json {jpath}", value)
            proj = self.index_json.get("project") if isinstance(self.index_json, dict) else None
            if isinstance(proj, dict):
                if proj.get("network") is not None:
                    claims.append({"kind": "network", "value": str(proj["network"]), "page": "index.json $.project.network",
                                   "sentence": f"project.network = {proj['network']}"})
                if isinstance(proj.get("validators"), int):
                    claims.append({"kind": "validators", "value": proj["validators"], "match": str(proj["validators"]),
                                   "page": "index.json $.project.validators",
                                   "sentence": f"project.validators = {proj['validators']}"})
        unique, seen = [], set()
        for c in claims:
            k = (c["kind"], str(c["value"]).lower(), c["sentence"][:200])
            if k not in seen:
                seen.add(k)
                unique.append(c)
        claims = unique
        judge_chain_claims(claims, facts)
        for c in claims:
            if c["verdict"] == "MISMATCH":
                expected = facts["network"] if c["kind"] == "network" else facts["validators"]
                F.warn("chain-facts", f"{c['page']}: says {c.get('match', c['value'])!r}, chain-state-current.md "
                                      f"at main says {expected!r}: “{c['sentence'][:200]}”", escalate=True)
        if not any(c["kind"] == "network" for c in claims):
            F.info("chain-facts", f"the /listings/ pages never name the network ({facts.get('network')})")
        if not any(c["kind"] == "validators" and not c["verdict"].startswith("other") for c in claims):
            F.info("chain-facts", "the /listings/ pages state no validator count for the L1 devnet")
        self.data["chain_claims"] = claims

    # -- stage 7: TIH ------------------------------------------------------

    def tih(self, name: str, argv: list[str], timeout: float = 7200) -> tuple[int, str]:
        env = dict(os.environ, TIH_USAGE_DIR=str(self.usage_dir), PYTHONDONTWRITEBYTECODE="1")
        cmd = [sys.executable, "-m", "text_improvement_harness", *argv]
        logs = self.run_dir / "logs"
        logs.mkdir(parents=True, exist_ok=True)
        try:
            res = subprocess.run(cmd, cwd=self.tih_dir, env=env, capture_output=True, text=True, timeout=timeout)
            rc, out, err = res.returncode, res.stdout, res.stderr
        except subprocess.TimeoutExpired as exc:
            rc, out, err = 124, exc.stdout or "", f"timeout after {timeout}s"
            out = out.decode() if isinstance(out, bytes) else out
        shown = [a if len(a) < 200 else a[:80] + "…" for a in argv]
        (logs / f"tih-{name}.log").write_text(f"$ tih {' '.join(shown)}\nexit={rc}\n\n--- stdout\n{out}\n--- stderr\n{err}\n")
        return rc, out

    def common(self) -> list[str]:
        return ["--db", str(self.db), "--project", self.args.project]

    def stage_tih_init(self) -> None:
        rc, _ = self.tih("init", ["init", *self.common(), "--target-website", "postfiat.org",
                                  "--reference-repository", UPSTREAM_REPO])
        if rc != 0:
            raise RuntimeError(f"tih init failed (exit {rc}); see logs/tih-init.log")

    def stage_tih_audit(self) -> None:
        F = self.F
        if not self.build_dir:
            F.warn("tih-audit", "skipped: needs --site-repo, --build-dir or --serve-local")
            return
        if not (self.build_dir / "listings" / "index.html").exists():
            F.hard("tih-audit", f"/listings/ is not in the site build ({self.build_dir})")
        rc, out = self.tih("audit", ["audit", *self.common(), "--build-dir", str(self.build_dir), "--limit", "100000"],
                           timeout=900)
        try:
            con = sqlite3.connect(self.db)
            con.row_factory = sqlite3.Row
            row = con.execute(
                "SELECT a.findings, a.counts, a.created_at FROM site_audits a JOIN projects p ON p.id = a.project_id "
                "WHERE p.name = ? ORDER BY a.id DESC LIMIT 1", (self.args.project,)).fetchone()
            con.close()
        except sqlite3.Error as exc:
            F.warn("tih-audit", f"audit ran (exit {rc}) but its result could not be read: {exc}")
            return
        if row is None:
            F.warn("tih-audit", f"audit produced no record (exit {rc}); see logs/tih-audit.log")
            return
        findings = json.loads(row["findings"])
        listing = [f for f in findings if str(f.get("url", "")).startswith(LISTINGS_PATH)]
        site_counts = Counter(f["severity"] for f in findings)
        for f in listing:
            msg = f"{f['kind']} on {f['url']}" + (f": {f['detail']}" if f.get("detail") else "")
            if f["severity"] == "error":
                F.hard("tih-audit", msg)
            elif f["severity"] == "warn":
                F.warn("tih-audit", msg)
        self.data["tih_audit"] = {
            "exit": rc, "created_at": row["created_at"], "build_dir": str(self.build_dir),
            "site_counts": dict(site_counts), "site_kinds": json.loads(row["counts"]),
            "listings_findings": listing,
        }

    def snapshot_landing(self) -> pathlib.Path | None:
        F = self.F
        add = ["add-page", *self.common(), "--url", LISTINGS_PATH, "--target-website", "postfiat.org"]
        if self.site_repo:
            add += ["--repo", str(self.site_repo)]
        self.tih("add-page", add)
        snap = self.db.parent / "site-snapshots" / self.args.project / "listings.md"
        snap.unlink(missing_ok=True)
        argv = ["snapshot", *self.common(), "--url", LISTINGS_PATH]
        if self.build_dir and self.is_local_target():
            argv += ["--build-dir", str(self.build_dir)]
            if self.site_repo:
                argv += ["--repo", str(self.site_repo)]
        else:
            argv += ["--production", "--base-url", self.base_url.rstrip("/")]
        rc, out = self.tih("snapshot", argv, timeout=300)
        if rc != 0 or not snap.exists():
            F.warn("tih-score", f"could not snapshot {LISTINGS_PATH} for scoring (exit {rc}); see logs/tih-snapshot.log")
            return None
        shutil.copy(snap, self.run_dir / "sources" / "listings-landing-snapshot.md")
        return snap

    def lane_of(self, model: str) -> str:
        return self.tih_game.mode_label(model)

    def previous_score(self, target: str, gate: str) -> dict | None:
        for h in reversed(self.history):
            s = (h.get("scores") or {}).get(target)
            if s and s.get("gate") == gate and bool(h.get("mock")) == bool(self.args.mock) and s.get("lanes"):
                return {**s, "run_id": h.get("run_id")}
        return None

    def score_one(self, target: str, path: pathlib.Path, gate: str, runs: int, prompt: str | None) -> dict:
        run_group = f"plm-{self.run_id}-{target}"
        argv = ["score", str(path), *self.common(), "--gate", gate, "--runs", str(runs), "--force",
                "--temperature", "0", "--max-tokens", "8000", "--run-group", run_group,
                "--concurrency", str(self.args.concurrency)]
        if gate == "cheap":
            argv += ["--mode", self.args.cheap_lane]
        if prompt:
            argv += ["--scoring-prompt", prompt]
        if self.args.mock:
            argv.append("--mock")
        rc, out = self.tih(f"score-{target}", argv)
        con = sqlite3.connect(self.db)
        con.row_factory = sqlite3.Row
        rows = con.execute("SELECT provider, model, score, raw_response, document_sha256 FROM score_runs "
                           "WHERE run_group = ? AND score IS NOT NULL", (run_group,)).fetchall()
        con.close()
        lanes: dict[str, dict] = {}
        for r in rows:
            lane = self.lane_of(r["model"])
            d = lanes.setdefault(lane, {"provider": r["provider"], "model": r["model"], "scores": [], "notes": None,
                                        "_low": None})
            d["scores"].append(float(r["score"]))
            if d["_low"] is None or float(r["score"]) < d["_low"]:
                d["_low"] = float(r["score"])
                with contextlib.suppress(Exception):
                    j = parse_json_lenient(r["raw_response"])
                    d["notes"] = {"worst_thing": j.get("worst_thing"), "one_best_next_edit": j.get("one_best_next_edit")}
        for d in lanes.values():
            s = d.pop("scores")
            d.pop("_low")
            d.update({"runs": len(s), "avg": round(statistics.mean(s), 2), "min": min(s), "max": max(s)})
        cheap_lane = self.tih_game.LEGACY_LANE_ALIASES.get(self.args.cheap_lane, self.args.cheap_lane)
        expected = list(FULL_LANES) if gate == "full" else [cheap_lane]
        incomplete = [l for l in expected if lanes.get(l, {}).get("runs", 0) < runs]
        avg = round(statistics.mean(lanes[l]["avg"] for l in lanes), 2) if lanes else None
        return {"gate": gate, "runs_per_lane": runs, "run_group": run_group, "exit": rc, "lanes": lanes,
                "avg": avg, "incomplete_lanes": incomplete, "document_sha256": rows[0]["document_sha256"] if rows else None,
                "path": str(path), "scoring_prompt": "web page prompt (TIH site lane)" if prompt else "TIH default"}

    def stage_tih_scores(self) -> None:
        F = self.F
        a = self.args
        gate = "full" if self.mode == "full" else "cheap"
        runs = a.runs or (5 if gate == "full" else 1)
        wanted = [t.strip() for t in a.score_docs.split(",") if t.strip()]
        bad = [t for t in wanted if t not in SCORE_TARGETS]
        if bad:
            raise SystemExit(f"--score-docs: unknown target(s) {bad}; use {SCORE_TARGETS}")
        scores: dict[str, dict] = {}
        tag = " (mock scores)" if a.mock else ""
        for target in wanted:
            if target == "plan":
                doc = self.docs.get("integration_plan") or {}
                if not doc.get("text"):
                    (F.hard if gate == "full" else F.warn)("tih-score", "integration plan unavailable; not scored")
                    continue
                path, prompt, label = pathlib.Path(doc["local_path"]), None, SOURCE_DOCS["integration_plan"][0]
            else:
                path = self.snapshot_landing()
                if path is None:
                    continue
                prompt, label = self.tih_site.web_scoring_prompt("postfiat.org", LISTINGS_PATH), LISTINGS_PATH
            res = self.score_one(target, path, gate, runs, prompt)
            res["label"] = label
            prev = self.previous_score(target, gate)
            res["previous"] = {"run_id": prev["run_id"], "avg": prev.get("avg"),
                               "lanes": {k: v.get("avg") for k, v in prev["lanes"].items()}} if prev else None
            for lane, d in res["lanes"].items():
                p = (prev or {}).get("lanes", {}).get(lane, {}).get("avg")
                d["prev"] = p
                d["delta"] = round(d["avg"] - p, 2) if p is not None else None
                if d["delta"] is not None and d["delta"] < -a.lane_drop:
                    F.warn("tih-score", f"{label}: {lane} lane fell {abs(d['delta']):.1f} points vs previous "
                                        f"{gate} run ({p:.1f} -> {d['avg']:.1f}){tag}")
            if res["incomplete_lanes"]:
                msg = f"{label}: {gate} gate incomplete, missing runs for {', '.join(res['incomplete_lanes'])} " \
                      f"(see logs/tih-score-{target}.log){tag}"
                (F.hard if gate == "full" and target == "plan" else F.warn)("tih-score", msg)
            if target == "plan" and gate == "full" and res["avg"] is not None and not res["incomplete_lanes"]:
                if res["avg"] < a.plan_threshold:
                    F.hard("tih-score", f"integration plan full-gate average {res['avg']:.2f} is below "
                                        f"{a.plan_threshold:g}{tag}")
                else:
                    F.info("tih-score", f"integration plan full-gate average {res['avg']:.2f} "
                                        f"(threshold {a.plan_threshold:g}){tag}")
            scores[target] = res
        # Context for cheap runs: the most recent full-gate plan score.
        if gate == "cheap":
            last_full = self.previous_score("plan", "full")
            if last_full:
                self.data["last_full_plan"] = {"run_id": last_full["run_id"], "avg": last_full.get("avg")}
        self.data["scores"] = scores

    # -- stage 8: adversarial ----------------------------------------------

    def build_repo_index(self, texts: list[str]) -> str:
        """Every file the inputs link to (uncapped), then a capped selection of other paths."""
        if not self.tree:
            return "(repository tree unavailable)"
        blobs, dirs = self.tree["blobs"], self.tree["dirs"]
        on_main: set[str] = set()
        local_only: set[str] = set()
        for item in ((self.data.get("checks") or {}).get("doc_links") or {}).get("items", []):
            path = item["resolved"]
            if path in blobs or path in dirs:
                on_main.add(path)
            elif item["status"] != "NOT FOUND":
                local_only.add(path)
        for page in self.pages.values():
            for href, _ in page["links"]:
                m = GH_BLOB_RE.match(href)
                if m:
                    path = urllib.parse.unquote(m.group(2)).rstrip("/")
                    (on_main if path in blobs or path in dirs else local_only).add(path)
        for text in texts:
            for target in re.findall(r"(?:docs|deployments|benchmarks|crates|scripts|tools|python|programs)/[A-Za-z0-9_./-]+",
                                     text):
                t = target.rstrip(".,);:")
                if t in blobs:
                    on_main.add(t)
        top = sorted(p for p in blobs if "/" not in p)
        docs_md = [p for p in sorted(blobs) if p.startswith("docs/") and p.endswith(".md") and p.count("/") <= 2
                   and p not in on_main]
        dir_counts = Counter("/".join(p.split("/")[:2]) for p in blobs if "/" in p)
        lines = ["# A. every repository path the inputs link to that exists at public main (complete)"]
        lines += sorted(on_main) or ["(none)"]
        lines += ["", "# B. paths the inputs link to that exist only in the unpublished docs checkout, "
                      "not yet at public main (complete)"]
        lines += sorted(local_only - on_main) or ["(none)"]
        lines += ["", "# C. top-level files"] + top
        lines += ["", f"# D. other docs/ Markdown files (selection of {len(docs_md)}; absence here proves nothing)"]
        lines += docs_md[: self.args.repo_index_limit]
        lines += ["", "# E. directories (file counts)"]
        lines += [f"{d}/ ({n})" for d, n in sorted(dir_counts.items()) if n >= 3][:150]
        return "\n".join(lines)

    def adversarial_inputs(self) -> list[tuple[str, str]]:
        blocks = []
        included = {SOURCE_DOCS[k][0] for k in LISTING_DOC_KEYS if (self.docs.get(k) or {}).get("text")}
        for page in sorted(self.pages.values(), key=lambda p: p["path"]):
            if self.mirror_urls.get(page["path"]) in included:
                continue  # a mirror of a source document that is included below
            blocks.append((f"site:{page['path']}", page["text"]))
        if not self.pages:
            blocks.append(("site:/listings/", "(MISSING: the /listings/ page did not load during this run)"))
        for key in LISTING_DOC_KEYS:
            doc = self.docs.get(key) or {}
            text = doc.get("text") or f"(MISSING: {SOURCE_DOCS[key][0]} was not available during this run)"
            blocks.append((f"repo:{SOURCE_DOCS[key][0]}", text))
        return blocks

    def load_prompt(self) -> tuple[str, str]:
        text = (HERE / "adversarial_prompt.md").read_text()
        m = re.search(r"<!-- SYSTEM -->\s*(.*?)\s*<!-- USER -->\s*(.*)$", text, re.S)
        if not m:
            raise RuntimeError("adversarial_prompt.md is missing the <!-- SYSTEM --> / <!-- USER --> markers")
        return m.group(1).strip(), m.group(2).strip()

    def openrouter_chat(self, key: str, model: str, system: str, user: str, effort: str) -> tuple[str, dict]:
        def post(response_format: dict) -> dict:
            payload = {
                "model": model,
                "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
                "max_tokens": self.args.adversarial_max_tokens,
                "reasoning": {"effort": effort},
                "response_format": response_format,
                "usage": {"include": True},
            }
            req = urllib.request.Request(OPENROUTER_URL, data=json.dumps(payload).encode("utf-8"), method="POST",
                                         headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                                                  "HTTP-Referer": "https://postfiat.org",
                                                  "X-Title": "Post Fiat listings monitor"})
            try:
                with urllib.request.urlopen(req, timeout=self.args.adversarial_timeout) as resp:
                    return json.loads(resp.read().decode("utf-8"))
            except urllib.error.HTTPError as exc:
                msg = ""
                with contextlib.suppress(Exception):
                    msg = str(json.loads(exc.read(65536)).get("error", {}).get("message", ""))[:200]
                raise AdversarialHTTPError(exc.code, msg) from None

        schema_format = {"type": "json_schema",
                         "json_schema": {"name": "listings_red_team", "strict": True, "schema": ADVERSARIAL_SCHEMA}}
        started = time.time()
        try:
            raw = post(schema_format)
            fmt = "json_schema"
        except AdversarialHTTPError as exc:
            if exc.code != 400:
                raise
            raw = post({"type": "json_object"})
            fmt = "json_object (schema rejected)"
        if raw.get("error"):
            raise RuntimeError(f"provider error: {str(raw['error'].get('message', raw['error']))[:200]}")
        choice = raw["choices"][0]
        usage = raw.get("usage") or {}
        meta = {"id": raw.get("id"), "model": raw.get("model", model), "requested_model": model,
                "provider": raw.get("provider"), "finish_reason": choice.get("finish_reason"),
                "response_format": fmt, "elapsed_s": round(time.time() - started, 1), "usage": usage}
        content = (choice.get("message") or {}).get("content")
        if choice.get("finish_reason") == "length":
            raise RuntimeError(f"output token limit reached ({self.args.adversarial_max_tokens}); raise "
                               "--adversarial-max-tokens")
        if not isinstance(content, str) or not content.strip():
            raise RuntimeError(f"empty response (finish_reason={choice.get('finish_reason')})")
        return content, meta

    def stage_adversarial(self, pricing: Pricing) -> None:
        F = self.F
        a = self.args
        rec: dict = {"mode": a.adversarial, "model": a.adversarial_model, "fallback": a.adversarial_fallback}
        self.data["adversarial"] = rec
        if a.adversarial == "skip":
            rec["status"] = "skipped"
            return
        system, user_t = self.load_prompt()
        blocks = self.adversarial_inputs()
        input_docs = "\n\n".join(f"=== INPUT {label} ({len(text)} chars) ===\n{text}\n=== END INPUT {label} ==="
                                 for label, text in blocks)
        facts = self.data.get("chain_facts") or {}
        facts_line = (f"network `{facts.get('network')}`, {facts.get('validators')} validators "
                      f"({facts.get('validators_basis')}), file updated {facts.get('updated')}") if facts else \
            "(chain-state-current.md could not be read this run)"
        excerpt = (self.chain_text or "(unavailable)")[: a.chain_excerpt_chars]
        repo_index = self.build_repo_index([t for _, t in blocks])
        user = (user_t.replace("{{TODAY}}", self.started.strftime("%Y-%m-%d"))
                .replace("{{MAIN_SHA}}", self.main_sha or "unknown")
                .replace("{{CHAIN_FACTS}}", facts_line)
                .replace("{{CHAIN_STATE_EXCERPT}}", excerpt)
                .replace("{{REPO_INDEX}}", repo_index)
                .replace("{{INPUT_DOCUMENTS}}", input_docs))
        input_hash = sha256_text("\n".join([a.adversarial_model, system, input_docs, excerpt]))
        prompt_path = self.run_dir / "adversarial-prompt.md"
        prompt_path.write_text(f"<!-- SYSTEM -->\n{system}\n\n<!-- USER -->\n{user}\n")
        est_in = (len(system) + len(user)) // 4
        rec.update({"input_sha256": input_hash, "prompt_path": str(prompt_path), "prompt_chars": len(system) + len(user),
                    "est_input_tokens": est_in, "inputs": [{"label": l, "chars": len(t)} for l, t in blocks]})
        rate = pricing.rate("openrouter", a.adversarial_model)
        last = None
        with contextlib.suppress(Exception):
            last = json.loads((self.state / "adversarial-cache.json").read_text())
        last_call = (last or {}).get("call") or {}
        if last_call.get("cost_usd") and last.get("prompt_chars") and last_call.get("requested_model") == a.adversarial_model:
            rec["est_cost_usd"] = round(last_call["cost_usd"] * rec["prompt_chars"] / last["prompt_chars"], 3)
            rec["est_basis"] = f"last real call ({last['created_at']}) scaled by prompt size"
        elif rate:
            rec["est_cost_usd"] = round(est_in * rate["prompt"] + a.est_adversarial_output_tokens * rate["completion"], 3)
            rec["est_basis"] = "list price; pro models can bill several times the prompt (multi-pass)"
        corpus_norm = normalize_for_match("\n".join(t for _, t in blocks) + "\n" + (self.chain_text or ""))
        missing_inputs = [l for l, t in blocks if t.startswith("(MISSING")]
        if missing_inputs:
            F.warn("adversarial", "red-team inputs missing: " + ", ".join(missing_inputs))

        if a.adversarial == "dry-run":
            rec["status"] = "dry-run (no model call)"
            result = empty_adversarial_result()
            rec["shape_problems"] = []
            rec["verification"] = annotate_adversarial(result, corpus_norm, self.tree, self.docs_repo)
            rec["result"] = result
            F.info("adversarial", f"dry run: prompt saved ({rec['prompt_chars']} chars, ~{est_in} input tokens)")
            return

        cache_path = self.state / "adversarial-cache.json"
        if self.mode == "cheap" and a.adversarial_reuse_days > 0 and cache_path.exists():
            with contextlib.suppress(Exception):
                cache = json.loads(cache_path.read_text())
                age = (self.started - parse_iso(cache["created_at"])).total_seconds() / 86400
                if cache.get("input_sha256") == input_hash and age <= a.adversarial_reuse_days:
                    result = json.loads(pathlib.Path(cache["result_path"]).read_text())
                    rec.update({"status": f"reused (inputs unchanged since {cache['created_at']})",
                                "reused_from": cache["result_path"], "call": cache.get("call")})
                    rec["shape_problems"] = shape_problems(result)
                    rec["verification"] = annotate_adversarial(result, corpus_norm, self.tree, self.docs_repo)
                    rec["result"] = result
                    return

        key, key_source = self.tih_keys.resolve_key_source("OPENROUTER_API_KEY", None)
        rec["key_source"] = key_source
        errors = []
        content = meta = None
        for model, effort in ((a.adversarial_model, a.adversarial_effort), (a.adversarial_fallback, "medium")):
            if not model:
                continue
            try:
                content, meta = self.openrouter_chat(key, model, system, user, effort)
                break
            except Exception as exc:  # network, HTTP, provider errors -> try fallback
                errors.append(f"{model}: {exc}")
        del key
        rec["errors"] = errors
        if content is None:
            rec["status"] = "failed"
            F.warn("adversarial", "red-team call failed: " + " | ".join(errors))
            return
        usage = meta.get("usage") or {}
        tin, tout = usage_tokens(usage)
        cost = usage.get("cost")
        if not isinstance(cost, (int, float)):
            cost = pricing.cost("openrouter", meta["requested_model"], tin, tout)
        meta["cost_usd"] = cost
        rec["call"] = meta
        (self.run_dir / "adversarial-response.txt").write_text(content)
        try:
            result = parse_json_lenient(content)
        except json.JSONDecodeError as exc:
            rec["status"] = "unparseable response"
            F.warn("adversarial", f"red-team response is not valid JSON ({exc}); raw saved to adversarial-response.txt")
            return
        rec["status"] = "ok" if meta["requested_model"] == a.adversarial_model else "ok (fallback model)"
        rec["shape_problems"] = shape_problems(result)
        if rec["shape_problems"]:
            F.warn("adversarial", "red-team response deviates from the requested shape: "
                   + "; ".join(rec["shape_problems"]))
        if isinstance(result, dict):
            rec["verification"] = annotate_adversarial(result, corpus_norm, self.tree, self.docs_repo)
        rec["result"] = result
        result_path = self.run_dir / "adversarial-result.json"
        result_path.write_text(json.dumps(result, indent=2))
        cache_path.write_text(json.dumps({"input_sha256": input_hash, "created_at": iso(self.started),
                                          "prompt_chars": rec["prompt_chars"], "result_path": str(result_path),
                                          "call": meta}, indent=2))
        if isinstance(result, dict):
            highs = sum(1 for k in ("unsupported_or_contradicted_claims", "misleading_framing_or_omissions",
                                    "broken_or_circular_references")
                        for i in result.get(k) or [] if isinstance(i, dict) and i.get("severity") == "high"
                        and i.get("kind") != "no_issue")
            F.info("adversarial", f"red team: readiness={result.get('listing_readiness')}, {highs} high-severity finding(s)")

    # -- costs, history, report ----------------------------------------------

    def costs(self, pricing: Pricing) -> dict:
        rows = summarize_receipts(self.usage_dir, pricing)
        adv = (self.data.get("adversarial") or {}).get("call")
        adv_status = (self.data.get("adversarial") or {}).get("status", "")
        if adv and not adv_status.startswith("reused"):
            tin, tout = usage_tokens(adv.get("usage") or {})
            rows.append({"provider": "openrouter", "model": adv.get("model"), "calls": 1, "completed": 1,
                         "tokens_in": tin, "tokens_out": tout, "cost_usd": adv.get("cost_usd") or 0.0,
                         "cost_basis": "provider" if isinstance((adv.get("usage") or {}).get("cost"), (int, float))
                         else "list price", "step": "adversarial"})
        for r in rows:
            r.setdefault("step", "tih scoring")
        total = round(sum(r["cost_usd"] or 0 for r in rows), 4)
        return {"rows": rows, "total_usd": total, "pricing_source": pricing.source}

    def write_outputs(self, cost: dict) -> tuple[pathlib.Path, pathlib.Path, int]:
        hard, warn = self.F.of("hard"), self.F.of("warn")
        exit_code = 1 if hard else 0
        finished = utcnow()
        meta = {
            "run_id": self.run_id, "mode": self.mode, "requested_mode": self.args.mode,
            "started": iso(self.started), "finished": iso(finished),
            "duration_s": round((finished - self.started).total_seconds(), 1),
            "status": "FAIL" if hard else "PASS", "exit_code": exit_code,
            "target": {"base_url": self.base_url, "kind": self.target_kind,
                       "site_repo": git_identity(self.site_repo) if self.site_repo else None,
                       "build_dir": str(self.build_dir) if self.build_dir else None},
            "mock_scores": bool(self.args.mock), "adversarial_mode": self.args.adversarial,
            "thresholds": {"plan_full_gate_min": self.args.plan_threshold, "lane_drop": self.args.lane_drop,
                           "drift_days": self.args.drift_days, "strict": self.args.strict},
            "db": str(self.db), "project": self.args.project, "run_dir": str(self.run_dir),
            "counts": {lvl: len(self.F.of(lvl)) for lvl in ("hard", "warn", "info")},
            "github": {"auth": self.gh.auth_mode, "api_calls": self.gh.api_calls, "raw_fetches": self.gh.raw_calls},
        }
        report = {"meta": meta, "findings": self.F.items, **self.data, "cost": cost}
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        stem = f"{self.started:%Y-%m-%d}-{self.mode}"
        json_path = self.reports_dir / f"{stem}.json"
        md_path = self.reports_dir / f"{stem}.md"
        json_path.write_text(json.dumps(report, indent=2, default=lambda o: sorted(o) if isinstance(o, set) else str(o)))
        md_path.write_text(render_markdown(report))
        (self.run_dir / "report.md").write_text(md_path.read_text())
        for name, target in (("latest.md", md_path.name), ("latest.json", json_path.name)):
            link = self.reports_dir / name
            tmp = self.reports_dir / f".{name}.tmp"
            tmp.unlink(missing_ok=True)
            tmp.symlink_to(target)
            os.replace(tmp, link)
        hist = {"run_id": self.run_id, "date": iso(self.started), "mode": self.mode, "mock": bool(self.args.mock),
                "adversarial": self.args.adversarial, "status": meta["status"], "counts": meta["counts"],
                "report": str(md_path), "cost_usd": cost["total_usd"],
                "docs": {k: {"sha256": v.get("sha256")} for k, v in (self.data.get("docs") or {}).items()},
                "scores": {k: {"gate": v["gate"], "avg": v["avg"],
                               "lanes": {l: {"avg": d["avg"], "runs": d["runs"]} for l, d in v["lanes"].items()},
                               "document_sha256": v["document_sha256"], "run_group": v["run_group"]}
                           for k, v in (self.data.get("scores") or {}).items()}}
        with (self.state / "history.jsonl").open("a") as fh:
            fh.write(json.dumps(hist) + "\n")
        return md_path, json_path, exit_code

    def run(self) -> int:
        self.state.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.run_dir.mkdir(parents=True, exist_ok=True)
        lock_fh = (self.state / "monitor.lock").open("w")
        try:
            fcntl.flock(lock_fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print("another monitor run holds the lock; exiting", file=sys.stderr)
            return 3
        self.import_tih()
        pricing = Pricing(self.state / "pricing-cache.json")
        stages = [
            ("upstream", self.stage_upstream),
            ("chain-state", self.stage_chain_state),
            ("site", self.stage_site),
            ("drift", self.stage_drift),
            ("docs", self.stage_docs),
            ("links", self.stage_links),
            ("chain-claims", self.stage_chain_claims),
            ("tih-init", self.stage_tih_init),
            ("tih-audit", self.stage_tih_audit),
            ("tih-scores", self.stage_tih_scores),
            ("adversarial", lambda: self.stage_adversarial(pricing)),
        ]
        timings = {}
        with self.target():
            self.data["target_ready"] = {"base_url": self.base_url, "build_dir": str(self.build_dir) if self.build_dir else None}
            for name, fn in stages:
                t0 = time.time()
                print(f"[{iso(utcnow())}] {name} …", flush=True)
                try:
                    fn()
                except SystemExit:
                    raise
                except Exception as exc:
                    self.F.hard("monitor", f"stage {name} crashed: {exc.__class__.__name__}: {exc}")
                    (self.run_dir / "logs").mkdir(parents=True, exist_ok=True)
                    (self.run_dir / "logs" / f"crash-{name}.log").write_text(traceback.format_exc())
                timings[name] = round(time.time() - t0, 1)
        self.data["stage_seconds"] = timings
        cost = self.costs(pricing)
        md_path, json_path, code = self.write_outputs(cost)
        hard, warn = self.F.of("hard"), self.F.of("warn")
        print(f"status={'FAIL' if hard else 'PASS'} hard={len(hard)} warn={len(warn)} cost=${cost['total_usd']:.4f}")
        for f in hard:
            print(f"  HARD {f['check']}: {f['message']}")
        print(f"report={md_path}\njson={json_path}")
        return code


class AdversarialHTTPError(RuntimeError):
    def __init__(self, code: int, message: str):
        super().__init__(f"OpenRouter HTTP {code}" + (f": {message}" if message else ""))
        self.code = code


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------


def render_markdown(r: dict) -> str:
    m = r["meta"]
    L: list[str] = []
    w = L.append
    banner = []
    if m["mock_scores"]:
        banner.append("TIH scores are MOCK values (no model calls)")
    if m["adversarial_mode"] != "real":
        banner.append(f"adversarial step: {m['adversarial_mode']}")
    w(f"# Post Fiat listings monitor: {m['started'][:10]} ({m['mode']})")
    w("")
    w(f"**Status: {m['status']}** (exit {m['exit_code']}). {m['counts']['hard']} hard failure(s), "
      f"{m['counts']['warn']} warning(s), {m['counts']['info']} note(s).")
    if banner:
        w("")
        w("> TEST RUN: " + "; ".join(banner) + ".")
    w("")
    t = m["target"]
    site = short_identity(t.get("site_repo")) if t.get("site_repo") else "n/a"
    up = r.get("upstream") or {}
    w("| | |")
    w("| --- | --- |")
    w(f"| Run | `{m['run_id']}`, {m['started']} to {m['finished']} ({m['duration_s']} s) |")
    w(f"| Target | {t['base_url']} ({t['kind']}) |")
    w(f"| Site checkout | {md_cell(t['site_repo']['path'] if t.get('site_repo') else 'n/a')} @ {md_cell(site)} |")
    w(f"| Upstream | `{UPSTREAM_REPO}` main @ `{(up.get('main_sha') or '?')[:12]}` "
      f"({up.get('main_commit_date') or 'date unknown'}) |")
    w(f"| Listing docs read from | {md_cell(r.get('docs_origin', 'n/a'), None)} |")
    sc_cost = r.get("cost") or {}
    w(f"| Model spend | ${sc_cost.get('total_usd', 0):.4f} |")
    w(f"| TIH DB / project | `{m['db']}` / `{m['project']}` |")
    w("")

    def findings_block(level: str, title: str) -> None:
        items = [f for f in r["findings"] if f["level"] == level]
        w(f"## {title} ({len(items)})")
        w("")
        if not items:
            w("None.")
        for f in items:
            w(f"- **{f['check']}**: {f['message']}")
        w("")

    findings_block("hard", "Hard failures")
    findings_block("warn", "Warnings")

    # 1. freshness
    w("## 1. Freshness and consistency (no model spend)")
    w("")
    w("### Mirrored pages vs public main")
    w("")
    mirrors = r.get("mirrors") or []
    if mirrors:
        w("| Source file | Pinned | Main ahead by | File changed | Drift age (days) | Status | Site pages |")
        w("| --- | --- | --- | --- | --- | --- | --- |")
        for x in mirrors:
            changed = {True: "yes", False: "no"}.get(x.get("file_changed_since_pin"), "?")
            rel, ahead, behind = x.get("relation"), x.get("main_ahead_by", "?"), x.get("main_behind_by")
            if rel == "identical":
                ahead = "0 (same commit)"
            elif rel == "behind":
                ahead = f"0 (pin has {behind} unmerged commit(s))"
            elif rel == "diverged":
                ahead = f"{ahead} (pin has {behind} unmerged commit(s))"
            w(f"| `{x['source_path']}` | `{x['source_commit'][:9]}` ({(x.get('pinned_date') or '')[:10]}) | "
              f"{ahead} | {changed} | {x.get('drift_age_days', '–')} | {x.get('status', '?')} | "
              f"{md_cell('; '.join(x['pages']), 160)} |")
    else:
        w("No mirrored pages found.")
    w("")
    cf = r.get("chain_facts")
    w("### Chain facts vs `docs/status/chain-state-current.md` at main")
    w("")
    if cf:
        w(f"Current: network `{cf.get('network')}`, **{cf.get('validators')} validators** "
          f"({cf.get('validators_basis')}); file updated {cf.get('updated')} "
          f"({cf.get('updated_age_days', '?')} days ago).")
        w("")
        claims = r.get("chain_claims") or []
        if claims:
            w("| Page | Says | Verdict | Sentence |")
            w("| --- | --- | --- | --- |")
            for c in claims:
                w(f"| {md_cell(c['page'], 60)} | {md_cell(c.get('match', c['value']), 40)} | {c['verdict']} | "
                  f"{md_cell(c['sentence'], 200)} |")
        else:
            w("No network-name or validator-count statements found on the /listings/ pages.")
    else:
        w("Not available this run.")
    w("")
    lk = (r.get("checks") or {}).get("links")
    w("### Links on /listings/ pages")
    w("")
    pages = r.get("listings_pages") or []
    if pages:
        w("Pages crawled: " + ", ".join(f"`{p['path']}` ({p['words']} words, {p['links']} links)" for p in pages) + ".")
        w("")
    if lk:
        w(f"{lk['checked']} unique URLs checked: " + ", ".join(f"{k}={v}" for k, v in sorted(lk["counts"].items())) + ".")
        expected = [i for i in lk["items"] if i["result"] == "ok" and str(i.get("via", "")).startswith("expected")]
        for i in expected:
            w(f"- Accepted by `link-expectations.json`: {i['url']} ({i['via']}).")
        bad = [i for i in lk["items"] if i["result"] != "ok" or i["missing_fragments"]]
        if bad:
            w("")
            w("| Result | HTTP | URL | Found on |")
            w("| --- | --- | --- | --- |")
            for i in bad[:80]:
                res = i["result"] + (" (anchor missing)" if i["missing_fragments"] else "")
                w(f"| {res} | {i['status'] or md_cell(i['error'], 60)} | {md_cell(i['url'], 140)} | "
                  f"{md_cell(', '.join(i['pages']), 80)} |")
    else:
        w("Not run.")
    w("")
    dl = (r.get("checks") or {}).get("doc_links")
    if dl:
        w(f"Relative and `blob/main` links inside the listing docs: {dl['checked']} checked, {dl['broken']} broken.")
        for i in [i for i in dl["items"] if i["status"] in ("NOT FOUND", "local checkout only")][:40]:
            w(f"- `{i['doc']}` → `{i['target']}`: {i['status']}")
        w("")
    ij = (r.get("checks") or {}).get("index_json") or {}
    lt = (r.get("checks") or {}).get("llms_txt") or {}
    w("### /listings/index.json and /llms.txt")
    w("")
    w(f"- `index.json`: HTTP {ij.get('status')}, valid JSON: {ij.get('valid', False)}"
      + (f", top-level keys: {', '.join(ij.get('keys', []))}" if ij.get("keys") else ""))
    w(f"- `llms.txt`: HTTP {lt.get('status')}, mentions `/listings/`: {lt.get('mentions_listings', False)}")
    w("")
    docs = r.get("docs") or {}
    if docs:
        w("### Source documents")
        w("")
        w("| Document | Present | Words | sha256 | Changed since last run | On public main |")
        w("| --- | --- | --- | --- | --- | --- |")
        for d in docs.values():
            ch = {True: "yes", False: "no", None: "first run"}.get(d.get("changed_since_last_run"), "?")
            onmain = "no" if d.get("on_public_main") is False else ("yes" if d.get("present") else "–")
            w(f"| `{d['path']}` | {'yes' if d['present'] else '**no**'} | {d.get('words', '–')} | "
              f"`{(d.get('sha256') or '')[:12]}` | {ch} | {onmain} |")
        w("")

    # 2. TIH
    w("## 2. Text Improvement Harness")
    w("")
    au = r.get("tih_audit")
    w("### Site audit (deterministic)")
    w("")
    if au:
        w(f"Whole site: {', '.join(f'{k}={v}' for k, v in sorted(au['site_counts'].items())) or 'no findings'} "
          f"(TIH exit {au['exit']}; kinds: {', '.join(f'{k}={v}' for k, v in sorted(au['site_kinds'].items()))}). "
          f"Only findings on /listings/ pages affect this monitor's status: {len(au['listings_findings'])}.")
        for f in au["listings_findings"][:30]:
            w(f"- [{f['severity']}] {f['kind']} {f['url']} {f.get('detail', '')}")
    else:
        w("Not run.")
    w("")
    w("### Scores")
    w("")
    scores = r.get("scores") or {}
    if scores:
        w("| Document | Gate | Lane | Model | Runs | Avg | Min | Max | Prev | Δ |")
        w("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
        for s in scores.values():
            for lane, d in sorted(s["lanes"].items()):
                delta = f"{d['delta']:+.1f}" if d.get("delta") is not None else "–"
                prev = f"{d['prev']:.1f}" if d.get("prev") is not None else "–"
                w(f"| {md_cell(s['label'], 60)} | {s['gate']} | {lane} | `{d['model']}` | {d['runs']} | {d['avg']:.1f} | "
                  f"{d['min']:.0f} | {d['max']:.0f} | {prev} | {delta} |")
            if s["avg"] is not None:
                w(f"| **{md_cell(s['label'], 60)}** | {s['gate']} | **average** | | | **{s['avg']:.2f}** | | | "
                  f"{(s.get('previous') or {}).get('avg') or '–'} | |")
        w("")
        lf = r.get("last_full_plan")
        if lf:
            w(f"Last full-gate plan average: {lf['avg']} (run `{lf['run_id']}`).")
            w("")
        for s in scores.values():
            for lane, d in sorted(s["lanes"].items()):
                n = d.get("notes") or {}
                if n.get("worst_thing"):
                    w(f"- {s['label']} / {lane} (lowest run), worst thing: {md_cell(n['worst_thing'], 400)} "
                      f"Next edit: {md_cell(n.get('one_best_next_edit'), 300)}")
        w("")
    else:
        w("No scores this run.")
        w("")

    # 3. adversarial
    adv = r.get("adversarial") or {}
    w("## 3. Adversarial review")
    w("")
    call = adv.get("call") or {}
    w(f"Status: **{adv.get('status', 'not run')}**. Model: `{call.get('model') or adv.get('model')}`"
      + (f", {call.get('elapsed_s')} s, finish={call.get('finish_reason')}, format={call.get('response_format')}"
         if call else "")
      + (f". Prompt ~{adv.get('est_input_tokens')} input tokens" if adv.get("est_input_tokens") else "")
      + (f", estimated ${adv['est_cost_usd']:.2f} per call ({adv.get('est_basis')})"
         if adv.get("est_cost_usd") is not None else "") + ".")
    if adv.get("prompt_path"):
        w(f"Prompt sent: `{adv['prompt_path']}`.")
    w("")
    res = adv.get("result") if isinstance(adv.get("result"), dict) else None
    ver = adv.get("verification") or {}
    if res and (res.get("overall_assessment") or any(res.get(k) for k in ADVERSARIAL_LIST_KEYS)):
        w(f"**Readiness: {res.get('listing_readiness')}.** {md_cell(res.get('overall_assessment'), None)}")
        w("")
        if ver:
            w(f"Checked by the monitor: {ver.get('quotes_verified', 0)}/{ver.get('quotes_checked', 0)} claim quotes found "
              f"verbatim in the inputs ({ver.get('quotes_partial', 0)} partial, {ver.get('quotes_not_found', 0)} not found); "
              f"{ver.get('paths_found', 0)}/{ver.get('paths_checked', 0)} cited repo paths exist.")
            w("")
        claims = res.get("unsupported_or_contradicted_claims") or []
        w(f"### Unsupported or contradicted claims ({len(claims)})")
        w("")
        if claims:
            w("| Sev | Status | Claim (quote check) | Source | Problem | File to check (exists?) | Fix |")
            w("| --- | --- | --- | --- | --- | --- | --- |")
            order = {"high": 0, "medium": 1, "low": 2}
            for c in sorted(claims, key=lambda c: order.get(c.get("severity"), 3)):
                paths = "; ".join(f"`{p['path']}` ({p['status']})" for p in c.get("_path_check") or []) or \
                    md_cell(c.get("repo_file_to_check"), 80)
                w(f"| {c.get('severity')} | {c.get('status')} | “{md_cell(c.get('claim_quote'), 200)}” "
                  f"({c.get('_quote_check')}) | {md_cell(c.get('source_document'), 60)} | {md_cell(c.get('problem'), 300)} | "
                  f"{paths} | {md_cell(c.get('suggested_fix'), 200)} |")
            w("")
        framing = res.get("misleading_framing_or_omissions") or []
        w(f"### Misleading framing and omissions ({len(framing)})")
        w("")
        if framing:
            w("| Topic | Kind | Sev | Quote | Problem | Fix |")
            w("| --- | --- | --- | --- | --- | --- |")
            for f in framing:
                q = f"“{md_cell(f.get('quote'), 160)}” ({f.get('_quote_check')})" if str(f.get("quote", "")).strip() else "–"
                w(f"| {f.get('topic')} | {f.get('kind')} | {f.get('severity')} | {q} | {md_cell(f.get('problem'), 300)} | "
                  f"{md_cell(f.get('suggested_fix'), 200)} |")
            w("")
        refs = res.get("broken_or_circular_references") or []
        w(f"### Broken or circular references ({len(refs)})")
        w("")
        if ver.get("refs_contradicted_by_tree"):
            w(f"The monitor found the target of {ver['refs_contradicted_by_tree']} reference(s) the model called "
              f"broken or dangling; those entries are marked below.")
            w("")
        for x in refs:
            pc = x.get("_path_check") or []
            note = ""
            if pc:
                note = " Monitor: " + "; ".join(f"`{c['path']}` {c['status']}" for c in pc) + "."
            w(f"- [{x.get('severity')}/{x.get('kind')}] `{md_cell(x.get('reference'), 160)}` in "
              f"{md_cell(x.get('source_document'), 60)}: {md_cell(x.get('problem'), 300)}{note}")
        w("")
        qs = res.get("top_coinbase_questions") or []
        w("### Top questions Coinbase would still ask")
        w("")
        for i, q in enumerate(qs, 1):
            w(f"{i}. **{md_cell(q.get('question'), None)}** Why: {md_cell(q.get('why_it_matters'), 300)} "
              f"Answer belongs in: {md_cell(q.get('where_answer_should_live'), 160)}")
        w("")
        hl = res.get("hostile_journalist_headlines") or []
        if hl:
            w("### Hostile-journalist headlines")
            w("")
            for h in hl:
                w(f"- **{md_cell(h.get('headline'), 200)}**: “{md_cell(h.get('supporting_quote'), 200)}” "
                  f"({h.get('_quote_check', 'n/a')}). Current rebuttal: {md_cell(h.get('best_available_rebuttal'), 240) or 'none'}")
            w("")
    elif adv.get("status", "").startswith("dry-run"):
        w("Dry run: the prompt was built and saved and no model was called. Inputs: "
          + ", ".join(f"`{i['label']}` ({i['chars']} chars)" for i in adv.get("inputs", [])) + ".")
        w("")
    elif adv.get("errors"):
        w("Errors: " + "; ".join(md_cell(e, 200) for e in adv["errors"]))
        w("")

    # cost
    w("## Cost")
    w("")
    rows = (r.get("cost") or {}).get("rows") or []
    if rows:
        w("| Step | Provider | Model | Calls | Tokens in | Tokens out | USD | Basis |")
        w("| --- | --- | --- | --- | --- | --- | --- | --- |")
        for x in rows:
            w(f"| {x.get('step')} | {x['provider']} | `{x['model']}` | {x['calls']} | {x['tokens_in']} | {x['tokens_out']} | "
              f"{x['cost_usd']:.4f} | {x['cost_basis']} |")
    else:
        w("No paid model calls this run.")
    w("")
    w(f"Pricing source: {(r.get('cost') or {}).get('pricing_source')}. GitHub: {m['github']['auth']} "
      f"({m['github']['api_calls']} API calls, {m['github']['raw_fetches']} raw fetches).")
    w("")
    w("## Artifacts")
    w("")
    w(f"- Run directory: `{m['run_dir']}` (fetched sources, page text, TIH logs, prompt, raw model response)")
    w(f"- Stage timings (s): {', '.join(f'{k}={v}' for k, v in (r.get('stage_seconds') or {}).items())}")
    w("")
    return "\n".join(L) + "\n"


# ---------------------------------------------------------------------------
# Self-test (no network, no model calls)
# ---------------------------------------------------------------------------


def self_test() -> int:
    failures = 0

    def check(name: str, cond: bool) -> None:
        nonlocal failures
        print(("ok   " if cond else "FAIL ") + name)
        failures += 0 if cond else 1

    chain = ("# PostFiat L1 Current State\n\nUpdated: `2026-10-21T12:35:00Z` (x)\n\n"
             "!!! success \"2026-10-21: store-handle release deployed to all six validators\"\n\n"
             "| Field | Value |\n| --- | --- |\n| Chain | `postfiat-wan-devnet-2` |\n| Validators | 6, all converged |\n")
    facts = parse_chain_state(chain)
    check("chain facts: network", facts["network"] == "postfiat-wan-devnet-2")
    check("chain facts: validators", facts["validators"] == 6)
    check("chain facts: updated", facts["updated"] == "2026-10-21T12:35:00Z")
    page = ("The L1 runs as postfiat-wan-devnet-2, a six-validator devnet. All 6 validators are Foundation-administered. "
            "The legacy postfiatd testnet lists 53 validators in the VHS snapshot. An old postfiat-wan-devnet-1 note. "
            "Quorum is 5 of 6 validators. PFTL runs on a 7-validator network today. "
            "Releases use a one-validator-at-a-time rollout. At the whitepaper's 35-validator example it needs 24.")
    claims = extract_chain_claims("/listings/", page)
    judge_chain_claims(claims, facts)
    verdicts = {(c["kind"], str(c.get("match", c["value"]))): c["verdict"] for c in claims}
    check("claims: current network matches", verdicts.get(("network", "postfiat-wan-devnet-2")) == "match")
    check("claims: six-validator matches", verdicts.get(("validators", "six-validator")) == "match")
    check("claims: all 6 validators matches", verdicts.get(("validators", "All 6 validators")) == "match")
    check("claims: 7-validator flagged", verdicts.get(("validators", "7-validator")) == "MISMATCH")
    check("claims: devnet-1 historical", verdicts.get(("network", "postfiat-wan-devnet-1")) == "historical mention")
    check("claims: '5 of 6 validators' ignored", not any("5" == str(c["value"]) for c in claims))
    check("claims: 'one-validator-at-a-time' ignored", not any(c["value"] == 1 for c in claims))
    check("claims: '35-validator example' not compared",
          verdicts.get(("validators", "35-validator")) == "example or hypothetical, not compared")
    fm = parse_front_matter('---\ntitle: "X"\nsource_repo: "postfiatorg/postfiatl1v2"\nsource_commit: "90aebe371"\n---\nbody')
    check("front matter", fm.get("source_commit") == "90aebe371" and fm.get("source_repo") == UPSTREAM_REPO)
    check("markdown links skip code fences",
          markdown_links("[a](x.md)\n```\n[b](y.md)\n```\n[c]: ../z.md\n") == ["x.md", "../z.md"])
    fenced = '```json\n{"overall_assessment": "x", "listing_readiness": "not_ready"}\n```'
    check("lenient JSON parse (fenced)", parse_json_lenient(fenced)["listing_readiness"] == "not_ready")
    check("lenient JSON parse (prefixed)", parse_json_lenient('Here: {"a": 1} end')["a"] == 1)
    corpus = normalize_for_match("Accounts sign with **ML-DSA** from genesis — see [the paper](x.md).")
    check("quote verified", quote_status("Accounts sign with ML-DSA from genesis - see the paper", corpus) == "verified")
    check("quote not found", quote_status("Audited by Trail of Bits", corpus) == "not_found")
    tree = {"blobs": {"docs/status/chain-state-current.md"}, "dirs": {"docs", "docs/status"}}
    check("repo path cleanup",
          clean_repo_path("https://github.com/postfiatorg/postfiatl1v2/blob/main/docs/status/chain-state-current.md#x")
          == ["docs/status/chain-state-current.md"])
    check("repo path status", path_status("docs/status/chain-state-current.md", tree, None) == "exists at main"
          and path_status("docs/audits/report.md", tree, None) == "NOT FOUND")
    canned = {"overall_assessment": "x", "listing_readiness": "not_ready",
              "unsupported_or_contradicted_claims": [{"claim_quote": "sign with ML-DSA from genesis",
                                                      "source_document": "site:/listings/", "status": "needs_repo_check",
                                                      "problem": "p", "repo_file_to_check": "postfiatl1v2/docs/status/chain-state-current.md:10",
                                                      "severity": "high", "suggested_fix": "f"}],
              "misleading_framing_or_omissions": [{"topic": t, "kind": "no_issue", "quote": "", "source_document": "",
                                                   "problem": "no issue found", "severity": "low", "suggested_fix": ""}
                                                  for t in REQUIRED_TOPICS],
              "broken_or_circular_references": [], "hostile_journalist_headlines": [],
              "top_coinbase_questions": [{"question": "q", "why_it_matters": "w", "where_answer_should_live": "l"}] * 5}
    check("shape ok", shape_problems(canned) == [])
    stats = annotate_adversarial(canned, corpus, tree, None)
    check("annotate: quote + path", stats["quotes_verified"] == 1 and stats["paths_found"] == 1)
    check("shape catches missing questions", any("expected 5" in p for p in shape_problems({**canned, "top_coinbase_questions": []})))
    md = render_markdown({"meta": {"run_id": "t", "mode": "cheap", "started": "2026-10-22T00:00:00Z",
                                   "finished": "2026-10-22T00:00:01Z", "duration_s": 1, "status": "PASS", "exit_code": 0,
                                   "target": {"base_url": "http://127.0.0.1:1/", "kind": "test", "site_repo": None},
                                   "mock_scores": True, "adversarial_mode": "dry-run", "db": "x", "project": "p",
                                   "run_dir": "x", "counts": {"hard": 0, "warn": 0, "info": 0},
                                   "github": {"auth": "anonymous", "api_calls": 0, "raw_fetches": 0}},
                          "findings": [], "adversarial": {"status": "ok", "result": canned, "verification": stats},
                          "cost": {"rows": [], "total_usd": 0}})
    check("render markdown", "Readiness: not_ready" in md and "Top questions" in md)
    print(f"self-test: {'PASS' if not failures else f'{failures} FAILED'}")
    return 1 if failures else 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def default_hugo() -> str:
    local = HOME / ".local" / "bin" / "hugo"
    return str(local) if local.exists() else (shutil.which("hugo") or "hugo")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0], formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    g = p.add_argument_group("run")
    g.add_argument("--mode", choices=["cheap", "full", "auto"], default="cheap",
                   help="auto = full on Mondays (UTC), cheap otherwise")
    g.add_argument("--state-dir", type=pathlib.Path, default=DEFAULT_STATE_DIR,
                   help="reports/, runs/, history.jsonl, TIH DB")
    g.add_argument("--db", type=pathlib.Path, help="TIH database (default: <state-dir>/tih.sqlite3)")
    g.add_argument("--project", default="postfiat-listings")
    g.add_argument("--tih-dir", type=pathlib.Path, default=DEFAULT_TIH_DIR)
    g.add_argument("--strict", action="store_true",
                   help="treat chain-fact mismatches and llms.txt gaps as hard failures")
    g.add_argument("--self-test", action="store_true", help="run offline parser tests and exit")
    g = p.add_argument_group("target site")
    g.add_argument("--base-url", default=CANONICAL_ORIGIN + "/", help="site to check (live or a local server)")
    g.add_argument("--site-repo", type=pathlib.Path,
                   help="Hugo site checkout: front-matter mirrors, and a build for the TIH audit")
    g.add_argument("--build-dir", type=pathlib.Path, help="prebuilt site directory for the TIH audit")
    g.add_argument("--serve-local", action="store_true",
                   help="build --site-repo and serve it on 127.0.0.1 for this run (pre-launch target)")
    g.add_argument("--hugo", default=default_hugo())
    g.add_argument("--max-pages", type=int, default=60, help="crawl limit under /listings/")
    g = p.add_argument_group("source docs")
    g.add_argument("--docs-repo", type=pathlib.Path,
                   help="read listing docs from this postfiatl1v2 checkout instead of GitHub main")
    g = p.add_argument_group("checks")
    g.add_argument("--drift-days", type=float, default=7.0, help="hard fail when a mirror lags main longer")
    g.add_argument("--chain-state-stale-days", type=float, default=14.0)
    g.add_argument("--skip-links", action="store_true")
    g.add_argument("--link-workers", type=int, default=8)
    g.add_argument("--link-timeout", type=float, default=20.0)
    g.add_argument("--link-expectations", type=pathlib.Path, default=HERE / "link-expectations.json",
                   help="JSON rules for links whose non-200 status is intended")
    g = p.add_argument_group("TIH scoring")
    g.add_argument("--mock", action="store_true", help="pass --mock to TIH scoring (no model spend)")
    g.add_argument("--runs", type=int, help="runs per lane (default: cheap 1, full 5)")
    g.add_argument("--cheap-lane", default="fable", help="judge lane for the cheap gate")
    g.add_argument("--score-docs", default="plan,landing", help="comma list from: plan, landing")
    g.add_argument("--concurrency", type=int, default=15)
    g.add_argument("--plan-threshold", type=float, default=86.0, help="hard fail below this full-gate plan average")
    g.add_argument("--lane-drop", type=float, default=3.0, help="flag a lane that falls more than this")
    g = p.add_argument_group("adversarial review")
    g.add_argument("--adversarial", choices=["real", "dry-run", "skip"], default="real")
    g.add_argument("--adversarial-model", default="openai/gpt-5.6-sol-pro")
    g.add_argument("--adversarial-fallback", default="anthropic/claude-fable-5.1")
    g.add_argument("--adversarial-effort", default="high", choices=["low", "medium", "high"])
    g.add_argument("--adversarial-max-tokens", type=int, default=40000)
    g.add_argument("--adversarial-timeout", type=float, default=1800.0, help="socket timeout, seconds")
    g.add_argument("--adversarial-reuse-days", type=float, default=7.0,
                   help="cheap mode reuses the last review when inputs are unchanged and it is this recent (0 = never)")
    g.add_argument("--est-adversarial-output-tokens", type=int, default=15000, help="for the cost estimate only")
    g.add_argument("--chain-excerpt-chars", type=int, default=12000)
    g.add_argument("--repo-index-limit", type=int, default=450)
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.self_test:
        return self_test()
    try:
        return Monitor(args).run()
    except SystemExit as exc:
        if isinstance(exc.code, int):
            return exc.code
        print(f"error: {exc}", file=sys.stderr)
        return 3
    except Exception:
        traceback.print_exc()
        return 3


if __name__ == "__main__":
    sys.exit(main())
