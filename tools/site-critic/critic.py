"""Vision critic panel for rendered pages.

Adapted from the Text Improvement Harness (judge lanes, promote gate). The prompt is rubric.md, verbatim
and the video-gate process (plain questions about real footage, verbatim transcripts kept).

Usage:
  critic.py score  --run runs/<tag> --page home [--runs 1] [--lanes gpt,fable,opus]
  critic.py video  --run runs/<tag> --page home
  critic.py compare --base runs/<a> --cand runs/<b> --page home
"""
import argparse
import base64
import concurrent.futures as cf
import json
import re
import statistics
import subprocess
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
KEY_FILES = {
    "openai": Path("/home/pfrpc/repos/openai.txt"),
    "openrouter": Path("/home/pfrpc/repos/openx.txt"),
}
LANES = {
    "gpt": ("openai", "gpt-6-astra"),
    "fable": ("openrouter", "anthropic/claude-fable-5.1"),
    "opus": ("openrouter", "anthropic/claude-opus-5.5"),
}
VIDEO_MODEL = "google/gemini-3.5-flash"
FRONTIER = ("fable", "opus")

PROMPT = (HERE / "rubric.md").read_text().strip()


def key(provider: str) -> str:
    return KEY_FILES[provider].read_text().strip().splitlines()[0].strip()


def jpeg_b64(png: Path, width: int = 1280) -> str:
    with tempfile.NamedTemporaryFile(suffix=".jpg") as t:
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-i", str(png), "-vf", f"scale='min({width},iw)':-2", "-q:v", "4", t.name],
            check=True,
        )
        return base64.b64encode(Path(t.name).read_bytes()).decode()


COST_LOG = HERE / "runs" / "cost_log.jsonl"


def log_cost(model: str, raw: dict):
    u = raw.get("usage") or {}
    rec = {"model": model, "cost_usd": u.get("cost"),
           "input_tokens": u.get("prompt_tokens", u.get("input_tokens")),
           "output_tokens": u.get("completion_tokens", u.get("output_tokens"))}
    COST_LOG.parent.mkdir(exist_ok=True)
    with COST_LOG.open("a") as f:
        f.write(json.dumps(rec) + "\n")


def page_images(run: Path, page: str, max_desktop: int = 6, max_mobile: int = 3):
    shots = []
    for name, cap, w in (("desktop", max_desktop, 1280), ("mobile", max_mobile, 390)):
        frames = sorted(run.glob(f"{page}.{name}.frame*.png"))[:cap]
        for f in frames:
            shots.append((f"{name} viewport, screen {f.stem.split('frame')[-1]}", jpeg_b64(f, w)))
    return shots


def post(url, payload, api_key, title="Site Critic"):
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://postfiat.org",
            "X-Title": title,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code}: {e.read().decode(errors='replace')[:800]}")


def call_lane(lane: str, prompt: str, images) -> str:
    provider, model = LANES[lane]
    if provider == "openai":
        content = [{"type": "input_text", "text": prompt}]
        for label, b in images:
            content += [{"type": "input_text", "text": label}, {"type": "input_image", "image_url": f"data:image/jpeg;base64,{b}"}]
        raw = post(
            "https://api.openai.com/v1/responses",
            {"model": model, "input": [{"role": "user", "content": content}], "max_output_tokens": 12000},
            key("openai"),
        )
        log_cost(model, raw)
        if isinstance(raw.get("output_text"), str):
            return raw["output_text"]
        return "\n".join(
            c.get("text", "") for it in raw.get("output", []) if it.get("type") == "message" for c in it.get("content", [])
        )
    content = [{"type": "text", "text": prompt}]
    for label, b in images:
        content += [{"type": "text", "text": label}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b}"}}]
    raw = post(
        "https://openrouter.ai/api/v1/chat/completions",
        {
            "model": model,
            "messages": [{"role": "user", "content": content}],
            "max_tokens": 12000,
            "usage": {"include": True},
        },
        key("openrouter"),
    )
    log_cost(model, raw)
    return raw["choices"][0]["message"]["content"]


def parse_score(text: str) -> dict:
    """Pull the 0-100 score out of a free-text answer; keep the whole answer as the explanation."""
    pats = [r"(\d{1,3})\s*(?:/|out of)\s*100", r"[Ss]core[^0-9\n]{0,20}(\d{1,3})", r"\b(\d{1,3})\b"]
    for pat in pats:
        m = re.search(pat, text)
        if m and 0 <= int(m.group(1)) <= 100:
            return {"score_out_of_100": int(m.group(1)), "explanation": text}
    return {"score_out_of_100": None, "explanation": text}


