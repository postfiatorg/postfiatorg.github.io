from __future__ import annotations

import unittest

from queuecraft.clock import FrozenClock, epoch_to_datetime, parse_duration, window_bounds
from queuecraft.models import Job, build_stats
from queuecraft.priority import PriorityPolicy, bucket_priority


class ClockPriorityModelTests(unittest.TestCase):
    def test_parse_duration(self) -> None:
        self.assertEqual(parse_duration("2m"), 120)
        self.assertEqual(parse_duration("5s"), 5)

    def test_clock_advance(self) -> None:
        clock = FrozenClock(1)
        self.assertEqual(clock.advance(2), 3)

    def test_epoch_conversion(self) -> None:
        self.assertEqual(epoch_to_datetime(0).year, 1970)

    def test_window_bounds(self) -> None:
        self.assertEqual(window_bounds(0, 5, 2), [(0, 5), (5, 10)])

    def test_priority_aging(self) -> None:
        job = Job("a", priority=1, created_at=0)
        self.assertEqual(PriorityPolicy(aging_seconds=10, aging_boost=2).effective_priority(job, 25), 5)

    def test_bucket_priority(self) -> None:
        self.assertEqual(bucket_priority(100), "critical")
        self.assertEqual(bucket_priority(-1), "low")

    def test_job_round_trip(self) -> None:
        job = Job("a", payload={"x": 1})
        self.assertEqual(Job.from_dict(job.to_dict()).payload, {"x": 1})

    def test_build_stats(self) -> None:
        self.assertEqual(build_stats([Job("a")], [], 0).queued, 1)
