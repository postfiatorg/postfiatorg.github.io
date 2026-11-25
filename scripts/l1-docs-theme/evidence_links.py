"""Link omitted L1 documentation and repository evidence to the exact checkout."""
import os
import posixpath
import subprocess
from pathlib import PurePosixPath
from urllib.parse import quote, unquote, urlsplit, urlunsplit

from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor


class EvidenceLinks(Extension):
    def __init__(self, repo):
        super().__init__()
        self.revision = subprocess.check_output(["git", "-C", repo, "rev-parse", "HEAD"], text=True).strip()
        paths = subprocess.check_output(["git", "-C", repo, "ls-tree", "-r", "-z", "--name-only", self.revision])
        self.tracked = {PurePosixPath(os.fsdecode(path)) for path in paths.split(b"\0") if path}
        self.directories = {parent for path in self.tracked for parent in path.parents}

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
        return urlunsplit(("https", "github.com", path, url.query, url.fragment))

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
    links = EvidenceLinks(os.environ["POSTFIAT_L1_DOCS_CHECKOUT"])
    config.markdown_extensions.append(links)


def on_page_markdown(markdown, page, config, files):
    links.page = page
    links.files = files
