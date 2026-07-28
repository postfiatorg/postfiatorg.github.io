from __future__ import annotations

import unittest

from queuecraft import FrozenClock, MemoryStore, QueueScheduler, QueueEmpty
from queuecraft.models import JobState


class SchedulerCoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.clock = FrozenClock(0)
        self.scheduler = QueueScheduler(MemoryStore(), self.clock)

    def test_enqueue_defaults(self) -> None:
        job = self.scheduler.enqueue("a", {"x": 1})
        self.assertEqual(job.payload, {"x": 1})
        self.assertEqual(job.state, JobState.QUEUED)

    def test_delayed_job_not_ready_before_time(self) -> None:
        self.scheduler.enqueue("a", delay=10)
        self.assertEqual(self.scheduler.ready_jobs(), [])

    def test_acquire_sets_lease(self) -> None:
        self.scheduler.enqueue("a")
        job = self.scheduler.acquire("worker", lease_seconds=4)
        self.assertEqual(job.state, JobState.LEASED)
        self.assertEqual(job.locked_until, 4)

    def test_acquire_empty_raises(self) -> None:
        with self.assertRaises(QueueEmpty):
            self.scheduler.acquire("worker")

    def test_ack_done(self) -> None:
        self.scheduler.enqueue("a")
        job = self.scheduler.acquire("worker")
        self.scheduler.ack(job.id, job.lease_id or "")
        self.assertEqual(self.scheduler.get("a").state, JobState.DONE)

    def test_fail_retries(self) -> None:
        self.scheduler.enqueue("a", max_attempts=2)
        job = self.scheduler.acquire("worker")
        self.scheduler.fail(job.id, job.lease_id or "", "boom", retry_delay=3)
        self.assertEqual(self.scheduler.get("a").state, JobState.QUEUED)
        self.assertEqual(self.scheduler.get("a").run_at, 3)

    def test_cancel_removes_queued(self) -> None:
        self.scheduler.enqueue("a")
        self.scheduler.cancel("a")
        with self.assertRaises(Exception):
            self.scheduler.get("a")

    def test_stats_counts_delayed(self) -> None:
        self.scheduler.enqueue("a", delay=3)
        self.assertEqual(self.scheduler.stats()["delayed"], 1)

    def test_retry_delay_blocks_until_advanced(self) -> None:
        self.scheduler.enqueue("retry", max_attempts=2)
        job = self.scheduler.acquire("worker")
        self.scheduler.fail(job.id, job.lease_id or "", "boom", retry_delay=5)
        self.assertEqual(self.scheduler.ready_jobs(), [])
        self.clock.advance(5)
        self.assertEqual([job.id for job in self.scheduler.ready_jobs()], ["retry"])
