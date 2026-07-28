from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from queuecraft import QueueCraft


class ApiIntegrationTests(unittest.TestCase):
    def test_api_work_once(self) -> None:
        api = QueueCraft(start=0)
        api.enqueue("a", {"x": 1})
        self.assertEqual(api.work_once()["job_id"], "a")

    def test_api_empty_returns_none(self) -> None:
        self.assertIsNone(QueueCraft(start=0).work_once())

    def test_api_advance_unlocks_delay(self) -> None:
        api = QueueCraft(start=0)
        api.enqueue("a", delay=5)
        self.assertIsNone(api.work_once())
        api.advance(5)
        self.assertEqual(api.work_once()["job_id"], "a")

    def test_api_persistent_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "queue.json"
            first = QueueCraft(path=path, start=0)
            first.enqueue("a")
            second = QueueCraft(path=path, start=0)
            self.assertEqual(second.work_once()["job_id"], "a")
