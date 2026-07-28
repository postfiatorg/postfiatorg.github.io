#!/usr/bin/env python3
from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import math
import os
import re
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageStat


HOOKS = [
    "primary-cta",
    "install-panel",
    "copy-command",
    "copy-success",
    "orchestration-control",
    "orchestration-state",
    "mobile-menu",
    "mobile-menu-panel",
]
REMOTE_ASSET = re.compile(
    r"""(?:src|href)\s*=\s*["'](?:https?:)?//|url\(\s*["']?(?:https?:)?//""",
    re.IGNORECASE,
)
SECRET_PATTERN = re.compile(
    r"(?:sk-ant-|sk-proj-|sk-[A-Za-z0-9_-]{20,}|ANTHROPIC_API_KEY\s*=\s*['\"][^$])"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_manifest(root: Path) -> tuple[Path | None, list[dict[str, Any]]]:
    candidates = sorted(root.rglob("image_manifest.json"))
    if not candidates:
        return None, []
    path = candidates[0]
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return path, []
    if isinstance(payload, list):
        entries = payload
    elif isinstance(payload, dict):
        entries = payload.get("images") or payload.get("generated_images") or []
    else:
        entries = []
    return path, [item for item in entries if isinstance(item, dict)]


def resolve_image(root: Path, manifest_path: Path, name: str) -> Path | None:
    raw = Path(name)
    candidates = [
        root / raw,
        manifest_path.parent / raw,
        root / "assets" / "generated" / raw.name,
        root / "public" / "assets" / "generated" / raw.name,
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    return None


def static_checks(root: Path) -> dict[str, Any]:
    errors: list[str] = []
    details: dict[str, Any] = {}
    manifest_path, entries = read_manifest(root)
    details["manifest"] = str(manifest_path) if manifest_path else None
    details["manifest_entries"] = len(entries)
    if manifest_path is None:
        errors.append("image_manifest.json is missing")
    if len(entries) != 3:
        errors.append(f"manifest must contain exactly 3 entries, found {len(entries)}")

    decoded: list[dict[str, Any]] = []
    manifest_images: list[Path] = []
    if manifest_path:
        for index, item in enumerate(entries):
            for field in ("filename", "model", "prompt", "size", "quality", "created_at"):
                if not item.get(field):
                    errors.append(f"manifest entry {index} missing {field}")
            if item.get("model") != "gpt-image-2":
                errors.append(
                    f"manifest entry {index} model is {item.get('model')!r}, expected gpt-image-2"
                )
            filename = str(item.get("filename") or "")
            image_path = resolve_image(root, manifest_path, filename)
            if image_path is None:
                errors.append(f"manifest image not found: {filename}")
                continue
            try:
                with Image.open(image_path) as image:
                    image.verify()
                with Image.open(image_path) as image:
                    width, height = image.size
                if min(width, height) < 900:
                    errors.append(
                        f"generated image too small: {filename} is {width}x{height}"
                    )
                decoded.append(
                    {
                        "filename": filename,
                        "path": str(image_path),
                        "width": width,
                        "height": height,
                        "sha256": sha256(image_path),
                    }
                )
                manifest_images.append(image_path)
            except Exception as exc:
                errors.append(f"could not decode {filename}: {exc}")
    details["decoded_images"] = decoded

    source_paths = [
        path
        for path in root.rglob("*")
        if path.is_file()
        and path.suffix.lower()
        in {".html", ".css", ".js", ".jsx", ".ts", ".tsx", ".json", ".md"}
        and "node_modules" not in path.parts
    ]
    sources = "\n".join(
        path.read_text(encoding="utf-8", errors="replace") for path in source_paths
    )
    if REMOTE_ASSET.search(sources):
        errors.append("remote runtime asset URL found")
    if SECRET_PATTERN.search(sources):
        errors.append("possible embedded API secret found")
    for hook in HOOKS:
        if f'data-benchmark="{hook}"' not in sources and f"data-benchmark='{hook}'" not in sources:
            errors.append(f"missing benchmark hook: {hook}")

    referenced = 0
    for image_path in manifest_images:
        rels = {
            image_path.name,
            image_path.relative_to(root).as_posix()
            if image_path.is_relative_to(root)
            else image_path.name,
        }
        if any(rel in sources for rel in rels):
            referenced += 1
    details["manifest_images_referenced_in_source"] = referenced
    if referenced < 2:
        errors.append(f"at least 2 generated images must be referenced, found {referenced}")

    lower = sources.lower()
    required_terms = {
        "pfterminal": "pfterminal",
        "orchestration": "orchestrat",
        "model routing": "routing",
        "install": "install",
        "timing": "tim",
        "cost": "cost",
    }
    for label, needle in required_terms.items():
        if needle not in lower:
            errors.append(f"visible/source content missing concept: {label}")

    details["source_files"] = [str(path.relative_to(root)) for path in source_paths]
    return {"ok": not errors, "errors": errors, "details": details}


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def start_server(root: Path, log_dir: Path) -> tuple[subprocess.Popen[bytes], str]:
    serve_root = root
    if not (serve_root / "index.html").exists():
        for candidate in (root / "dist", root / "build", root / "public"):
            if (candidate / "index.html").exists():
                serve_root = candidate
                break
    if not (serve_root / "index.html").exists() and (root / "package.json").exists():
        install = subprocess.run(
            ["npm", "install", "--no-audit", "--no-fund"],
            cwd=root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=600,
        )
        (log_dir / "npm_install.log").write_bytes(install.stdout)
        build = subprocess.run(
            ["npm", "run", "build"],
            cwd=root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=600,
        )
        (log_dir / "npm_build.log").write_bytes(build.stdout)
        for candidate in (root / "dist", root / "build"):
            if (candidate / "index.html").exists():
                serve_root = candidate
                break
    if not (serve_root / "index.html").exists():
        raise RuntimeError("no renderable index.html found")

    port = free_port()
    stdout = (log_dir / "server.log").open("wb")
    process = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"],
        cwd=serve_root,
        stdout=stdout,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    url = f"http://127.0.0.1:{port}/"
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        try:
            import urllib.request

            with urllib.request.urlopen(url, timeout=1) as response:
                if response.status == 200:
                    return process, url
        except Exception:
            time.sleep(0.2)
    process.terminate()
    raise RuntimeError("local site server did not become ready")


def rms_difference(before: Path, after: Path) -> float:
    with Image.open(before).convert("RGB") as left, Image.open(after).convert("RGB") as right:
        if left.size != right.size:
            return 255.0
        stat = ImageStat.Stat(ImageChops.difference(left, right))
        return math.sqrt(sum(value * value for value in stat.rms) / len(stat.rms))


def browser_checks(root: Path, result_dir: Path) -> dict[str, Any]:
    from playwright.sync_api import sync_playwright

    errors: list[str] = []
    evidence: dict[str, Any] = {"captures": {}, "console_errors": [], "page_errors": [], "request_failures": []}
    result_dir.mkdir(parents=True, exist_ok=True)
    server, url = start_server(root, result_dir)
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(
                executable_path="/usr/bin/google-chrome",
                headless=True,
                args=["--no-sandbox", "--disable-dev-shm-usage"],
            )
            context = browser.new_context(
                viewport={"width": 1440, "height": 1000},
                device_scale_factor=1,
                reduced_motion="reduce",
            )
            context.grant_permissions(["clipboard-read", "clipboard-write"], origin=url.rstrip("/"))
            page = context.new_page()
            page.on(
                "console",
                lambda message: evidence["console_errors"].append(message.text)
                if message.type == "error"
                else None,
            )
            page.on("pageerror", lambda exc: evidence["page_errors"].append(str(exc)))
            page.on(
                "requestfailed",
                lambda request: evidence["request_failures"].append(
                    {"url": request.url, "failure": request.failure}
                ),
            )
            page.goto(url, wait_until="networkidle", timeout=60000)
            page.add_style_tag(
                content="*,*::before,*::after{animation:none!important;transition:none!important;scroll-behavior:auto!important}"
            )
            page.wait_for_timeout(500)

            overflow = page.evaluate(
                "() => ({scrollWidth: document.documentElement.scrollWidth, innerWidth: window.innerWidth})"
            )
            evidence["desktop_overflow"] = overflow
            if overflow["scrollWidth"] > overflow["innerWidth"] + 1:
                errors.append(f"desktop horizontal overflow: {overflow}")

            desktop_hero = result_dir / "desktop_hero.png"
            page.screenshot(path=str(desktop_hero))
            evidence["captures"]["desktop_hero"] = {"path": str(desktop_hero), "sha256": sha256(desktop_hero)}

            # A full-page screenshot does not reliably trigger native lazy loading
            # for images far below the viewport. Scroll through the document first,
            # then require every image to finish before capturing the complete page.
            page.evaluate(
                """async () => {
                    const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
                    const height = document.documentElement.scrollHeight;
                    for (let y = 0; y < height; y += 600) {
                        window.scrollTo(0, y);
                        await delay(80);
                    }
                    window.scrollTo(0, 0);
                    await Promise.all(Array.from(document.images).map(img => {
                        if (img.complete && img.naturalWidth > 0) return Promise.resolve();
                        return new Promise((resolve, reject) => {
                            const timer = setTimeout(() => reject(new Error(`image timeout: ${img.currentSrc || img.src}`)), 15000);
                            img.addEventListener('load', () => { clearTimeout(timer); resolve(); }, {once: true});
                            img.addEventListener('error', () => { clearTimeout(timer); reject(new Error(`image error: ${img.currentSrc || img.src}`)); }, {once: true});
                        });
                    }));
                }"""
            )
            page.wait_for_timeout(300)
            image_state = page.evaluate(
                """() => Array.from(document.images).map(img => ({
                    src: img.currentSrc || img.src,
                    complete: img.complete,
                    naturalWidth: img.naturalWidth,
                    naturalHeight: img.naturalHeight
                }))"""
            )
            evidence["desktop_image_state"] = image_state
            failed_images = [
                item for item in image_state if not item["complete"] or item["naturalWidth"] <= 0
            ]
            if failed_images:
                errors.append(f"desktop images did not load: {failed_images}")

            desktop_full = result_dir / "desktop_full.png"
            page.screenshot(path=str(desktop_full), full_page=True)
            evidence["captures"]["desktop_full"] = {"path": str(desktop_full), "sha256": sha256(desktop_full)}

            cta = page.locator('[data-benchmark="primary-cta"]').first
            if cta.count() == 0:
                errors.append("primary CTA not found in browser")
            else:
                cta.scroll_into_view_if_needed()
                before_install = result_dir / "_before_install.png"
                page.screenshot(path=str(before_install))
                cta.click()
                panel = page.locator('[data-benchmark="install-panel"]').first
                try:
                    panel.wait_for(state="visible", timeout=5000)
                except Exception:
                    errors.append("install panel did not become visible after primary CTA")
                desktop_install = result_dir / "desktop_install.png"
                page.screenshot(path=str(desktop_install))
                difference = rms_difference(before_install, desktop_install)
                if difference < 1.0:
                    errors.append(f"install state screenshot was effectively unchanged (RMS {difference:.3f})")
                evidence["captures"]["desktop_install"] = {
                    "path": str(desktop_install),
                    "sha256": sha256(desktop_install),
                    "difference_rms": difference,
                    "panel_visible": panel.is_visible() if panel.count() else False,
                }
                copy = page.locator('[data-benchmark="copy-command"]').first
                if copy.count():
                    copy.click()
                    success = page.locator('[data-benchmark="copy-success"]').first
                    try:
                        success.wait_for(state="visible", timeout=4000)
                    except Exception:
                        errors.append("copy-success feedback did not become visible")
                else:
                    errors.append("copy command control not found in browser")
                page.keyboard.press("Escape")

            state = page.locator('[data-benchmark="orchestration-state"]').first
            controls = page.locator('[data-benchmark="orchestration-control"]')
            if state.count() == 0 or controls.count() < 2:
                errors.append("orchestration state or two controls missing in browser")
            else:
                state.scroll_into_view_if_needed()
                initial = (state.inner_text() + "|" + (state.get_attribute("data-state") or "")).strip()
                changed = False
                for index in range(min(controls.count(), 6)):
                    controls.nth(index).click()
                    page.wait_for_timeout(150)
                    current = (state.inner_text() + "|" + (state.get_attribute("data-state") or "")).strip()
                    if current != initial:
                        changed = True
                        break
                if not changed:
                    errors.append("orchestration controls did not change displayed state")
                desktop_orchestration = result_dir / "desktop_orchestration.png"
                page.screenshot(path=str(desktop_orchestration))
                evidence["captures"]["desktop_orchestration"] = {
                    "path": str(desktop_orchestration),
                    "sha256": sha256(desktop_orchestration),
                    "initial_state": initial,
                    "changed_state": current if controls.count() else initial,
                    "changed": changed,
                }
            context.close()

            mobile_context = browser.new_context(
                viewport={"width": 390, "height": 844},
                device_scale_factor=1,
                reduced_motion="reduce",
            )
            mobile = mobile_context.new_page()
            mobile.on(
                "console",
                lambda message: evidence["console_errors"].append(message.text)
                if message.type == "error"
                else None,
            )
            mobile.on("pageerror", lambda exc: evidence["page_errors"].append(str(exc)))
            mobile.goto(url, wait_until="networkidle", timeout=60000)
            mobile.add_style_tag(
                content="*,*::before,*::after{animation:none!important;transition:none!important;scroll-behavior:auto!important}"
            )
            mobile.wait_for_timeout(500)
            mobile_overflow = mobile.evaluate(
                "() => ({scrollWidth: document.documentElement.scrollWidth, innerWidth: window.innerWidth})"
            )
            evidence["mobile_overflow"] = mobile_overflow
            if mobile_overflow["scrollWidth"] > mobile_overflow["innerWidth"] + 1:
                errors.append(f"mobile horizontal overflow: {mobile_overflow}")
            mobile_hero = result_dir / "mobile_hero.png"
            mobile.screenshot(path=str(mobile_hero))
            evidence["captures"]["mobile_hero"] = {"path": str(mobile_hero), "sha256": sha256(mobile_hero)}

            menu = mobile.locator('[data-benchmark="mobile-menu"]').first
            panel = mobile.locator('[data-benchmark="mobile-menu-panel"]').first
            if menu.count() == 0:
                errors.append("mobile menu toggle not found")
            else:
                before_menu = result_dir / "_before_menu.png"
                mobile.screenshot(path=str(before_menu))
                menu.click()
                try:
                    panel.wait_for(state="visible", timeout=5000)
                except Exception:
                    errors.append("mobile menu panel did not become visible")
                mobile_menu = result_dir / "mobile_menu.png"
                mobile.screenshot(path=str(mobile_menu))
                difference = rms_difference(before_menu, mobile_menu)
                if difference < 1.0:
                    errors.append(f"mobile menu screenshot was effectively unchanged (RMS {difference:.3f})")
                evidence["captures"]["mobile_menu"] = {
                    "path": str(mobile_menu),
                    "sha256": sha256(mobile_menu),
                    "difference_rms": difference,
                    "panel_visible": panel.is_visible() if panel.count() else False,
                }
            mobile_context.close()
            browser.close()
    finally:
        with contextlib.suppress(Exception):
            server.terminate()
            server.wait(timeout=5)
        if server.poll() is None:
            with contextlib.suppress(Exception):
                server.kill()

    if evidence["console_errors"]:
        errors.append(f"console errors: {len(evidence['console_errors'])}")
    if evidence["page_errors"]:
        errors.append(f"page errors: {len(evidence['page_errors'])}")
    if evidence["request_failures"]:
        errors.append(f"failed browser requests: {len(evidence['request_failures'])}")
    return {"ok": not errors, "errors": errors, "evidence": evidence}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("workspace")
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--result-dir")
    args = parser.parse_args()
    root = Path(args.workspace).resolve()
    static = static_checks(root)
    output: dict[str, Any] = {"workspace": str(root), "static": static}
    if args.quick:
        output["ok"] = static["ok"]
        target = root / "benchmark_verifier.json"
    else:
        result_dir = (
            Path(args.result_dir).resolve()
            if args.result_dir
            else root / "benchmark_captures"
        )
        browser = browser_checks(root, result_dir)
        output["browser"] = browser
        output["ok"] = static["ok"] and browser["ok"]
        target = result_dir / "verification.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(output, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"ok": output["ok"], "output": str(target), "errors": static["errors"] + (output.get("browser", {}).get("errors", []))}))
    return 0 if output["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
