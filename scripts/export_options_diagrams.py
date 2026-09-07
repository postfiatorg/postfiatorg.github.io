"""Export the article's rendered figures for Markdown and Copy for LLM readers.

Build Hugo, serve public/ locally, run this script, then rebuild to include PNGs.
The live article keeps its responsive HTML and interactive verification figure.
"""
from argparse import ArgumentParser
from hashlib import sha256
from pathlib import Path
import json

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8772")
    parser.add_argument("--browser", default="/usr/bin/google-chrome")
    args = parser.parse_args()
    metadata = json.loads((ROOT / "data/options_tee_diagrams.json").read_text())
    output = ROOT / "static/research/options-tee-indices/figures"
    output.mkdir(exist_ok=True)
    manifest = {"source": "Responsive article figures rendered at 1280px, device scale 2", "figures": {}}
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=args.browser, headless=True, args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1280, "height": 960}, device_scale_factor=2)
        page.goto(args.base_url.rstrip("/") + "/blog/trustless-single-stock-option-indices/", wait_until="networkidle")
        page.evaluate("document.fonts.ready")
        assert page.locator("figure.ot-figure").count() == len(metadata)
        for kind, record in metadata.items():
            figure = page.locator(f"#ot-{kind}")
            assert figure.count() == 1
            assert figure.locator(".ot-heading h3").inner_text() == record["title"]
            assert figure.evaluate("el => el.scrollWidth <= el.clientWidth + 1")
            figure.scroll_into_view_if_needed()
            for img in figure.locator("img").all():
                img.evaluate("el => el.decode()")
            target = output / f"{kind}.png"
            figure.screenshot(path=str(target), animations="disabled", style=".site-header { visibility: hidden !important; }")
            manifest["figures"][kind] = {"file": target.name, "sha256": sha256(target.read_bytes()).hexdigest(), "title": record["title"]}
        browser.close()
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Exported {len(metadata)} article figures to {output}")


if __name__ == "__main__":
    main()
