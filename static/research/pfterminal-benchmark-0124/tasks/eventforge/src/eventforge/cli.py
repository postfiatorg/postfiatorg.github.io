from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import monthly_report, replay_events


def _read_lines(path: str) -> list[str]:
    return Path(path).read_text(encoding="utf-8").splitlines()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="eventforge")
    sub = parser.add_subparsers(dest="command", required=True)

    replay = sub.add_parser("replay")
    replay.add_argument("events")
    replay.add_argument("--as-of")
    replay.add_argument("--json", action="store_true")

    report = sub.add_parser("report")
    report.add_argument("events")
    report.add_argument("--month", required=True)
    report.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)
    if args.command == "replay":
        result = replay_events(_read_lines(args.events), as_of=args.as_of)
    else:
        result = monthly_report(_read_lines(args.events), month=args.month)

    if args.json:
        print(json.dumps(result, sort_keys=True))
    else:
        print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
