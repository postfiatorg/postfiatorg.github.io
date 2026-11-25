"""Link omitted L1 documentation and repository evidence to the exact checkout."""
import os
import posixpath
import re
import subprocess
from pathlib import PurePosixPath
from urllib.parse import parse_qsl, quote, unquote, urlencode, urlsplit, urlunsplit

from markdown import Markdown
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor


def source_heading_lines(source, extensions, configs):
    """Map the upstream Markdown processor's heading IDs to immutable source lines."""
    lines = source.splitlines()
    marked = []
    for i, line in enumerate(lines):
        # An empty inline element preserves the rendered heading text and slug.
        # Only markers inside actual TOC headings survive the Markdown parser.
        marker = f'<i data-l1-source-line="{i + 1}"></i>'
        atx = re.match(r"^(\s*#{1,6}\s*)", line)
        if atx:
            line = line[:atx.end()] + marker + line[atx.end():]
        elif line.strip() and i + 1 < len(lines) and re.fullmatch(r"\s*(?:=+|-+)\s*", lines[i + 1]):
            indent = len(line) - len(line.lstrip())
            line = line[:indent] + marker + line[indent:]
        marked.append(line)

    md = Markdown(extensions=extensions, extension_configs=configs)
    md.convert("\n".join(marked))
    headings = {}
    pending = list(md.toc_tokens)
    while pending:
        heading = pending.pop()
        match = re.search(r'<i data-l1-source-line="([0-9]+)"></i>', heading["html"])
        if match:
            headings[heading["id"]] = int(match[1])
        pending.extend(heading["children"])
    return headings


class EvidenceLinks(Extension):
    def __init__(self, repo, extensions, configs):
        super().__init__()
        self.repo = repo
        self.extensions = list(extensions)
        self.configs = configs
        self.heading_cache = {}
        self.revision = subprocess.check_output(["git", "-C", repo, "rev-parse", "HEAD"], text=True).strip()
        paths = subprocess.check_output(["git", "-C", repo, "ls-tree", "-r", "-z", "--name-only", self.revision])
        self.tracked = {PurePosixPath(os.fsdecode(path)) for path in paths.split(b"\0") if path}
        self.directories = {parent for path in self.tracked for parent in path.parents}

    def heading_lines(self, target):
        if target not in self.heading_cache:
            source = subprocess.check_output(
                ["git", "-C", self.repo, "show", f"{self.revision}:{target}"], encoding="utf-8"
            )
            self.heading_cache[target] = source_heading_lines(source, self.extensions, self.configs)
        return self.heading_cache[target]

    def destination(self, href):
        url = urlsplit(href)
        if url.scheme or url.netloc or not url.path or url.path.startswith("/"):
            return href
        rel = posixpath.normpath(posixpath.join(posixpath.dirname(self.page.file.src_uri), unquote(url.path)))
        file = self.files.get_file_from_path(rel)
        index = self.files.get_file_from_path(posixpath.join(rel, "index.md"))
        if (file and file.inclusion.is_included()) or (index and index.inclusion.is_included()):
            return href
        target = PurePosixPath(posixpath.normpath(posixpath.join("docs", rel)))
        if target in self.tracked:
            kind = "blob"
        elif target in self.directories and not file:
            kind = "tree"
        else:
            return href
        path = f"/postfiatorg/postfiatl1v2/{kind}/{self.revision}/{quote(str(target))}"
        query, fragment = url.query, url.fragment
        if kind == "blob" and target.suffix.lower() == ".md" and fragment:
            line = self.heading_lines(target).get(unquote(fragment))
            if line is None:
                raise ValueError(f"{self.page.file.src_uri}: unknown source heading {target}#{fragment}")
            params = [(key, value) for key, value in parse_qsl(query, keep_blank_values=True) if key != "plain"]
            query = urlencode([*params, ("plain", "1")])
            fragment = f"L{line}"
        return urlunsplit(("https", "github.com", path, query, fragment))

    def extendMarkdown(self, md):
        links = self

        class Resolve(Treeprocessor):
            def run(self, document):
                for element in document.iter("a"):
                    href = element.get("href")
                    if href:
                        element.set("href", links.destination(href))

        md.treeprocessors.register(Resolve(md), "l1_source_evidence", 2)


def on_config(config):
    global links
    links = EvidenceLinks(os.environ["POSTFIAT_L1_DOCS_CHECKOUT"], config.markdown_extensions, config.mdx_configs)
    config.markdown_extensions.append(links)


def on_page_markdown(markdown, page, config, files):
    links.page = page
    links.files = files
