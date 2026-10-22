#!/usr/bin/env python3
"""Mirror the Coinbase listing documents from postfiatl1v2 into content/listings/coinbase/.

The three source documents live in the L1 repository at
docs/listings/coinbase/{integration-plan,comparisons,reviewer-agent-guide}.md.
Each becomes a Hugo page with provenance front matter (source repo, path,
commit, branch). Relative repository links are rewritten to absolute GitHub
links at --ref, links to the whitepaper and to the other mirrored documents
point at their postfiat.org pages, and MkDocs admonitions become notices.

The page summary comes from the source front matter (summary or description)
when present, otherwise from the curated summary in DOCS below.

A document that does not exist yet in the source checkout is written as a
clearly marked placeholder, so the site always builds.

The script is idempotent: a page is only rewritten when its content changes.
Run it again whenever the source documents change, ideally against a checkout
of postfiatl1v2 main once they are merged, so that source_commit is a commit
GitHub serves.

Usage:
  python3 scripts/sync_listings_docs.py
  python3 scripts/sync_listings_docs.py --source ../postfiatl1v2 --ref main
  python3 scripts/sync_listings_docs.py --check   # report only; exit 1 if pages would change
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import posixpath
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = REPO_ROOT.parent / "postfiatl1v2-coinbase-listing-20261022"
OUT_DIR = REPO_ROOT / "content" / "listings" / "coinbase"
LANDING = REPO_ROOT / "content" / "listings" / "_index.md"

SOURCE_REPO = "postfiatorg/postfiatl1v2"
GITHUB = f"https://github.com/{SOURCE_REPO}"
RAW = f"https://raw.githubusercontent.com/{SOURCE_REPO}"
PUBLIC_REMOTE_RE = re.compile(r"github\.com[:/]postfiatorg/postfiatl1v2(?:\.git)?/?$")

PLACEHOLDER_LINE = "In review — published with the integration plan."

DOCS = [
    {
        "slug": "integration-plan",
        "source": "docs/listings/coinbase/integration-plan.md",
        "weight": 10,
        "title": "Coinbase integration plan",
        "summary": "The proposed plan for Coinbase to support Post Fiat L1 (PFTL), with its dependencies and open items stated.",
        "aliases": ["/listings/coinbase/"],
    },
    {
        "slug": "comparisons",
        "source": "docs/listings/coinbase/comparisons.md",
        "weight": 20,
        "title": "PFTL compared with XRP, Zcash and post-quantum chains",
        "summary": "How Post Fiat L1 compares with XRP, Zcash and post-quantum chains, feature by feature.",
        "aliases": [],
    },
    {
        "slug": "reviewer-agent-guide",
        "source": "docs/listings/coinbase/reviewer-agent-guide.md",
        "weight": 30,
        "title": "Reviewer agent guide",
        "summary": "Instructions for an AI agent reviewing Post Fiat L1: what to read, what to check and what not to assume.",
        "aliases": [],
    },
]

# Repository files that have their own page on postfiat.org.
SITE_PAGES = {
    "docs/whitepaper.md": "/whitepaper/",
    "docs/whitepaper_legacy.md": "/whitepaper/legacy-governance/",
    **{doc["source"]: f"/listings/coinbase/{doc['slug']}/" for doc in DOCS},
}

FENCE_RE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
CODE_SPAN_RE = re.compile(r"(`+)(?:.+?)\1")
INLINE_LINK_RE = re.compile(
    r"(?P<bang>!?)\[(?P<text>(?:[^\[\]]|\[[^\[\]]*\])*)\]\(\s*(?P<target><[^>]*>|[^\s()]+(?:\([^\s()]*\)[^\s()]*)*)(?P<title>\s+(?:\"[^\"]*\"|'[^']*'|\([^)]*\)))?\s*\)"
)
REF_DEF_RE = re.compile(r"^(?P<lead>\s{0,3}\[[^\]]+\]:\s*)(?P<target><[^>]*>|\S+)(?P<rest>.*)$")
HTML_ATTR_RE = re.compile(r"(?P<attr>\b(?:href|src))=(?P<q>[\"'])(?P<target>[^\"']*)(?P=q)")
SCHEME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")
ADMONITION_RE = re.compile(r"^(?P<indent>\s*)(?:!!!|\?\?\?\+?)\s+(?P<kind>[\w-]+)(?:\s+\"(?P<title>[^\"]*)\")?\s*$")
H1_RE = re.compile(r"^#\s+(?P<title>.+?)\s*#*\s*$")


def git(source: Path, *args: str, check: bool = True) -> str:
    result = subprocess.run(["git", "-C", str(source), *args], capture_output=True, text=True)
    if check and result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed in {source}: {result.stderr.strip()}")
    return result.stdout.strip() if result.returncode == 0 else ""


def public_remote(source: Path) -> str | None:
    for line in git(source, "remote", "-v", check=False).splitlines():
        parts = line.split()
        if len(parts) >= 2 and PUBLIC_REMOTE_RE.search(parts[1]):
            return parts[0]
    return None


def existing_paths(source: Path, treeish: str, paths: set[str]) -> set[str]:
    """Return the subset of paths that exist (as blob or tree) at treeish."""
    if not paths:
        return set()
    ordered = sorted(paths)
    query = "".join(f"{treeish}:{p}\n" for p in ordered)
    result = subprocess.run(
        ["git", "-C", str(source), "cat-file", "--batch-check"], input=query, capture_output=True, text=True
    )
    found = set()
    for path, line in zip(ordered, result.stdout.splitlines()):
        if not line.endswith("missing"):
            found.add(path)
    return found


def yaml_str(value: str) -> str:
    # JSON strings are valid YAML double-quoted scalars.
    return json.dumps(value, ensure_ascii=False)


def plain_text(markdown: str) -> str:
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", markdown)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\[[^\]]*\]", r"\1", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"[`*_]{1,3}", "", text)
    return re.sub(r"\s+", " ", text).strip()


def truncate(text: str, limit: int = 240) -> str:
    if len(text) <= limit:
        return text
    cut = text[:limit]
    sentence = max(cut.rfind(". "), cut.rfind("; "))
    if sentence > limit // 2:
        return cut[: sentence + 1]
    return cut[: cut.rfind(" ")].rstrip(",;:") + "…"


class Rewriter:
    """Rewrites repository-relative links in one source document."""

    def __init__(self, source: Path, source_path: str, ref: str):
        self.source = source
        self.base_dir = posixpath.dirname(source_path)
        self.ref = ref
        self.github_targets: set[str] = set()
        self.site_links: set[str] = set()
        self.escaped: list[str] = []
        self.count = 0

    def target(self, raw: str, image: bool, text: str = "") -> str:
        angle = raw.startswith("<") and raw.endswith(">")
        target = raw[1:-1] if angle else raw
        if not target or target.startswith("#") or target.startswith("//") or SCHEME_RE.match(target):
            return raw
        path, frag = (target.split("#", 1) + [""])[:2]
        path, query = (path.split("?", 1) + [""])[:2]
        if not path:
            return raw
        repo_path = path.lstrip("/") if path.startswith("/") else posixpath.normpath(posixpath.join(self.base_dir, path))
        if repo_path == ".." or repo_path.startswith("../"):
            self.escaped.append(target)
            return raw
        frag = f"#{frag}" if frag else ""
        query = f"?{query}" if query else ""
        self.count += 1
        # A link labelled "source" asks for the repository file, not the site page.
        if repo_path in SITE_PAGES and not image and not plain_text(text).lower().startswith("source"):
            self.site_links.add(repo_path)
            return SITE_PAGES[repo_path] + frag
        self.github_targets.add(repo_path)
        encoded = quote(repo_path, safe="/-_.~")
        if image:
            return f"{RAW}/{self.ref}/{encoded}"
        kind = "tree" if path.endswith("/") or (self.source / repo_path).is_dir() else "blob"
        return f"{GITHUB}/{kind}/{self.ref}/{encoded}{query}{frag}"

    def inline(self, segment: str) -> str:
        segment = INLINE_LINK_RE.sub(
            lambda m: f"{m['bang']}[{m['text']}]({self.target(m['target'], bool(m['bang']), m['text'])}{m['title'] or ''})",
            segment,
        )
        return HTML_ATTR_RE.sub(
            lambda m: f"{m['attr']}={m['q']}{self.target(m['target'], m['attr'] == 'src')}{m['q']}", segment
        )

    def line(self, line: str) -> str:
        ref = REF_DEF_RE.match(line)
        if ref:
            target = ref["target"]
            image = bool(re.search(r"\.(?:png|jpe?g|gif|svg|webp)$", target.strip("<>"), re.I))
            return f"{ref['lead']}{self.target(target, image)}{ref['rest']}"
        out, pos = [], 0
        for span in CODE_SPAN_RE.finditer(line):
            out.append(self.inline(line[pos : span.start()]))
            out.append(span.group(0))
            pos = span.end()
        out.append(self.inline(line[pos:]))
        return "".join(out)


def split_front_matter(text: str) -> tuple[dict, str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---", 4)
    if end < 0:
        return {}, text
    block, body = text[4:end], text[end + 4 :].lstrip("\n")
    try:
        import yaml  # type: ignore

        data = yaml.safe_load(block) or {}
        return (data if isinstance(data, dict) else {}), body
    except Exception:
        return {}, body


def convert_body(lines: list[str], rewriter: Rewriter) -> tuple[str | None, list[str]]:
    """Rewrite links, convert admonitions, and remove the first H1 (returned as the title)."""
    title = None
    out: list[str] = []
    fence = None
    admonition_indent = None
    for line in lines:
        if admonition_indent is not None:
            if line.strip() == "":
                if fence or out[-1] != "":
                    out.append("")
                continue
            if line.startswith(admonition_indent + "    "):
                line = admonition_indent + line[len(admonition_indent) + 4 :]
            else:
                while out and out[-1] == "":
                    out.pop()
                out.extend(["", "</div>", ""])
                admonition_indent = None
        marker = FENCE_RE.match(line)
        if fence:
            out.append(line)
            if marker and marker.group(1)[0] == fence[0] and len(marker.group(1)) >= len(fence) and not line.strip()[len(marker.group(1)):].strip():
                fence = None
            continue
        if marker:
            fence = marker.group(1)
            out.append(line)
            continue
        if title is None:
            heading = H1_RE.match(line)
            if heading:
                title = plain_text(heading["title"])
                continue
        adm = ADMONITION_RE.match(line)
        if adm and admonition_indent is None:
            label = adm["title"] if adm["title"] is not None else adm["kind"].replace("-", " ").capitalize()
            label_html = f'<span class="label">{label}</span>' if label else ""
            out.extend([f'<div class="notice">{label_html}', ""])
            admonition_indent = adm["indent"]
            continue
        out.append(rewriter.line(line))
    if admonition_indent is not None:
        while out and out[-1] == "":
            out.pop()
        out.extend(["", "</div>"])
    while out and out[0].strip() == "":
        out.pop(0)
    while out and out[-1].strip() == "":
        out.pop()
    return title, out


def front_matter(doc: dict, *, title: str, summary: str, status: str, prov: dict, ref: str, date: str | None) -> str:
    lines = [
        "---",
        "# Generated by scripts/sync_listings_docs.py. Edit the source document in",
        f"# {SOURCE_REPO} and re-run the script; local edits here are overwritten.",
        f"title: {yaml_str(title)}",
        f"url: {yaml_str('/listings/coinbase/' + doc['slug'] + '/')}",
        f"summary: {yaml_str(summary)}",
        f"weight: {doc['weight']}",
        'kicker: "Coinbase"',
        'listing: "coinbase"',
        f"status: {yaml_str(status)}",
        f"source_repo: {yaml_str(SOURCE_REPO)}",
        f"source_path: {yaml_str(doc['source'])}",
        f"source_commit: {yaml_str(prov['commit'])}",
        f"source_branch: {yaml_str(prov['branch'])}",
    ]
    if prov.get("dirty"):
        lines.append("source_dirty: true")
    lines.append(f"links_ref: {yaml_str(ref)}")
    if date:
        lines += [f"date: {date}", f"lastmod: {date}"]
    if doc["aliases"]:
        lines.append("aliases: [" + ", ".join(yaml_str(a) for a in doc["aliases"]) + "]")
    lines.append("---")
    return "\n".join(lines) + "\n"


def placeholder_body(doc: dict) -> str:
    return (
        f"**{PLACEHOLDER_LINE}**\n\n"
        f"This page will mirror `{doc['source']}` from [{SOURCE_REPO}]({GITHUB}) once the document is published. "
        "Until then, read the [whitepaper](/whitepaper/), the [status ledger](/listings/#status) "
        "and the [key design documents](/listings/#design-docs).\n"
    )


def file_date(source: Path, rel: str, dirty: bool) -> str:
    if not dirty:
        committed = git(source, "log", "-1", "--format=%cs", "--", rel, check=False)
        if committed:
            return committed
    mtime = (source / rel).stat().st_mtime
    return dt.datetime.fromtimestamp(mtime, dt.timezone.utc).date().isoformat()


def landing_design_docs() -> list[str]:
    try:
        import yaml  # type: ignore
    except ImportError:
        return []
    text = LANDING.read_text(encoding="utf-8") if LANDING.exists() else ""
    data, _ = split_front_matter(text)
    return [d["path"] for d in data.get("design_docs", []) if isinstance(d, dict) and d.get("path")]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE, help=f"postfiatl1v2 checkout (default: {DEFAULT_SOURCE})")
    parser.add_argument("--ref", default="main", help="Git ref used in rewritten GitHub links (default: main)")
    parser.add_argument("--check", action="store_true", help="Report what would change without writing; exit 1 if anything would")
    args = parser.parse_args()

    source = args.source.expanduser().resolve()
    if not (source / ".git").exists():
        print(f"error: {source} is not a git checkout of {SOURCE_REPO}", file=sys.stderr)
        return 2

    commit = git(source, "rev-parse", "--short", "HEAD")
    branch = git(source, "rev-parse", "--abbrev-ref", "HEAD")
    branch = "detached" if branch == "HEAD" else branch
    remote = public_remote(source)
    remote_ref = f"{remote}/{args.ref}" if remote else None
    if remote_ref and not git(source, "rev-parse", "--verify", "-q", remote_ref, check=False):
        remote_ref = None
    print(f"source   {source}")
    print(f"commit   {commit} on {branch}")
    print(f"links    {GITHUB}/blob/{args.ref}/…")

    warnings: list[str] = []
    if remote:
        on_remote = git(source, "branch", "-r", "--contains", "HEAD", check=False).split()
        if not any(name.startswith(f"{remote}/") for name in on_remote):
            warnings.append(
                f"source commit {commit} is not on any {remote}/* branch yet; GitHub source links on the mirrored pages "
                "will 404 until it is pushed (re-run against merged main before deploying)"
            )
    else:
        warnings.append(f"no remote for github.com/{SOURCE_REPO} in {source}; link targets not verified against GitHub")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    changed = 0
    all_targets: dict[str, set[str]] = {}
    for doc in DOCS:
        rel = doc["source"]
        out_path = OUT_DIR / f"{doc['slug']}.md"
        src_file = source / rel
        prov = {"commit": commit, "branch": branch}
        if src_file.is_file():
            dirty = bool(git(source, "status", "--porcelain", "--", rel, check=False))
            prov["dirty"] = dirty
            if dirty:
                warnings.append(f"{rel} has uncommitted changes; source_commit {commit} does not contain this text")
            meta, body = split_front_matter(src_file.read_text(encoding="utf-8"))
            rewriter = Rewriter(source, rel, args.ref)
            h1, lines = convert_body(body.splitlines(), rewriter)
            title = str(meta.get("title") or h1 or doc["title"])
            summary = truncate(plain_text(str(meta.get("summary") or meta.get("description") or doc["summary"])))
            content = front_matter(
                doc, title=title, summary=summary, status="published", prov=prov, ref=args.ref,
                date=file_date(source, rel, dirty),
            ) + "\n" + "\n".join(lines) + "\n"
            all_targets[rel] = rewriter.github_targets
            for target in rewriter.escaped:
                warnings.append(f"{rel}: link {target!r} points outside the repository; left unchanged")
            detail = f"mirrored, {rewriter.count} links rewritten ({len(rewriter.github_targets)} GitHub, {len(rewriter.site_links)} site)"
        else:
            content = front_matter(
                doc, title=doc["title"], summary=doc["summary"], status="in-review", prov=prov, ref=args.ref, date=None,
            ) + "\n" + placeholder_body(doc)
            detail = "placeholder (source document not found)"

        previous = out_path.read_text(encoding="utf-8") if out_path.exists() else None
        if previous == content:
            action = "unchanged"
        else:
            action = "would write" if args.check else ("updated" if previous is not None else "created")
            changed += 1
            if not args.check:
                out_path.write_text(content, encoding="utf-8")
        print(f"{action:<11} {out_path.relative_to(REPO_ROOT)}  <- {rel}: {detail}")

    if remote_ref:
        verified = git(source, "rev-parse", "--short", remote_ref)
        for rel, targets in all_targets.items():
            missing = targets - existing_paths(source, remote_ref, targets)
            for path in sorted(missing):
                warnings.append(f"{rel}: link target {path} does not exist at {remote_ref} ({verified})")
        design = set(landing_design_docs())
        if design:
            missing = design - existing_paths(source, remote_ref, design)
            print(f"checked  {len(design)} key design documents in content/listings/_index.md at {remote_ref} ({verified}): "
                  f"{len(design) - len(missing)} present")
            for path in sorted(missing):
                warnings.append(f"key design document {path} does not exist at {remote_ref} ({verified})")

    for warning in warnings:
        print(f"warning  {warning}")
    print(f"done     {changed} page(s) {'would change' if args.check else 'written'}, {len(DOCS) - changed} unchanged")
    return 1 if (args.check and changed) else 0


if __name__ == "__main__":
    sys.exit(main())
