#!/usr/bin/env python3
"""Build a frozen XLS provenance/support packet from XRPLF/XRPL-Standards.

The packet is meant to answer a narrow editorial question:

    "Is this proposal actually supported by a source-backed XRP/XRPL author?"

It deliberately separates:
  * strict support: Ripple author or explicit XRPL-org author evidence;
  * broad support: strict support plus recurring XLS author evidence;
  * topic surface: institutional/compliance/SWIFT-like content flags.

The topic flags are not provenance. They are review cues.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STANDARDS_DIR = ROOT / ".tih" / "external-cache" / "XRPL-Standards"
DEFAULT_ARTIFACT_ROOT = ROOT / "static" / "benchmarks"
REPO_URL = "https://github.com/XRPLF/XRPL-Standards"


EXPLICIT_XRPL_ORG_DOMAINS = {
    "xrpl-labs.com": "XRPL Labs",
}

ECOSYSTEM_DOMAINS_FOR_REVIEW = {
    "transia.co": "Transia",
    "xumm.dev": "Xumm/XRPL Labs",
}

EXTERNAL_AUTHOR_EVIDENCE = {
    "nikolaosbougalis": [
        {
            "class": "external_xrp_author",
            "url": "https://www.coindesk.com/markets/2020/04/02/ripple-engineers-publish-design-for-private-transactions-on-xrp-ledger",
            "claim": "CoinDesk identifies Nik Bougalis as a Ripple engineer publishing an XRP Ledger privacy proposal.",
        },
        {
            "class": "external_xrp_author",
            "url": "https://nik.bougalis.net/validator/",
            "claim": "Nik Bougalis states that he operates an XRP Ledger validator as a participant in the ecosystem.",
        },
    ],
    "nikbougalis": [
        {
            "class": "external_xrp_author",
            "url": "https://www.coindesk.com/markets/2020/04/02/ripple-engineers-publish-design-for-private-transactions-on-xrp-ledger",
            "claim": "CoinDesk identifies Nik Bougalis as a Ripple engineer publishing an XRP Ledger privacy proposal.",
        }
    ],
    "nikb": [
        {
            "class": "external_xrp_author",
            "url": "https://nik.bougalis.net/validator/",
            "claim": "Nik Bougalis states that he operates an XRP Ledger validator as a participant in the ecosystem.",
        }
    ],
    "richardholland": [
        {
            "class": "external_xrp_author",
            "url": "https://thecryptobasic.com/2023/12/04/xrpl-labs-proposes-new-atomic-multi-asset-payments-transactor-for-xahau/",
            "claim": "The Crypto Basic identifies Richard Holland as CTO of XRPL Labs and author of the Remit proposal.",
        },
        {
            "class": "external_xrp_author",
            "url": "https://evernode-labs.com.au/about",
            "claim": "Evernode Labs describes a Ripple UBRI/XRPL Grants-backed collaboration involving Richard Holland in the XRPL ecosystem.",
        },
    ],
    "richardah": [
        {
            "class": "external_xrp_author",
            "url": "https://thecryptobasic.com/2023/12/04/xrpl-labs-proposes-new-atomic-multi-asset-payments-transactor-for-xahau/",
            "claim": "The Crypto Basic identifies Richard Holland as CTO of XRPL Labs and author of the Remit proposal.",
        }
    ],
    "tequ": [
        {
            "class": "external_xrp_author",
            "url": "https://tequ.dev/about",
            "claim": "Tequ self-identifies as an XRP Ledger ecosystem developer.",
        }
    ],
    "tequdev": [
        {
            "class": "external_xrp_author",
            "url": "https://tequ.dev/about",
            "claim": "Tequ self-identifies as an XRP Ledger ecosystem developer.",
        }
    ],
    "denisangell": [
        {
            "class": "external_xrp_author",
            "url": "https://dev.to/dangell7",
            "claim": "Denis Angell's DEV profile identifies him as an XRPL developer.",
        }
    ],
    "dangell7": [
        {
            "class": "external_xrp_author",
            "url": "https://dev.to/dangell7",
            "claim": "Denis Angell's DEV profile identifies him as an XRPL developer.",
        }
    ],
    "hubertgetrouw": [
        {
            "class": "external_xrp_author",
            "url": "https://dailyhodl.com/2021/03/09/heres-how-nfts-are-coming-to-the-xrp-ledger-according-to-ripple-backed-xrpl-labs/",
            "claim": "Daily Hodl identifies Hubert Getrouw with XRPL Labs in coverage of XRPL NFT work.",
        }
    ],
    "hubertg97": [
        {
            "class": "external_xrp_author",
            "url": "https://dailyhodl.com/2021/03/09/heres-how-nfts-are-coming-to-the-xrp-ledger-according-to-ripple-backed-xrpl-labs/",
            "claim": "Daily Hodl identifies Hubert Getrouw with XRPL Labs in coverage of XRPL NFT work.",
        }
    ],
}

MANUAL_ALIAS_GROUPS = [
    # Corpus-internal propagation groups. These do not invent affiliation; they
    # connect handles/names to emails already present in the frozen corpus or
    # commit history.
    ["mayukhavadari", "mvadari"],
    ["vytautasvitotumas", "vitotumas", "vtumas", "tapanito"],
    ["davidfuelling", "fuelling", "sappenin"],
    ["julianberridi", "jberridi", "julian78780"],
    ["gregoryweisbrod", "gregweisbrod", "gweisbrod"],
    ["shawnxie", "shawnxie999"],
    ["yinyiqian", "yinyiqian1"],
    ["aanchalmalhotra", "amalhotra"],
    ["davidjschwartz", "davidschwartz"],
    ["scottschurr"],
    ["scottdeterman", "sdeterman"],
    ["edhennis"],
    ["gregorytsipenyuk", "gtsipenyuk"],
    ["kuanlin", "klin"],
    ["ashraychowdhry", "achowdhry", "achowdhryripple"],
    ["wietsewind", "wietse"],
    ["nikolaosdbougalis", "nikolaosbougalis", "nikbougalis", "nikb"],
    ["richardholland", "richardah"],
    ["denisangell", "dangell", "dangell7"],
    ["tequ", "tequdev"],
]

INSTITUTIONAL_KEYWORDS = {
    "swift_or_correspondent": [
        "swift",
        "iso 20022",
        "correspondent",
        "interbank",
        "cross-border",
        "remittance",
        "remit",
    ],
    "regulated_institution": [
        "regulated",
        "institution",
        "financial institution",
        "bank",
        "compliance",
        "aml",
        "kyc",
        "sanction",
        "permissioned",
        "credential",
        "confidential",
        "privacy",
    ],
    "issuer_controls": [
        "issuer",
        "clawback",
        "freeze",
        "deep freeze",
        "global freeze",
        "blacklist",
        "whitelist",
    ],
    "credit_lending": [
        "loan",
        "lending",
        "borrower",
        "underwriting",
        "first-loss",
        "credit",
        "vault",
    ],
    "payments_billing": [
        "payment",
        "invoice",
        "subscription",
        "direct debit",
        "paychan",
        "escrow",
    ],
}


@dataclass
class Identity:
    raw: str
    name: str = ""
    emails: list[str] = field(default_factory=list)
    handles: list[str] = field(default_factory=list)
    keys: list[str] = field(default_factory=list)


class UnionFind:
    def __init__(self) -> None:
        self.parent: dict[str, str] = {}

    def find(self, item: str) -> str:
        if item not in self.parent:
            self.parent[item] = item
        if self.parent[item] != item:
            self.parent[item] = self.find(self.parent[item])
        return self.parent[item]

    def union(self, a: str, b: str) -> None:
        ra = self.find(a)
        rb = self.find(b)
        if ra != rb:
            self.parent[rb] = ra


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run(args: list[str], cwd: Path | None = None) -> str:
    return subprocess.check_output(args, cwd=cwd, text=True, stderr=subprocess.STDOUT)


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def split_author_list(raw: str) -> list[str]:
    parts: list[str] = []
    buf: list[str] = []
    depth_angle = 0
    depth_paren = 0
    depth_bracket = 0
    for ch in raw:
        if ch == "<":
            depth_angle += 1
        elif ch == ">" and depth_angle:
            depth_angle -= 1
        elif ch == "(":
            depth_paren += 1
        elif ch == ")" and depth_paren:
            depth_paren -= 1
        elif ch == "[":
            depth_bracket += 1
        elif ch == "]" and depth_bracket:
            depth_bracket -= 1
        if ch == "," and depth_angle == 0 and depth_paren == 0 and depth_bracket == 0:
            item = "".join(buf).strip()
            if item:
                parts.append(item)
            buf = []
        else:
            buf.append(ch)
    item = "".join(buf).strip()
    if item:
        parts.append(item)
    return parts


def parse_identity(raw: str) -> Identity:
    raw = raw.strip()
    emails = [m.lower() for m in re.findall(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}", raw)]
    handles = [m.lower() for m in re.findall(r"@([A-Za-z0-9_\-]+)", raw) if "." not in m]
    name = raw
    name = re.sub(r"<[^>]+>", " ", name)
    name = re.sub(r"\([^)]*@[^)]*\)", " ", name)
    name = re.sub(r"@[A-Za-z0-9_\-]+", " ", name)
    name = re.sub(r"\s+", " ", name).strip(" ,")
    keys: list[str] = []
    if name:
        keys.append(slug(name))
    for email in emails:
        keys.append(slug(email))
        local, _, domain = email.partition("@")
        keys.append(slug(local))
        if "+" in local:
            keys.append(slug(local.rsplit("+", 1)[1]))
        keys.append(slug(domain))
    for handle in handles:
        keys.append(slug(handle))
    keys = [k for k in dict.fromkeys(keys) if k]
    return Identity(raw=raw, name=name, emails=emails, handles=handles, keys=keys)


def parse_pre_metadata(markdown: str) -> dict[str, str]:
    match = re.search(r"<pre>(.*?)</pre>", markdown, flags=re.DOTALL | re.IGNORECASE)
    if not match:
        return {}
    meta: dict[str, str] = {}
    current_key = ""
    for line in match.group(1).splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        key_match = re.match(r"([A-Za-z0-9_\-]+):\s*(.*)$", stripped)
        if key_match:
            current_key = key_match.group(1).lower()
            meta[current_key] = key_match.group(2).strip()
        elif current_key:
            meta[current_key] = f"{meta[current_key]} {stripped}".strip()
    return meta


def github_blob_url(commit: str, relpath: str) -> str:
    return f"{REPO_URL}/blob/{commit}/{relpath}"


def github_commit_url(commit_hash: str) -> str:
    return f"{REPO_URL}/commit/{commit_hash}"


def get_file_commits(standards_dir: Path, relpath: str) -> list[dict[str, str]]:
    fmt = "%H%x09%an%x09%ae%x09%cn%x09%ce%x09%cI%x09%s"
    output = run(["git", "log", "--follow", f"--format={fmt}", "--", relpath], cwd=standards_dir)
    commits: list[dict[str, str]] = []
    for line in output.splitlines():
        parts = line.split("\t")
        if len(parts) < 7:
            continue
        commit, an, ae, cn, ce, ci, subject = parts[:7]
        commits.append(
            {
                "commit": commit,
                "author_name": an,
                "author_email": ae.lower(),
                "committer_name": cn,
                "committer_email": ce.lower(),
                "commit_date": ci,
                "subject": subject,
                "url": github_commit_url(commit),
            }
        )
    return commits


def content_flags(text: str) -> tuple[list[str], list[str]]:
    lower = text.lower()
    categories: list[str] = []
    hits: list[str] = []
    for category, terms in INSTITUTIONAL_KEYWORDS.items():
        matched = [term for term in terms if term in lower]
        if matched:
            categories.append(category)
            hits.extend(matched)
    return sorted(set(categories)), sorted(set(hits))


def evidence_snippets(text: str, terms: list[str], limit: int = 4) -> list[str]:
    snippets: list[str] = []
    lower = text.lower()
    for term in terms:
        idx = lower.find(term.lower())
        if idx == -1:
            continue
        start = max(0, idx - 130)
        end = min(len(text), idx + len(term) + 170)
        snippet = re.sub(r"\s+", " ", text[start:end]).strip()
        if snippet and snippet not in snippets:
            snippets.append(snippet)
        if len(snippets) >= limit:
            break
    return snippets


def classify_support(
    identities: list[Identity],
    commits: list[dict[str, str]],
    uf: UnionFind,
    root_classes: dict[str, set[str]],
    author_proposal_counts: Counter[str],
    final_author_roots: set[str],
) -> dict[str, Any]:
    front_roots: set[str] = set()
    for identity in identities:
        for key in identity.keys:
            front_roots.add(uf.find(key))

    commit_roots: set[str] = set()
    for commit in commits:
        for raw in (
            f"{commit['author_name']} <{commit['author_email']}>",
            f"{commit['committer_name']} <{commit['committer_email']}>",
        ):
            identity = parse_identity(raw)
            for key in identity.keys:
                commit_roots.add(uf.find(key))

    def has_class(roots: set[str], cls: str) -> bool:
        return any(cls in root_classes.get(root, set()) for root in roots)

    recurring_roots = {
        root
        for root in front_roots
        if author_proposal_counts[root] >= 2 or root in final_author_roots
    }

    maintainer_touch = has_class(commit_roots, "ripple") or has_class(commit_roots, "explicit_xrpl_org")

    if has_class(front_roots, "ripple"):
        strict = "DIRECT_RIPPLE_AUTHOR"
    elif has_class(front_roots, "explicit_xrpl_org"):
        strict = "DIRECT_EXPLICIT_XRPL_ORG_AUTHOR"
    elif has_class(front_roots, "external_xrp_author"):
        strict = "DIRECT_EXTERNAL_XRP_AUTHOR_EVIDENCE"
    else:
        strict = "NO_DIRECT_XRP_AUTHOR_SUPPORT"

    if strict in {"DIRECT_RIPPLE_AUTHOR", "DIRECT_EXPLICIT_XRPL_ORG_AUTHOR", "DIRECT_EXTERNAL_XRP_AUTHOR_EVIDENCE"}:
        broad = strict
    elif recurring_roots:
        broad = "DIRECT_RECURRING_XLS_AUTHOR"
    else:
        broad = "NO_BROAD_XRP_AUTHOR_SUPPORT"

    root_labels = []
    for root in sorted(front_roots):
        classes = sorted(root_classes.get(root, set()))
        root_labels.append({"root": root, "classes": classes, "proposal_count": author_proposal_counts[root]})

    return {
        "strict_support_tier": strict,
        "broad_support_tier": broad,
        "front_author_roots": sorted(front_roots),
        "commit_identity_roots": sorted(commit_roots),
        "front_author_root_labels": root_labels,
        "front_has_ripple": has_class(front_roots, "ripple"),
        "front_has_explicit_xrpl_org": has_class(front_roots, "explicit_xrpl_org"),
        "front_has_external_xrp_author_evidence": has_class(front_roots, "external_xrp_author"),
        "front_has_recurring_xls_author": bool(recurring_roots),
        "commit_has_ripple_or_explicit_xrpl_org": maintainer_touch,
        "maintainer_touch_tier": "RIPPLE_OR_EXPLICIT_XRPL_ORG_TOUCH" if maintainer_touch else "NO_XRP_MAINTAINER_TOUCH",
    }


def write_csv(path: Path, rows: list[dict[str, Any]], columns: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def build_packet(standards_dir: Path, artifact_dir: Path, fetch: bool) -> None:
    if not standards_dir.exists():
        standards_dir.parent.mkdir(parents=True, exist_ok=True)
        run(["git", "clone", REPO_URL, str(standards_dir)])
    if fetch:
        run(["git", "fetch", "--all", "--prune"], cwd=standards_dir)
        default_branch = run(["git", "symbolic-ref", "refs/remotes/origin/HEAD"], cwd=standards_dir).strip()
        branch = default_branch.rsplit("/", 1)[-1]
        run(["git", "checkout", branch], cwd=standards_dir)
        run(["git", "pull", "--ff-only"], cwd=standards_dir)

    artifact_dir.mkdir(parents=True, exist_ok=True)
    commit = run(["git", "rev-parse", "HEAD"], cwd=standards_dir).strip()
    commit_date = run(["git", "log", "-1", "--format=%cI"], cwd=standards_dir).strip()
    commit_subject = run(["git", "log", "-1", "--format=%s"], cwd=standards_dir).strip()
    commit_author = run(["git", "log", "-1", "--format=%an <%ae>"], cwd=standards_dir).strip()

    proposal_paths = sorted(
        path
        for path in standards_dir.glob("XLS-*/README.md")
        if path.parent.is_dir()
    )

    raw_rows: list[dict[str, Any]] = []
    all_identity_events: list[Identity] = []
    path_commits: dict[str, list[dict[str, str]]] = {}

    for readme in proposal_paths:
        relpath = readme.relative_to(standards_dir).as_posix()
        text = readme.read_text(encoding="utf-8", errors="replace")
        meta = parse_pre_metadata(text)
        xls_match = re.match(r"XLS-(\d+)", readme.parent.name, flags=re.IGNORECASE)
        xls_number = meta.get("xls") or (str(int(xls_match.group(1))) if xls_match else "")
        author_raw = meta.get("author") or meta.get("authors") or ""
        identities = [parse_identity(part) for part in split_author_list(author_raw)] if author_raw else []
        for identity in identities:
            all_identity_events.append(identity)
        commits = get_file_commits(standards_dir, relpath)
        path_commits[relpath] = commits
        for commit_row in commits:
            all_identity_events.append(parse_identity(f"{commit_row['author_name']} <{commit_row['author_email']}>"))
            all_identity_events.append(parse_identity(f"{commit_row['committer_name']} <{commit_row['committer_email']}>"))
        categories, hits = content_flags(text)
        raw_rows.append(
            {
                "id": f"XLS-{int(xls_number):04d}" if xls_number else readme.parent.name,
                "xls_number": int(xls_number) if str(xls_number).isdigit() else None,
                "dir": readme.parent.name,
                "relpath": relpath,
                "title": meta.get("title", ""),
                "description": meta.get("description", ""),
                "category": meta.get("category", ""),
                "status": meta.get("status", ""),
                "created": meta.get("created", ""),
                "updated": meta.get("updated", ""),
                "requires": meta.get("requires", ""),
                "proposal_from": meta.get("proposal-from", ""),
                "implementation": meta.get("implementation", ""),
                "author_raw": author_raw,
                "authors": identities,
                "readme_url": github_blob_url(commit, relpath),
                "readme_sha256": sha256_file(readme),
                "commit_count": len(commits),
                "last_file_commit": commits[0]["commit"] if commits else "",
                "last_file_commit_url": commits[0]["url"] if commits else "",
                "institutional_categories": categories,
                "institutional_terms": hits,
                "institutional_snippets": evidence_snippets(text, hits),
            }
        )

    uf = UnionFind()
    for identity in all_identity_events:
        if not identity.keys:
            continue
        first = identity.keys[0]
        for key in identity.keys:
            uf.union(first, key)
    for group in MANUAL_ALIAS_GROUPS:
        normalized = [slug(item) for item in group if slug(item)]
        if not normalized:
            continue
        first = normalized[0]
        for key in normalized:
            uf.union(first, key)

    root_classes: dict[str, set[str]] = defaultdict(set)
    root_evidence: dict[str, list[str]] = defaultdict(list)
    for identity in all_identity_events:
        roots = {uf.find(key) for key in identity.keys}
        if not roots:
            continue
        domains = [email.partition("@")[2].lower() for email in identity.emails]
        for root in roots:
            for domain in domains:
                if domain == "ripple.com":
                    root_classes[root].add("ripple")
                    root_evidence[root].append(f"email:{identity.raw}")
                if domain in EXPLICIT_XRPL_ORG_DOMAINS:
                    root_classes[root].add("explicit_xrpl_org")
                    root_evidence[root].append(f"email:{identity.raw}")
                if domain in ECOSYSTEM_DOMAINS_FOR_REVIEW:
                    root_classes[root].add("ecosystem_domain_for_review")
                    root_evidence[root].append(f"email:{identity.raw}")
            for handle in identity.handles:
                if "ripple" in handle.lower():
                    root_classes[root].add("ripple")
                    root_evidence[root].append(f"handle:{identity.raw}")
    for key, evidence_items in EXTERNAL_AUTHOR_EVIDENCE.items():
        root = uf.find(slug(key))
        for evidence in evidence_items:
            root_classes[root].add(evidence["class"])
            root_evidence[root].append(f"external:{evidence['claim']} {evidence['url']}")

    author_proposal_counts: Counter[str] = Counter()
    final_author_roots: set[str] = set()
    for row in raw_rows:
        row_roots = set()
        for identity in row["authors"]:
            for key in identity.keys:
                row_roots.add(uf.find(key))
        for root in row_roots:
            author_proposal_counts[root] += 1
            if row["status"].lower() == "final":
                final_author_roots.add(root)

    rows: list[dict[str, Any]] = []
    for row in raw_rows:
        support = classify_support(
            row["authors"],
            path_commits[row["relpath"]],
            uf,
            root_classes,
            author_proposal_counts,
            final_author_roots,
        )
        institutional = bool(row["institutional_categories"])
        strict_weak = support["strict_support_tier"] in {
            "NO_DIRECT_XRP_AUTHOR_SUPPORT",
        }
        broad_weak = support["broad_support_tier"] in {
            "NO_BROAD_XRP_AUTHOR_SUPPORT",
        }
        review_flags = []
        if institutional and strict_weak:
            review_flags.append("institutional_surface_without_strict_xrp_author")
        if institutional and broad_weak:
            review_flags.append("institutional_surface_without_broad_xrp_author")
        if not row["author_raw"]:
            review_flags.append("missing_author_metadata")
        if row["category"].lower() == "amendment" and row["status"].lower() in {"draft", "stagnant", "deprecated"}:
            review_flags.append("non_final_amendment")
        flat = {
            "id": row["id"],
            "xls_number": row["xls_number"],
            "title": row["title"],
            "description": row["description"],
            "category": row["category"],
            "status": row["status"],
            "created": row["created"],
            "updated": row["updated"],
            "author_raw": row["author_raw"],
            "strict_support_tier": support["strict_support_tier"],
            "broad_support_tier": support["broad_support_tier"],
            "front_has_ripple": support["front_has_ripple"],
            "front_has_explicit_xrpl_org": support["front_has_explicit_xrpl_org"],
            "front_has_external_xrp_author_evidence": support["front_has_external_xrp_author_evidence"],
            "front_has_recurring_xls_author": support["front_has_recurring_xls_author"],
            "commit_has_ripple_or_explicit_xrpl_org": support["commit_has_ripple_or_explicit_xrpl_org"],
            "maintainer_touch_tier": support["maintainer_touch_tier"],
            "institutional_categories": ";".join(row["institutional_categories"]),
            "institutional_terms": ";".join(row["institutional_terms"]),
            "review_flags": ";".join(review_flags),
            "readme_url": row["readme_url"],
            "proposal_from": row["proposal_from"],
            "implementation": row["implementation"],
            "readme_sha256": row["readme_sha256"],
            "commit_count": row["commit_count"],
            "last_file_commit": row["last_file_commit"],
            "last_file_commit_url": row["last_file_commit_url"],
            "requires": row["requires"],
            "dir": row["dir"],
            "relpath": row["relpath"],
            "front_author_root_labels": json.dumps(support["front_author_root_labels"], sort_keys=True),
            "institutional_snippets": json.dumps(row["institutional_snippets"], ensure_ascii=False),
        }
        detail = dict(flat)
        detail.update(
            {
                "authors_parsed": [identity.__dict__ for identity in row["authors"]],
                "support": support,
                "file_commits": path_commits[row["relpath"]][:20],
            }
        )
        rows.append(detail)

    rows.sort(key=lambda r: (r["xls_number"] if r["xls_number"] is not None else 999999, r["id"]))

    csv_columns = [
        "id",
        "xls_number",
        "title",
        "description",
        "category",
        "status",
        "created",
        "updated",
        "author_raw",
        "strict_support_tier",
        "broad_support_tier",
        "front_has_ripple",
        "front_has_explicit_xrpl_org",
        "front_has_external_xrp_author_evidence",
        "front_has_recurring_xls_author",
        "commit_has_ripple_or_explicit_xrpl_org",
        "maintainer_touch_tier",
        "institutional_categories",
        "institutional_terms",
        "review_flags",
        "readme_url",
        "proposal_from",
        "implementation",
        "readme_sha256",
        "commit_count",
        "last_file_commit",
        "last_file_commit_url",
        "requires",
        "dir",
        "relpath",
        "front_author_root_labels",
        "institutional_snippets",
    ]
    public_rows = [{k: row.get(k, "") for k in csv_columns} for row in rows]
    write_csv(artifact_dir / "xls_provenance.csv", public_rows, csv_columns)
    write_json(artifact_dir / "xls_provenance.json", rows)

    flagged = [
        row
        for row in public_rows
        if "institutional_surface_without_strict_xrp_author" in str(row["review_flags"])
    ]
    write_csv(artifact_dir / "institutional_surface_review.csv", flagged, csv_columns)
    no_direct = [
        row
        for row in public_rows
        if row["strict_support_tier"] == "NO_DIRECT_XRP_AUTHOR_SUPPORT"
    ]
    write_csv(artifact_dir / "no_direct_xrp_author_support.csv", no_direct, csv_columns)
    write_json(artifact_dir / "external_author_evidence.json", EXTERNAL_AUTHOR_EVIDENCE)

    author_registry: list[dict[str, Any]] = []
    for root in sorted({uf.find(key) for identity in all_identity_events for key in identity.keys}):
        author_registry.append(
            {
                "root": root,
                "classes": sorted(root_classes.get(root, set())),
                "proposal_count": author_proposal_counts[root],
                "has_final_proposal": root in final_author_roots,
                "evidence": sorted(set(root_evidence.get(root, [])))[:20],
            }
        )
    write_json(artifact_dir / "author_registry.json", author_registry)

    summary = {
        "generated_at": utc_now(),
        "source_repo": REPO_URL,
        "source_commit": commit,
        "source_commit_date": commit_date,
        "source_commit_subject": commit_subject,
        "source_commit_author": commit_author,
        "proposal_count": len(rows),
        "amendment_count": sum(1 for row in rows if row["category"].lower() == "amendment"),
        "strict_support_tiers": Counter(row["strict_support_tier"] for row in rows),
        "broad_support_tiers": Counter(row["broad_support_tier"] for row in rows),
        "amendment_strict_support_tiers": Counter(
            row["strict_support_tier"] for row in rows if row["category"].lower() == "amendment"
        ),
        "amendment_broad_support_tiers": Counter(
            row["broad_support_tier"] for row in rows if row["category"].lower() == "amendment"
        ),
        "status_counts": Counter(row["status"] for row in rows),
        "category_counts": Counter(row["category"] for row in rows),
        "institutional_surface_count": sum(1 for row in rows if row["institutional_categories"]),
        "institutional_surface_without_strict_xrp_author_count": len(flagged),
        "heuristic": {
            "strict_supported_by_xrp_author": [
                "DIRECT_RIPPLE_AUTHOR: a proposal front-matter author or propagated author identity has @ripple.com evidence in this frozen corpus/commit history.",
                "DIRECT_EXPLICIT_XRPL_ORG_AUTHOR: a proposal front-matter author or propagated identity has an explicit XRPL-org domain, currently xrpl-labs.com.",
                "DIRECT_EXTERNAL_XRP_AUTHOR_EVIDENCE: the front-matter author identity has an external URL tying it to Ripple, XRPL Labs, or XRP Ledger ecosystem development.",
                "NO_DIRECT_XRP_AUTHOR_SUPPORT: no direct front-matter author evidence under the strict rule.",
            ],
            "broad_supported_by_xrp_author": [
                "All strict-supported rows.",
                "DIRECT_RECURRING_XLS_AUTHOR: a proposal front-matter author identity appears on at least two XLS proposals or at least one Final XLS proposal. This is useful for XRP-native review, but weaker than email/org evidence.",
                "NO_BROAD_XRP_AUTHOR_SUPPORT: no direct strict support and no recurring-XLS-author support.",
            ],
            "not_counted_as_author_support": [
                "Institutional/compliance/SWIFT-like topic surface.",
                "A Ripple/XRPL maintainer touching the file without being a front-matter author.",
                "A proposal being Final.",
            ],
            "separate_maintainer_touch_column": "commit_has_ripple_or_explicit_xrpl_org records repository-history touch. It is evidence of review/edit path, not evidence that the listed proposal author is an XRP author.",
        },
    }
    write_json(artifact_dir / "summary.json", summary)

    def md_table(table_rows: list[dict[str, Any]], columns: list[str], limit: int = 25) -> str:
        shown = table_rows[:limit]
        if not shown:
            return "_None._\n"
        out = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
        for item in shown:
            vals = [str(item.get(col, "")).replace("\n", " ").replace("|", "\\|") for col in columns]
            out.append("| " + " | ".join(vals) + " |")
        if len(table_rows) > limit:
            out.append(f"\n_Truncated to {limit} of {len(table_rows)} rows._")
        return "\n".join(out) + "\n"

    report = f"""# XRPL XLS Provenance Report

