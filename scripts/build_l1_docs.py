#!/usr/bin/env python3
"""Build the postfiatl1v2 MkDocs Material site into postfiat.org's /docs/l1/ directory.

Uses MkDocs' native `INHERIT: mkdocs.yml` overlay so every navigation item,
markdown extension, redaction exclusion, and upstream page stays synced with
postfiatorg/postfiatl1v2 without duplicating markdown files into this repo.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
THEME_DIR = Path(__file__).resolve().parent / "l1-docs-theme"
DEFAULT_REPO_URL = "https://github.com/postfiatorg/postfiatl1v2.git"
DEFAULT_SITE_URL = "https://postfiat.org/docs/l1/"


def extract_yaml_list(mkdocs_text: str, key: str) -> list[str]:
    """Extract a simple top-level YAML list (e.g. extra_css) without needing custom YAML tag loaders."""
    items: list[str] = []
    in_block = False
    for line in mkdocs_text.splitlines():
        if re.match(rf"^{re.escape(key)}:\s*$", line):
            in_block = True
            continue
        if in_block:
            if line and not line[0].isspace():
                break
            m = re.match(r"^\s*-\s+(.+?)\s*$", line)
            if m:
                items.append(m.group(1).strip().strip("'\""))
    return items


def run(cmd: list[str], cwd: Path, env: dict[str, str] | None = None) -> None:
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, cwd=str(cwd), env=env, check=True)


def build(l1_dir: Path, out_dir: Path, site_url: str, skip_evidence_index: bool = False) -> None:
    l1_dir = l1_dir.resolve()
    out_dir = out_dir.resolve()
    mkdocs_yml = l1_dir / "mkdocs.yml"
    if not mkdocs_yml.is_file():
        raise FileNotFoundError(f"Missing mkdocs.yml in {l1_dir}")

    # Copy postfiatl1v2 docs inputs into an isolated staging dir so we never mutate l1_dir.
    with tempfile.TemporaryDirectory(prefix="postfiat-l1-docs-") as tmp:
        stage = Path(tmp) / "l1"
        stage.mkdir(parents=True)

        for name in ("mkdocs.yml", "docs", "docs_site", "scripts", "reports", "benchmarks"):
            src = l1_dir / name
            if not src.exists():
                continue
            dst = stage / name
            if name in ("docs", "docs_site", "mkdocs.yml"):
                if src.is_dir():
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)
            else:
                # Symlink read-only supporting dirs so scripts/docs-site-evidence-index works fast
                dst.symlink_to(src)

        if not skip_evidence_index and (stage / "scripts" / "docs-site-evidence-index").exists():
            run(["bash", str(stage / "scripts" / "docs-site-evidence-index")], cwd=stage)

        # Copy Post Fiat Ink overlay assets into staged docs/assets/
        css_dst = stage / "docs" / "assets" / "stylesheets" / "postfiat-ink.css"
        js_dst = stage / "docs" / "assets" / "javascripts" / "postfiat-ink.js"
        css_dst.parent.mkdir(parents=True, exist_ok=True)
        js_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(THEME_DIR / "postfiat-ink.css", css_dst)
        shutil.copy2(THEME_DIR / "postfiat-ink.js", js_dst)

        overrides_dst = stage / "_postfiat_overrides"
        shutil.copytree(THEME_DIR / "overrides", overrides_dst)

        base_text = (stage / "mkdocs.yml").read_text(encoding="utf-8")
        extra_css = extract_yaml_list(base_text, "extra_css")
        extra_js = extract_yaml_list(base_text, "extra_javascript")
        if "assets/stylesheets/postfiat-ink.css" not in extra_css:
            extra_css.append("assets/stylesheets/postfiat-ink.css")
        if "assets/javascripts/postfiat-ink.js" not in extra_js:
            extra_js.append("assets/javascripts/postfiat-ink.js")

        overlay_lines = [
            "INHERIT: mkdocs.yml",
            "site_name: Post Fiat L1 Docs",
            f"site_url: {site_url}",
            "theme:",
            f"  custom_dir: {overrides_dst.name}",
            "extra_css:",
            *[f"  - {item}" for item in extra_css],
            "extra_javascript:",
            *[f"  - {item}" for item in extra_js],
            "",
        ]
        overlay_yml = stage / "mkdocs.postfiat-org.yml"
        overlay_yml.write_text("\n".join(overlay_lines), encoding="utf-8")

        if out_dir.exists():
            shutil.rmtree(out_dir)
        out_dir.parent.mkdir(parents=True, exist_ok=True)

        env = os.environ.copy()
        env["POSTFIAT_DOCS_SITE_URL"] = site_url
        mkdocs_bin = shutil.which("mkdocs") or sys.executable
        if mkdocs_bin == sys.executable:
            cmd = [sys.executable, "-m", "mkdocs", "build", "--strict", "-f", str(overlay_yml), "-d", str(out_dir)]
        else:
            cmd = [mkdocs_bin, "build", "--strict", "-f", str(overlay_yml), "-d", str(out_dir)]
        run(cmd, cwd=stage, env=env)

    html_count = sum(1 for _ in out_dir.rglob("*.html"))
    print(f"Built Post Fiat L1 MkDocs site: {html_count} HTML pages -> {out_dir}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--l1-dir", type=Path, help="Existing postfiatl1v2 checkout directory")
    parser.add_argument("--repo-url", default=DEFAULT_REPO_URL, help="Git URL to clone when --l1-dir is omitted")
    parser.add_argument("--ref", default="main", help="Branch/ref to clone when --l1-dir is omitted")
    parser.add_argument("--out-dir", type=Path, default=REPO_ROOT / "public" / "docs" / "l1", help="Output directory")
    parser.add_argument("--site-url", default=DEFAULT_SITE_URL, help="Published MkDocs site_url")
    parser.add_argument("--skip-evidence-index", action="store_true", help="Skip regenerating docs_site/evidence/index.md")
    args = parser.parse_args()

    if args.l1_dir is not None:
        build(args.l1_dir, args.out_dir, args.site_url, args.skip_evidence_index)
        return 0

    with tempfile.TemporaryDirectory(prefix="postfiat-l1-clone-") as tmp:
        clone_dir = Path(tmp) / "postfiatl1v2"
        run(["git", "clone", "--depth", "1", "--branch", args.ref, args.repo_url, str(clone_dir)], cwd=Path(tmp))
        build(clone_dir, args.out_dir, args.site_url, args.skip_evidence_index)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
