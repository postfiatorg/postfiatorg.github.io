#!/usr/bin/env python3
"""Verify every /docs/l1/... link rendered on /docs/ resolves to a built MkDocs HTML page."""

from __future__ import annotations

import html.parser
import sys
from pathlib import Path
from urllib.parse import urlsplit


class LinkExtractor(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "a":
            for k, v in attrs:
                if k == "href" and v:
                    self.hrefs.append(v)


def main() -> int:
    public_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("public")
    docs_index = public_dir / "docs" / "index.html"
    if not docs_index.is_file():
        print(f"FAIL: missing {docs_index}", file=sys.stderr)
        return 1

    parser = LinkExtractor()
    parser.feed(docs_index.read_text(encoding="utf-8"))

    checked = 0
    missing: list[str] = []
    seen: set[str] = set()
    for href in parser.hrefs:
        path = urlsplit(href).path
        if not path.startswith("/docs/l1/"):
            continue
        if path in seen:
            continue
        seen.add(path)
        checked += 1
        rel = path.lstrip("/")
        target = public_dir / rel
        if target.is_dir():
            target = target / "index.html"
        elif not target.exists() and not rel.endswith(".html"):
            target = public_dir / rel / "index.html"
        if not target.is_file():
            missing.append(f"{path} -> {target}")

    if checked == 0:
        print("FAIL: no /docs/l1/ links found in /docs/index.html", file=sys.stderr)
        return 1
    if missing:
        print("FAIL: broken /docs/l1/ links found:", file=sys.stderr)
        for item in missing:
            print(f"  - {item}", file=sys.stderr)
        return 1

    search_idx = public_dir / "docs" / "l1" / "search" / "search_index.json"
    if not search_idx.is_file():
        print(f"FAIL: missing MkDocs search index at {search_idx}", file=sys.stderr)
        return 1

    print(f"OK: {checked} unique /docs/l1/ links verified in {docs_index}; MkDocs search index present ({search_idx.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