Generated: {summary['generated_at']}

Frozen source: [`{commit}`]({github_commit_url(commit)}) from {REPO_URL}

Source date: {commit_date}

## Headline Counts

- Proposals parsed: {len(rows)}
- Amendment proposals parsed: {summary['amendment_count']}
- Strict direct XRP-author support: {sum(1 for row in rows if row['strict_support_tier'] != 'NO_DIRECT_XRP_AUTHOR_SUPPORT')}/{len(rows)}
- Strict direct XRP-author support, amendments only: {sum(1 for row in rows if row['category'].lower() == 'amendment' and row['strict_support_tier'] != 'NO_DIRECT_XRP_AUTHOR_SUPPORT')}/{summary['amendment_count']}
- Institutional/compliance/payment surface rows: {summary['institutional_surface_count']}
- Institutional surface rows without strict XRP-author support: {len(flagged)}

## Support Tiers

Strict support requires one of:

1. Ripple author evidence in the frozen corpus or commit history.
2. Explicit XRPL-org author evidence in the frozen corpus or commit history.
3. External URL evidence tying the listed author identity to Ripple, XRPL Labs, or XRP Ledger ecosystem development.

Broad support adds recurring XLS authorship. Broad support is useful for review, but the strict column is the one to use for the article's austere claim.

