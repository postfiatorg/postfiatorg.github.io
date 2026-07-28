from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


EVENTS_COMPLEX = [
    '{"id":"late","ts":"2026-02-01T00:00:00Z","type":"deposit","account":"alice","amount":"999.00","currency":"USD"}',
    '{"id":"seed","ts":"2025-12-31T23:59:00Z","type":"deposit","account":"alice","amount":"10.00","currency":"USD"}',
    '{"id":"dep","ts":"2026-01-02T10:00:00Z","type":"deposit","account":"alice","amount":"100.005","currency":"USD"}',
    '{"id":"dup","ts":"2026-01-02T10:01:00Z","type":"deposit","account":"alice","amount":"1.00","currency":"USD"}',
    '{"id":"dup","ts":"2026-01-02T10:02:00Z","type":"deposit","account":"alice","amount":"500.00","currency":"USD"}',
    '{"id":"hold1","ts":"2026-01-03T09:00:00Z","type":"hold","account":"alice","amount":"30.00","currency":"USD"}',
    '{"id":"rel1","ts":"2026-01-04T09:00:00Z","type":"release","account":"alice","hold_id":"hold1","amount":"10.00","currency":"USD"}',
    '{"id":"wd","ts":"2026-01-05T12:00:00Z","type":"withdrawal","account":"alice","amount":"20.00","currency":"USD"}',
    '{"id":"fee","ts":"2026-01-06T12:00:00Z","type":"fee","account":"alice","amount":"2.50","currency":"USD"}',
    '{"id":"xfer","ts":"2026-01-07T12:00:00Z","type":"transfer","from_account":"alice","to_account":"bob","amount":"15.00","currency":"USD"}',
    '{"id":"adj","ts":"2026-01-08T12:00:00Z","type":"adjustment","account":"bob","amount":"-1.25","currency":"USD"}',
    '{"id":"rev-xfer","ts":"2026-01-09T12:00:00Z","type":"reversal","reverses":"xfer"}',
    '{"id":"bad-release","ts":"2026-01-10T12:00:00Z","type":"release","account":"alice","hold_id":"hold1","amount":"99.00","currency":"USD"}',
    '{"id":"missing-rev","ts":"2026-01-11T12:00:00Z","type":"reversal","reverses":"does-not-exist"}',
    '{"id":"nan","ts":"2026-01-12T12:00:00Z","type":"deposit","account":"alice","amount":"NaN","currency":"USD"}',
    '{"id":"bad-json",',
]


def money_path(data: dict, *path: str) -> str:
    cur = data
    for part in path:
        cur = cur[part]
    return cur


class HiddenContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        repo = Path(__file__).resolve().parent
        sys.path.insert(0, str(repo / "src"))
        global monthly_report, replay_events
        from eventforge import monthly_report as mr
        from eventforge import replay_events as re

        monthly_report = mr
        replay_events = re

    def test_replay_complex_balances_and_diagnostics(self) -> None:
        state = replay_events(EVENTS_COMPLEX, as_of="2026-01-31T23:59:59Z")
        self.assertEqual(money_path(state, "accounts", "alice", "USD", "posted"), "88.51")
        self.assertEqual(money_path(state, "accounts", "alice", "USD", "held"), "20.00")
        self.assertEqual(money_path(state, "accounts", "alice", "USD", "available"), "68.51")
        self.assertEqual(money_path(state, "accounts", "bob", "USD", "posted"), "-1.25")
        self.assertEqual(state["applied_event_ids"][:3], ["seed", "dep", "dup"])
        codes = [d["code"] for d in state["diagnostics"]]
        for expected in [
            "duplicate_event",
            "invalid_release",
            "missing_reversal_target",
            "invalid_amount",
            "invalid_json",
        ]:
            self.assertIn(expected, codes)

    def test_as_of_filter_excludes_later_events(self) -> None:
        state = replay_events(EVENTS_COMPLEX, as_of="2026-01-05T23:59:59Z")
        self.assertEqual(money_path(state, "accounts", "alice", "USD", "posted"), "91.01")
        self.assertEqual(money_path(state, "accounts", "alice", "USD", "held"), "20.00")
        self.assertNotIn("bob", state["accounts"])

    def test_reversal_is_idempotent(self) -> None:
        lines = [
            '{"id":"d","ts":"2026-01-01T00:00:00Z","type":"deposit","account":"a","amount":"10","currency":"USD"}',
            '{"id":"r1","ts":"2026-01-02T00:00:00Z","type":"reversal","reverses":"d"}',
            '{"id":"r2","ts":"2026-01-03T00:00:00Z","type":"reversal","reverses":"d"}',
        ]
        state = replay_events(lines)
        self.assertEqual(money_path(state, "accounts", "a", "USD", "posted"), "0.00")
        self.assertIn("already_reversed", [d["code"] for d in state["diagnostics"]])

    def test_insufficient_hold_is_skipped(self) -> None:
        lines = [
            '{"id":"d","ts":"2026-01-01T00:00:00Z","type":"deposit","account":"a","amount":"5","currency":"USD"}',
            '{"id":"h","ts":"2026-01-02T00:00:00Z","type":"hold","account":"a","amount":"6","currency":"USD"}',
        ]
        state = replay_events(lines)
        self.assertEqual(money_path(state, "accounts", "a", "USD", "posted"), "5.00")
        self.assertEqual(money_path(state, "accounts", "a", "USD", "held"), "0.00")
        self.assertIn("insufficient_available", [d["code"] for d in state["diagnostics"]])

    def test_monthly_report_flow_accounting(self) -> None:
        report = monthly_report(EVENTS_COMPLEX, month="2026-01")
        alice = report["accounts"]["alice"]["USD"]
        self.assertEqual(alice["opening"], "10.00")
        self.assertEqual(alice["inflow"], "116.01")
        self.assertEqual(alice["outflow"], "35.00")
        self.assertEqual(alice["fees"], "2.50")
        self.assertEqual(alice["closing"], "88.51")
        bob = report["accounts"]["bob"]["USD"]
        self.assertEqual(bob["inflow"], "15.00")
        self.assertEqual(bob["outflow"], "16.25")
        self.assertEqual(bob["closing"], "-1.25")

    def test_cli_json_replay_and_report(self) -> None:
        repo = Path(__file__).resolve().parent
        env = os.environ.copy()
        env["PYTHONPATH"] = str(repo / "src")
        with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as f:
            f.write("\n".join(EVENTS_COMPLEX))
            events_path = f.name
        replay_out = subprocess.check_output(
            [
                sys.executable,
                "-m",
                "eventforge.cli",
                "replay",
                events_path,
                "--as-of",
                "2026-01-31T23:59:59Z",
                "--json",
            ],
            cwd=repo,
            env=env,
            text=True,
        )
        replay_data = json.loads(replay_out)
        self.assertEqual(money_path(replay_data, "accounts", "alice", "USD", "posted"), "88.51")

        report_out = subprocess.check_output(
            [sys.executable, "-m", "eventforge.cli", "report", events_path, "--month", "2026-01", "--json"],
            cwd=repo,
            env=env,
            text=True,
        )
        report_data = json.loads(report_out)
        self.assertEqual(report_data["month"], "2026-01")
        self.assertEqual(report_data["accounts"]["alice"]["USD"]["closing"], "88.51")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo", help="Benchmark repo copy to verify")
    args = parser.parse_args()
    repo = Path(args.repo).resolve()
    if not (repo / "src" / "eventforge").exists():
        print(json.dumps({"ok": False, "error": f"not an eventforge repo: {repo}"}))
        return 2

    # Make this file appear under the candidate repo so relative imports and cwd
    # checks are exactly the same as a normal test run.
    target = repo / ".hidden_verify.py"
    target.write_text(Path(__file__).read_text(encoding="utf-8"), encoding="utf-8")
    try:
        proc = subprocess.run(
            [sys.executable, str(target), "--internal-run"],
            cwd=repo,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=60,
        )
    finally:
        target.unlink(missing_ok=True)
    print(proc.stdout, end="")
    return proc.returncode


def internal_run() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(HiddenContractTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    summary = {
        "ok": result.wasSuccessful(),
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
    }
    print("HIDDEN_VERIFIER_SUMMARY", json.dumps(summary, sort_keys=True))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    if "--internal-run" in sys.argv:
        raise SystemExit(internal_run())
    raise SystemExit(main())
