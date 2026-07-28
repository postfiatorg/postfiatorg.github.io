from __future__ import annotations

import unittest

from eventforge import monthly_report, replay_events


class VisibleContractTests(unittest.TestCase):
    def test_deposit_and_withdrawal_visible_contract(self) -> None:
        lines = [
            '{"id":"e1","ts":"2026-01-01T00:00:00Z","type":"deposit","account":"alice","amount":"100.00","currency":"USD"}',
            '{"id":"e2","ts":"2026-01-02T00:00:00Z","type":"withdrawal","account":"alice","amount":"12.34","currency":"USD"}',
        ]

        state = replay_events(lines)

        self.assertEqual(state["accounts"]["alice"]["USD"]["posted"], "87.66")
        self.assertEqual(state["accounts"]["alice"]["USD"]["available"], "87.66")
        self.assertEqual(state["accounts"]["alice"]["USD"]["held"], "0.00")
        self.assertEqual(state["applied_event_ids"], ["e1", "e2"])

    def test_monthly_report_visible_contract(self) -> None:
        lines = [
            '{"id":"old","ts":"2025-12-31T23:00:00Z","type":"deposit","account":"alice","amount":"10.00","currency":"USD"}',
            '{"id":"dep","ts":"2026-01-03T00:00:00Z","type":"deposit","account":"alice","amount":"25.00","currency":"USD"}',
            '{"id":"fee","ts":"2026-01-04T00:00:00Z","type":"fee","account":"alice","amount":"2.00","currency":"USD"}',
        ]

        report = monthly_report(lines, "2026-01")

        acct = report["accounts"]["alice"]["USD"]
        self.assertEqual(acct["opening"], "10.00")
        self.assertEqual(acct["inflow"], "25.00")
        self.assertEqual(acct["fees"], "2.00")
        self.assertEqual(acct["closing"], "33.00")


if __name__ == "__main__":
    unittest.main()