## Institutional Surface Without Strict XRP-Author Evidence

{md_table(flagged, ['id', 'title', 'category', 'status', 'author_raw', 'broad_support_tier', 'readme_url'])}

## All Rows Without Strict XRP-Author Evidence

{md_table(no_direct, ['id', 'title', 'category', 'status', 'author_raw', 'broad_support_tier', 'readme_url'])}

## Files

- `xls_provenance.csv`
- `xls_provenance.json`
- `institutional_surface_review.csv`
- `no_direct_xrp_author_support.csv`
- `author_registry.json`
- `external_author_evidence.json`
- `summary.json`
- `SHA256SUMS.txt`
"""
    (artifact_dir / "REPORT.md").write_text(report, encoding="utf-8")

    readme = f"""# XRPL XLS Provenance Packet

Generated: {summary['generated_at']}

Source: {REPO_URL}

Frozen commit: `{commit}`

Commit date: {commit_date}

Commit subject: {commit_subject}

## Files

- `xls_provenance.csv`: row-level table for every XLS proposal.
- `xls_provenance.json`: row-level table with parsed authors, support evidence, commit receipts, and snippets.
- `institutional_surface_review.csv`: subset where content has institutional/compliance/payment keywords and strict XRP-author support is weak or indirect.
- `no_direct_xrp_author_support.csv`: rows with no strict direct XRP-author support.
- `author_registry.json`: propagated identity roots and source-backed classes.
- `external_author_evidence.json`: manually curated external identity URLs used by the strict external-evidence tier.
- `REPORT.md`: human-readable summary.
- `summary.json`: counts and heuristic definition.
- `SHA256SUMS.txt`: hashes for packet files.