def score(run: Path, page: str, lanes, runs: int, hero: bool = False):
    prompt = PROMPT
    images = page_images(run, page, 1, 1) if hero else page_images(run, page)
    jobs = [(lane, i) for lane in lanes for i in range(runs)]
    out = []

    def one(job):
        lane, i = job
        try:
            txt = call_lane(lane, prompt, images)
            return {"lane": lane, "run": i, "model": LANES[lane][1], "verdict": parse_score(txt), "raw": txt}
        except Exception as e:  # keep the panel going; record the failure verbatim
            return {"lane": lane, "run": i, "model": LANES[lane][1], "error": str(e)[:1200]}

    with cf.ThreadPoolExecutor(max_workers=len(jobs)) as ex:
        out = list(ex.map(one, jobs))
    crit = run / "critiques"
    crit.mkdir(exist_ok=True)
    (crit / f"{page}.panel.json").write_text(json.dumps(out, indent=2))
    summary = summarize(out)
    (crit / f"{page}.summary.json").write_text(json.dumps(summary, indent=2))
    return summary, out


def summarize(out):
    by = {}
    for r in out:
        if "verdict" in r:
            if r["verdict"].get("score_out_of_100") is not None:
                by.setdefault(r["lane"], []).append(float(r["verdict"]["score_out_of_100"]))
    lane_mean = {k: round(statistics.mean(v), 2) for k, v in by.items()}
    frontier = [lane_mean[k] for k in FRONTIER if k in lane_mean]
    return {
        "lane_mean": lane_mean,
        "frontier_mean": round(statistics.mean(frontier), 2) if frontier else None,
        "panel_mean": round(statistics.mean(lane_mean.values()), 2) if lane_mean else None,
        "errors": [r["error"][:200] for r in out if "error" in r],
    }


VIDEO_QUESTION = PROMPT


def video(run: Path, page: str):
    mp4 = run / f"{page}.desktop.scroll.mp4"
    b = base64.b64encode(mp4.read_bytes()).decode()
    raw = post(
        "https://openrouter.ai/api/v1/chat/completions",
        {
            "model": VIDEO_MODEL,
            "messages": [{"role": "user", "content": [
                {"type": "text", "text": VIDEO_QUESTION},
                {"type": "video_url", "video_url": {"url": f"data:video/mp4;base64,{b}"}},
            ]}],
            "max_tokens": 4000,
        },
        key("openrouter"),
    )
    txt = raw["choices"][0]["message"]["content"]
    crit = run / "critiques"
    crit.mkdir(exist_ok=True)
    (crit / f"{page}.video.md").write_text(f"# {VIDEO_MODEL} on {mp4.name}\n\n> {VIDEO_QUESTION}\n\n{txt}\n")
    return txt


def compare(base: Path, cand: Path, page: str, flat_margin=1.0, improve_margin=1.0):
    b = json.loads((base / "critiques" / f"{page}.summary.json").read_text())
    c = json.loads((cand / "critiques" / f"{page}.summary.json").read_text())
    gpt_ok = c["lane_mean"].get("gpt", 0) >= b["lane_mean"].get("gpt", 0) - flat_margin
    fr_ok = (c["frontier_mean"] or 0) >= (b["frontier_mean"] or 0) + improve_margin
    return {"base": b, "cand": c, "gpt_flat_ok": gpt_ok, "frontier_improved": fr_ok, "promote": gpt_ok and fr_ok}


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("score"); s.add_argument("--run", required=True); s.add_argument("--page", required=True)
    s.add_argument("--runs", type=int, default=1); s.add_argument("--lanes", default="gpt,fable,opus")
    s.add_argument("--hero", action="store_true", help="send only the first desktop and mobile screen (cheap; for hero/tagline tests)")
    v = sub.add_parser("video"); v.add_argument("--run", required=True); v.add_argument("--page", required=True)
    c = sub.add_parser("compare"); c.add_argument("--base", required=True); c.add_argument("--cand", required=True); c.add_argument("--page", required=True)
    a = ap.parse_args()
    if a.cmd == "score":
        summary, out = score(Path(a.run), a.page, a.lanes.split(","), a.runs, a.hero)
        for r in out:
            if "verdict" in r:
                vd = r["verdict"]
                print(f"[{r['lane']}] {vd.get('score_out_of_100')}")
            else:
                print(f"[{r['lane']}] ERROR {r['error'][:300]}")
        print(json.dumps(summary))
    elif a.cmd == "video":
        print(video(Path(a.run), a.page))
    else:
        print(json.dumps(compare(Path(a.base), Path(a.cand), a.page), indent=2))


if __name__ == "__main__":
    main()
