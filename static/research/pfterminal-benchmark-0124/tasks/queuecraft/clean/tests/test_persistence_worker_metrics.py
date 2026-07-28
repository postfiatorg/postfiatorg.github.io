from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from queuecraft import FrozenClock, JsonStore, QueueCraft, QueueScheduler, Worker, WorkerPool
from queuecraft.metrics import event_counts, summarize_events


class PersistenceWorkerMetricsTests(unittest.TestCase):
    def test_json_store_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = JsonStore(Path(tmp) / "q.json")
            clock = FrozenClock(0)
            scheduler = QueueScheduler(store, clock)
            scheduler.enqueue("a", priority=3)
            restored = JsonStore(Path(tmp) / "q.json")
            self.assertEqual(restored.get("a").priority, 3)

    def test_worker_run_once_acks(self) -> None:
        clock = FrozenClock(0)
        scheduler = QueueScheduler(JsonStore(Path(tempfile.mkdtemp()) / "q.json"), clock)
        scheduler.enqueue("a", {"n": 1})
        result = Worker(scheduler, "w").run_once()
        self.assertTrue(result.ok)
        self.assertEqual(scheduler.stats()["done"], 1)

    def test_worker_failure_retries(self) -> None:
        clock = FrozenClock(0)
        scheduler = QueueScheduler(JsonStore(Path(tempfile.mkdtemp()) / "q.json"), clock)
        scheduler.enqueue("a", max_attempts=2)
        result = Worker(scheduler, "w", handler=lambda job: (_ for _ in ()).throw(RuntimeError("x"))).run_once()
        self.assertFalse(result.ok)
        self.assertEqual(scheduler.stats()["queued"], 1)

    def test_worker_pool_round_robin(self) -> None:
        api = QueueCraft(start=0)
        api.enqueue("a")
        api.enqueue("b")
        results = WorkerPool(api.scheduler, 2).drain_round_robin()
        self.assertEqual([r.job_id for r in results], ["a", "b"])

    def test_event_counts(self) -> None:
        api = QueueCraft(start=0)
        api.enqueue("a")
        api.work_once()
        counts = event_counts(api.store.events)
        self.assertEqual(counts["enqueue"], 1)
        self.assertEqual(counts["ack"], 1)

    def test_summarize_events(self) -> None:
        api = QueueCraft(start=0)
        api.enqueue("a")
        api.work_once()
        summary = summarize_events(api.store.events)
        self.assertEqual(summary["total"], 3)
