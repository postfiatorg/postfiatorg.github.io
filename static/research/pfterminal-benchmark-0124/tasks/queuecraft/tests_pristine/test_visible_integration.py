from __future__ import annotations

import unittest

from queuecraft import FrozenClock, MemoryStore, QueueScheduler
from queuecraft.worker import Worker


class VisibleIntegrationTests(unittest.TestCase):
    def test_due_job_at_exact_resume_time_is_processed_by_worker(self) -> None:
        clock = FrozenClock(100)
        scheduler = QueueScheduler(MemoryStore(), clock)
        scheduler.enqueue("send-report", {"kind": "email"}, priority=50, delay=0)
        result = Worker(scheduler, "worker-a").run_once()
        self.assertEqual(result.job_id, "send-report")
        self.assertEqual(scheduler.stats()["done"], 1)


if __name__ == "__main__":
    unittest.main()
