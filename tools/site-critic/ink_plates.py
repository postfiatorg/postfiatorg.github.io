"""Generate Hyperstitional Ink plates for the site (OpenRouter images, same call shape as navstrategies video_studios).

Usage: ink_plates.py [name ...]   # default: all plates that do not exist yet
"""
import base64
import json
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

OUT = Path("/home/pfrpc/tmp/ink-src")
KEY = Path("/home/pfrpc/repos/openx.txt").read_text().strip().splitlines()[0].strip()
MODEL = "openai/gpt-image-2"

STYLE = (
    "An authored pen-and-ink plate of techno-arcane financial machinery, drawn with a fine nib and a brush on warm ivory "
    "cotton paper (#F2EEE5). Tens of thousands of crisp crosshatching strokes, dense stippled shadow, pooled India ink, "
    "etched engraving-grade detail, varied nib pressure, deep black masses, generous white negative space. Lineage: "
    "Piranesi's Carceri and Vedute, nineteenth-century patent and engineering engravings, Hugh Ferriss, Lebbeus Woods, "
    "Tsutomu Nihei's megastructures. Austere, architectural, cybernetic, monumental and quiet: theory-fiction, not "
    "fantasy. No robed or hooded figures, no glowing eyes, no gore, no blood, no gothic ornament, no fantasy creatures. Palette: black ink on ivory with sparse luminous petrol-teal (#057F82) watercolor washes "
    "under five percent of the frame, and at most one small oxblood accent on the single most important element. "
    "Preserve paper grain. No text, letters, numbers, glyph strings, logos, coins with symbols, charts, neon, cyber "
    "cityscapes, plastic CGI, glossy 3D, cartoons, anime, mascots, parchment or sepia."
)

PLATES_V1 = {
    "hero": "Wide panoramic plate. A vast cathedral-scale ledger engine receding into deep perspective: tall engraved obelisk-validators each with a single lit teal aperture, joined by taut ink threads, around a continuous spiral ribbon of hatched ledger pages rising into a dark vault. Tiny solitary figures at the base for scale. Quiet empty ivory paper across the left third of the frame.",
    "navcoin": "A sealed vault drawn in cutaway: inside, a precise balance scale weighing a dense bundle of heterogeneous holdings (bars, bonds, folded certificates) against a single thin luminous teal disc. Fine teal filaments converge from every holding onto a glass lens that focuses them into the disc. Engraved, clinical, exact.",
    "swap": "Two hooded couriers, faceless, each passing a sealed ink envelope into opposite sides of a single black monolithic chamber; from the chamber two different sealed envelopes emerge at the same instant. The chamber is wrapped in a dense veil of crosshatched shadow; a thin teal seam of light marks the atomic join. One oxblood wax seal.",
    "supply": "A monumental fixed obelisk cast as a single unbroken block, ringed by a slow furnace at its base in which small offerings burn to ash and smoke that rises and disappears; nothing is added to the obelisk. Severe symmetry, stark negative space.",
    "quantum": "A lattice: an immense crystalline cage of interlocking engraved struts in impossible depth, protecting a small glowing teal key at its center. Shards of a shattered older curved lock lie on the ground in the foreground.",
    "cobalt": "A tribunal of seven tall obelisk-nodes standing in a ring on a stone floor, each with a lit teal aperture, examining a single sealed envelope with an oxblood wax seal floating at the center on taut ink threads. Old weathered obelisks judging a newer smaller one entering the ring.",
    "hive": "A swarm of many small anonymous hooded figures and masked automata seen from above in an engraved plaza, each linked by fine ink threads to a single towering hive-like intelligence machine of interlocking cells at the center; a few threads glow teal. Dense, intricate, coordinated.",
}


PLATES = {
    "hero": "Wide panoramic plate. A vast receding colonnade of identical monolithic validator towers in severe one-point perspective, each a plain engraved slab with a single small teal aperture, linked by taut cables to a continuous spiral ribbon of hatched ledger sheets ascending into a vaulted megastructure. Two or three tiny silhouetted people at ground level for scale. The left third of the frame is quiet empty ivory paper.",
    "navcoin": "A technical cutaway engraving of a precision balance inside a vault, drawn like a patent plate: on one pan a dense bundle of heterogeneous holdings (ingots, bond certificates, folded contracts), on the other a single thin teal disc. Fine teal filaments converge from each holding through a glass lens onto the disc. Exact, clinical, engineered.",
    "swap": "An engineering engraving of a sealed black monolithic exchange chamber in a vast empty hall. Two parallel conveyor rails enter from opposite sides, each carrying one sealed ingot of a different shape; the same rails leave carrying the two ingots swapped. The chamber is wrapped in dense crosshatched shadow; a thin teal seam of light marks the atomic join. One small oxblood seal on the chamber. No people.",
    "quantum": "An immense lattice: a crystalline cage of interlocking engraved struts in deep perspective, like a Piranesi prison rebuilt as a lattice-based cryptographic structure, protecting a small teal key at its center. In the foreground, the neat fragments of an older circular dial-lock lie disassembled on the floor like components on an engineer's bench. No people, no organic forms, no red.",
    "cobalt": "Seven tall plain monolithic slabs arranged in a precise ring on a geometric stone floor, seen from a high oblique angle, each with a single small teal aperture, all connected by taut ink threads to a small sealed document with an oxblood wax seal hovering at the center. A smaller new slab stands at the edge of the ring awaiting admission. Severe, ceremonial, architectural. No people.",
    "hive": "Seen from high above: a vast engraved plaza laid out like a circuit, with hundreds of small identical work-cells and desks arranged in concentric rings, each linked by fine ink threads to a central cellular hive-tower of hexagonal chambers; a few threads glow teal. Tiny anonymous silhouettes at the desks, too small for detail. Dense, ordered, coordinated, like an engraving of a city plan.",
}


def gen(name: str):
    target = OUT / f"{name}.png"
    if target.exists():
        return name, "exists"
    payload = {"model": MODEL, "prompt": f"{PLATES[name]}\n\n{STYLE}", "quality": "high", "aspect_ratio": "16:9", "n": 1}
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/images",
        data=json.dumps(payload).encode(),
        method="POST",
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json", "HTTP-Referer": "https://postfiat.org", "X-Title": "Post Fiat site plates"},
    )
    with urllib.request.urlopen(req, timeout=600) as r:
        body = json.loads(r.read().decode())
    entry = body["data"][0]
    target.write_bytes(base64.b64decode(entry["b64_json"], validate=True))
    (OUT / f"{name}.json").write_text(json.dumps({"model": MODEL, "prompt": payload["prompt"], "usage": body.get("usage", {})}, indent=2))
    return name, body.get("usage", {}).get("cost")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    names = sys.argv[1:] or list(PLATES)
    with ThreadPoolExecutor(max_workers=len(names)) as ex:
        for name, res in ex.map(gen, names):
            print(name, res)
