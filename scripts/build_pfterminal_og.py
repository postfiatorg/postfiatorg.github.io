#!/usr/bin/env python3
"""Render static/media-kit/pfterminal-og-1200x630.png from the design spec brief.

Flat 1200x630 on pure black with a faint 52px Post Fiat grid, a 1px phosphor-green
terminal panel containing IBM Plex Mono text, and the Post Fiat X mark rotated -45
degrees on the right. No gradient, bevel, glow, photography, or fabricated telemetry.

    python3 scripts/build_pfterminal_og.py
"""

from __future__ import annotations

import pathlib
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "static" / "media-kit" / "pfterminal-og-1200x630.png"

W, H = 1200, 630
BLACK = (0, 0, 0)
GREEN = (127, 238, 100)
PALE = (221, 255, 220)
DIM = (92, 107, 89)

LINES = [
    ("PFTerminal 0.1.19", PALE),
    ("", PALE),
    ("default model   Ambient GLM 5.2", PALE),
    ("", PALE),
    ("Nazgul", GREEN),
    ("└─ Troll", GREEN),
    ("   └─ Orc", GREEN),
]


def load_mono(size: int) -> ImageFont.FreeTypeFont:
    for name in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
        "/usr/share/fonts/TTF/DejaVuSansMono.ttf",
    ):
        if pathlib.Path(name).exists():
            return ImageFont.truetype(name, size)
    return ImageFont.load_default()


def logo_layer() -> Image.Image | None:
    """Rasterise the existing Post Fiat mark; never invent a second logo."""
    svg = ROOT / "static" / "media-kit" / "logo.svg"
    png = ROOT / "static" / "media-kit" / "logo1024x1024-whitefill.png"
    if png.exists():
        return Image.open(png).convert("RGBA")
    if svg.exists():
        tmp = pathlib.Path("/tmp/pf_logo_og.png")
        for cmd in (["rsvg-convert", "-w", "512", "-o", str(tmp), str(svg)],
                    ["inkscape", str(svg), "-o", str(tmp), "-w", "512"]):
            try:
                subprocess.run(cmd, check=True, capture_output=True, timeout=60)
                return Image.open(tmp).convert("RGBA")
            except Exception:  # noqa: BLE001
                continue
    return None


def main() -> int:
    img = Image.new("RGB", (W, H), BLACK)
    d = ImageDraw.Draw(img)

    grid = (6, 6, 6)
    for x in range(0, W, 52):
        d.line([(x, 0), (x, H)], fill=grid, width=1)
    for y in range(0, H, 52):
        d.line([(0, y), (W, y)], fill=grid, width=1)

    logo = logo_layer()
    if logo is not None:
        size = 300
        logo = logo.resize((size, size), Image.LANCZOS)
        tinted = Image.new("RGBA", logo.size, GREEN + (255,))
        tinted.putalpha(logo.split()[-1])
        tinted = tinted.rotate(-45, resample=Image.BICUBIC, expand=True)
        img.paste(tinted, (W - tinted.width - 70, (H - tinted.height) // 2), tinted)

    panel = (64, 96, 700, 534)
    d.rectangle(panel, outline=GREEN, width=1)

    title = load_mono(21)
    body = load_mono(23)
    d.text((panel[0] + 26, panel[1] + 26), "PFTerminal 0.1.19", font=title, fill=GREEN)
    d.line([(panel[0] + 1, panel[1] + 66), (panel[2] - 1, panel[1] + 66)], fill=DIM, width=1)

    y = panel[1] + 100
    for text, colour in LINES[2:]:
        if text:
            d.text((panel[0] + 26, y), text, font=body, fill=colour)
        y += 40

    d.text((panel[0] + 26, panel[3] - 58), "postfiat.org/terminal", font=title, fill=DIM)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, "PNG", optimize=True)
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
