from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from queuecraft import FrozenClock, JsonStore, MemoryStore, QueueScheduler, QueueEmpty
from queuecraft.models import JobState


class BugProbeTests(unittest.TestCase):
    def test_probe_bug1_due_at_now_is_ready(self) -> None:
        clock = FrozenClock(10)
        scheduler = QueueScheduler(MemoryStore(), clock)
        scheduler.enqueue("job", delay=0)
        self.assertEqual([job.id for job in scheduler.ready_jobs()], ["job"])

    def test_probe_bug2_higher_priority_wins_over_lower_priority(self) -> None:
        clock = FrozenClock(0)
        scheduler = QueueScheduler(MemoryStore(), clock)
        scheduler.enqueue("low", priority=1)
        scheduler.enqueue("high", priority=10)
        self.assertEqual(scheduler.acquire("w").id, "high")

    def test_probe_bug3_fifo_tie_break_with_same_priority(self) -> None:
        clock = FrozenClock(0)
        scheduler = QueueScheduler(MemoryStore(), clock)
        scheduler.enqueue("first", priority=5)
        scheduler.enqueue("second", priority=5)
        self.assertEqual([job.id for job in scheduler.ready_jobs()], ["first", "second"])

    def test_probe_bug4_expired_lease_at_boundary_requeues(self) -> None:
        clock = FrozenClock(0)
        scheduler = QueueScheduler(MemoryStore(), clock)
        scheduler.enqueue("job")
        scheduler.acquire("w", lease_seconds=5)
        clock.set(5)
        self.assertEqual(scheduler.release_expired(), ["job"])
        self.assertEqual(scheduler.acquire("w2").id, "job")

    def test_probe_bug5_max_attempts_moves_to_dead_letter_without_extra_retry(self) -> None:
        clock = FrozenClock(0)
        store = MemoryStore()
        scheduler = QueueScheduler(store, clock)
        job = scheduler.enqueue("job", max_attempts=1)
        leased = scheduler.acquire("w")
        scheduler.fail(leased.id, leased.lease_id or "", "boom")
        self.assertEqual(scheduler.get("job").state, JobState.DEAD)
        self.assertEqual(len(store.dead), 1)

    def test_probe_bug6_persistence_preserves_delay_priority_and_sequence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "queue.json"
            clock = FrozenClock(0)
            scheduler = QueueScheduler(JsonStore(path), clock)
            scheduler.enqueue("low", priority=1, delay=1)
            scheduler.enqueue("high", priority=9, delay=1)
            clock.set(1)
            restored = QueueScheduler(JsonStore(path), clock)
            self.assertEqual([job.id for job in restored.ready_jobs()], ["high", "low"])

    def test_probe_bug7_ack_persists_done_state_after_reload(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "queue.json"
            clock = FrozenClock(0)
            scheduler = QueueScheduler(JsonStore(path), clock)
            scheduler.enqueue("job")
            job = scheduler.acquire("w")
            scheduler.ack(job.id, job.lease_id or "")
            restored = QueueScheduler(JsonStore(path), clock)
            self.assertEqual(restored.get("job").state, JobState.DONE)


if __name__ == "__main__":
    unittest.main()
