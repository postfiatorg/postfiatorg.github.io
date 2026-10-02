"""Capture rendered pages for critique: full-page screenshots, viewport frames and a scroll video.

Usage:
  capture.py --base http://127.0.0.1:8137 --out runs/<tag> --pages / /whitepaper/ ...
"""
import argparse
import json
import subprocess
from pathlib import Path

from playwright.sync_api import sync_playwright

VIEWPORTS = {"desktop": (1440, 900), "mobile": (390, 844)}


def slug(path: str) -> str:
    s = path.strip("/").replace("/", "__")
    return s or "home"


def capture_page(browser, base, path, out: Path, video: bool):
    rec = {"path": path, "shots": {}}
    for name, (w, h) in VIEWPORTS.items():
        ctx_kwargs = {"viewport": {"width": w, "height": h}, "device_scale_factor": 1}
        if video and name == "desktop":
            ctx_kwargs["record_video_dir"] = str(out / "video_tmp")
            ctx_kwargs["record_video_size"] = {"width": w, "height": h}
        ctx = browser.new_context(**ctx_kwargs)
        page = ctx.new_page()
        console_errors = []
        page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)
        page.goto(base + path, wait_until="networkidle", timeout=60000)
        page.add_style_tag(content="html{scroll-behavior:auto!important}")
        page.wait_for_timeout(1200)
        # Dismiss cookie/consent banners so judges see the site, not the banner.
        for label in ("Deny", "Reject all", "Reject", "Decline", "Allow all", "Accept all", "Accept", "I agree", "Got it"):
            btn = page.get_by_role("button", name=label, exact=True)
            if btn.count():
                try:
                    btn.first.click(timeout=2000)
                    page.wait_for_timeout(800)
                    break
                except Exception:
                    pass
        # Walk the page once so lazy-loaded and scroll-triggered content renders before capture.
        h0 = page.evaluate("document.documentElement.scrollHeight")
        for y in range(0, h0, 600):
            page.evaluate(f"window.scrollTo({{top:{y},behavior:'instant'}})")
            page.wait_for_timeout(150)
        page.evaluate("window.scrollTo({top:0,behavior:'instant'})")
        page.wait_for_timeout(600)
        if name == "desktop":
            (out / f"{slug(path)}.text.txt").write_text(page.inner_text("body"))
        full = out / f"{slug(path)}.{name}.full.png"
        page.screenshot(path=str(full), full_page=True)
        height = page.evaluate("document.documentElement.scrollHeight")
        # Viewport frames down the page: what a visitor actually sees screen by screen.
        frames = []
        for i, y in enumerate(range(0, max(height - h, 0) + 1, int(h * 0.9))):
            if i >= 8:
                break
            page.evaluate(f"window.scrollTo({{top:{y},behavior:'instant'}})")
            page.wait_for_timeout(500 if video else 250)
            f = out / f"{slug(path)}.{name}.frame{i:02d}.png"
            page.screenshot(path=str(f))
            frames.append(f.name)
        overflow = page.evaluate(
            "document.documentElement.scrollWidth > document.documentElement.clientWidth"
        )
        offenders = page.evaluate("""() => { const W = document.documentElement.clientWidth; const out = [];
          for (const el of document.querySelectorAll('body *')) { const r = el.getBoundingClientRect();
            if (r.right > W + 1 && r.width > 0 && getComputedStyle(el).position !== 'fixed') {
              let p = el.parentElement, clipped = false;
              while (p) { const o = getComputedStyle(p).overflowX; if (o === 'auto' || o === 'scroll' || o === 'hidden') { clipped = true; break; } p = p.parentElement; }
              if (!clipped) out.push(el.tagName.toLowerCase() + (el.className && typeof el.className === 'string' ? '.' + el.className.split(' ').join('.') : '') + ' w=' + Math.round(r.width) + ' "' + (el.textContent || '').trim().slice(0, 50) + '"'); } }
          return out.slice(0, 8); }""") if overflow else []
        rec["shots"][name] = {
            "full": full.name,
            "frames": frames,
            "height": height,
            "horizontal_overflow": overflow,
            "overflow_offenders": offenders,
            "console_errors": console_errors[:10],
        }
        vid = page.video
        ctx.close()
        if vid:
            src = Path(vid.path())
            mp4 = out / f"{slug(path)}.desktop.scroll.mp4"
            subprocess.run(
                ["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-c:v", "libx264", "-pix_fmt", "yuv420p", str(mp4)],
                check=False,
            )
            src.unlink(missing_ok=True)
            rec["video"] = mp4.name
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--pages", nargs="+", default=["/"])
    ap.add_argument("--video", action="store_true")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path="/usr/bin/google-chrome")
        manifest = [capture_page(browser, a.base.rstrip("/"), path, out, a.video) for path in a.pages]
        browser.close()
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
