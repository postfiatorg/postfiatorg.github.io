#!/usr/bin/env python3
"""Verify links from the Hugo docs hub and every published L1 article."""
from html.parser import HTMLParser
from pathlib import Path
import sys
from urllib.parse import unquote, urljoin, urlsplit

BASE = "https://postfiat.org"
PREFIX = "/docs/l1/"


class Page(HTMLParser):
    def __init__(self, hub=False):
        super().__init__()
        self.hub = hub
        self.article = False
        self.hrefs = []
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "article":
            self.article = True
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        if tag == "a" and (self.article or self.hub) and attrs.get("href"):
            self.hrefs.append(attrs["href"])

    def handle_endtag(self, tag):
        if tag == "article":
            self.article = False


def validate(public):
    site = public / "docs/l1"
    hub = public / "docs/index.html"
    pages = {}
    for path in [hub, *sorted(site.rglob("*.html"))]:
        page = Page(hub=path == hub)
        page.feed(path.read_text(encoding="utf-8"))
        pages[path] = page
    if len(pages) < 2 or not (site / "search/search_index.json").is_file():
        raise ValueError("Missing published L1 pages or search index")
    errors = set()
    checked = 0
    for source, page in pages.items():
        base = BASE + "/" + source.relative_to(public).as_posix()
        for href in page.hrefs:
            link = urlsplit(urljoin(base, href))
            if link.netloc != "postfiat.org" or not link.path.startswith(PREFIX):
                continue
            path = public / unquote(link.path).lstrip("/")
            if path.is_dir():
                path = path / "index.html"
            checked += 1
            if not path.is_file() or (link.fragment and path in pages
                                      and unquote(link.fragment) not in pages[path].ids):
                errors.add(f"{source.relative_to(public)} -> {href}")
    if not any(urlsplit(urljoin(BASE + "/docs/", href)).path.startswith(PREFIX) for href in pages[hub].hrefs):
        errors.add("Docs hub has no L1 links")
    for error in sorted(errors):
        print(error, file=sys.stderr)
    print(f"{len(pages)-1} L1 HTML files, {checked} internal link references, {len(errors)} invalid")
    return not errors


if __name__ == "__main__":
    sys.exit(0 if validate(Path(sys.argv[1] if len(sys.argv) > 1 else "public")) else 1)