## Heuristic

Strict "supported by an XRP author" means direct front-matter author evidence for Ripple or an explicit XRPL organization. It does not count topic flavor, final status, or maintainer edits.

Broad support adds recurring XLS authors. This is useful for editorial review but weaker than direct org/email evidence.

The institutional surface review is only a cue for manual review. It does not mean the proposal is bad, fake, or unsupported.
"""
    (artifact_dir / "README.md").write_text(readme, encoding="utf-8")

    sha_lines = []
    for path in sorted(artifact_dir.iterdir()):
        if path.name == "SHA256SUMS.txt" or not path.is_file():
            continue
        sha_lines.append(f"{sha256_file(path)}  {path.name}")
    (artifact_dir / "SHA256SUMS.txt").write_text("\n".join(sha_lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--standards-dir", type=Path, default=DEFAULT_STANDARDS_DIR)
    parser.add_argument("--artifact-dir", type=Path, default=None)
    parser.add_argument("--fetch", action="store_true", help="Fetch and fast-forward the source checkout before freezing.")
    args = parser.parse_args()

    artifact_dir = args.artifact_dir
    if artifact_dir is None:
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        artifact_dir = DEFAULT_ARTIFACT_ROOT / f"xrpl-xls-provenance-{stamp}"
    build_packet(args.standards_dir, artifact_dir, args.fetch)
    print(artifact_dir)


if __name__ == "__main__":
    main()
