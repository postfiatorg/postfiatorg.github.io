from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Any

from .errors import QueueEmpty
from .models import Job
from .scheduler import QueueScheduler


@dataclass
class WorkerResult:
    job_id: str
    ok: bool
    detail: dict[str, Any]


class Worker:
    def __init__(self, scheduler: QueueScheduler, worker_id: str, handler: Callable[[Job], dict[str, Any]] | None = None):
        self.scheduler = scheduler
        self.worker_id = worker_id
        self.handler = handler or (lambda job: {"ok": True, "payload": job.payload})

    def run_once(self, *, queue: str | None = None) -> WorkerResult:
        job = self.scheduler.acquire(self.worker_id, queue=queue)
        try:
            detail = self.handler(job)
        except BaseException as exc:
            self.scheduler.fail(job.id, job.lease_id or "", str(exc))
            return WorkerResult(job.id, False, {"error": str(exc)})
        self.scheduler.ack(job.id, job.lease_id or "")
        return WorkerResult(job.id, True, detail)

    def drain(self, limit: int = 100, *, queue: str | None = None) -> list[WorkerResult]:
        results: list[WorkerResult] = []
        for _ in range(limit):
            try:
                results.append(self.run_once(queue=queue))
            except QueueEmpty:
                break
        return results


class WorkerPool:
    def __init__(self, scheduler: QueueScheduler, size: int):
        self.workers = [Worker(scheduler, f"worker-{i}") for i in range(size)]

    def drain_round_robin(self, limit: int = 100) -> list[WorkerResult]:
        results: list[WorkerResult] = []
        for index in range(limit):
            worker = self.workers[index % len(self.workers)]
            try:
                results.append(worker.run_once())
            except QueueEmpty:
                break
        return results


def worker_plan_0(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["worker_plan_0_score"] = score + priority * 1 - attempts
    data["worker_plan_0_bucket"] = "high" if data["worker_plan_0_score"] >= 0 else "normal"
    data["worker_plan_0_ready"] = bool(data.get("enabled", True)) and data["worker_plan_0_bucket"] in {"high", "normal"}
    return data


def worker_plan_1(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["worker_plan_1_score"] = score + priority * 2 - attempts
    data["worker_plan_1_bucket"] = "high" if data["worker_plan_1_score"] >= 1 else "normal"
    data["worker_plan_1_ready"] = bool(data.get("enabled", True)) and data["worker_plan_1_bucket"] in {"high", "normal"}
    return data


def worker_plan_2(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["worker_plan_2_score"] = score + priority * 3 - attempts
    data["worker_plan_2_bucket"] = "high" if data["worker_plan_2_score"] >= 2 else "normal"
    data["worker_plan_2_ready"] = bool(data.get("enabled", True)) and data["worker_plan_2_bucket"] in {"high", "normal"}
    return data


def worker_plan_3(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["worker_plan_3_score"] = score + priority * 4 - attempts
    data["worker_plan_3_bucket"] = "high" if data["worker_plan_3_score"] >= 3 else "normal"
    data["worker_plan_3_ready"] = bool(data.get("enabled", True)) and data["worker_plan_3_bucket"] in {"high", "normal"}
    return data


def worker_plan_4(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["worker_plan_4_score"] = score + priority * 5 - attempts
    data["worker_plan_4_bucket"] = "high" if data["worker_plan_4_score"] >= 4 else "normal"
    data["worker_plan_4_ready"] = bool(data.get("enabled", True)) and data["worker_plan_4_bucket"] in {"high", "normal"}
    return data


def worker_plan_5(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["worker_plan_5_score"] = score + priority * 6 - attempts
    data["worker_plan_5_bucket"] = "high" if data["worker_plan_5_score"] >= 5 else "normal"
    data["worker_plan_5_ready"] = bool(data.get("enabled", True)) and data["worker_plan_5_bucket"] in {"high", "normal"}
    return data


def worker_plan_6(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["worker_plan_6_score"] = score + priority * 7 - attempts
    data["worker_plan_6_bucket"] = "high" if data["worker_plan_6_score"] >= 6 else "normal"
    data["worker_plan_6_ready"] = bool(data.get("enabled", True)) and data["worker_plan_6_bucket"] in {"high", "normal"}
    return data


def worker_plan_7(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["worker_plan_7_score"] = score + priority * 8 - attempts
    data["worker_plan_7_bucket"] = "high" if data["worker_plan_7_score"] >= 0 else "normal"
    data["worker_plan_7_ready"] = bool(data.get("enabled", True)) and data["worker_plan_7_bucket"] in {"high", "normal"}
    return data


def worker_plan_8(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["worker_plan_8_score"] = score + priority * 9 - attempts
    data["worker_plan_8_bucket"] = "high" if data["worker_plan_8_score"] >= 1 else "normal"
    data["worker_plan_8_ready"] = bool(data.get("enabled", True)) and data["worker_plan_8_bucket"] in {"high", "normal"}
    return data


def worker_plan_9(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["worker_plan_9_score"] = score + priority * 10 - attempts
    data["worker_plan_9_bucket"] = "high" if data["worker_plan_9_score"] >= 2 else "normal"
    data["worker_plan_9_ready"] = bool(data.get("enabled", True)) and data["worker_plan_9_bucket"] in {"high", "normal"}
    return data


def worker_plan_10(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["worker_plan_10_score"] = score + priority * 11 - attempts
    data["worker_plan_10_bucket"] = "high" if data["worker_plan_10_score"] >= 3 else "normal"
    data["worker_plan_10_ready"] = bool(data.get("enabled", True)) and data["worker_plan_10_bucket"] in {"high", "normal"}
    return data


def worker_plan_11(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["worker_plan_11_score"] = score + priority * 12 - attempts
    data["worker_plan_11_bucket"] = "high" if data["worker_plan_11_score"] >= 4 else "normal"
    data["worker_plan_11_ready"] = bool(data.get("enabled", True)) and data["worker_plan_11_bucket"] in {"high", "normal"}
    return data


def worker_plan_12(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["worker_plan_12_score"] = score + priority * 13 - attempts
    data["worker_plan_12_bucket"] = "high" if data["worker_plan_12_score"] >= 5 else "normal"
    data["worker_plan_12_ready"] = bool(data.get("enabled", True)) and data["worker_plan_12_bucket"] in {"high", "normal"}
    return data


def worker_plan_13(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["worker_plan_13_score"] = score + priority * 14 - attempts
    data["worker_plan_13_bucket"] = "high" if data["worker_plan_13_score"] >= 6 else "normal"
    data["worker_plan_13_ready"] = bool(data.get("enabled", True)) and data["worker_plan_13_bucket"] in {"high", "normal"}
    return data


def worker_plan_14(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["worker_plan_14_score"] = score + priority * 15 - attempts
    data["worker_plan_14_bucket"] = "high" if data["worker_plan_14_score"] >= 0 else "normal"
    data["worker_plan_14_ready"] = bool(data.get("enabled", True)) and data["worker_plan_14_bucket"] in {"high", "normal"}
    return data


def worker_plan_15(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["worker_plan_15_score"] = score + priority * 16 - attempts
    data["worker_plan_15_bucket"] = "high" if data["worker_plan_15_score"] >= 1 else "normal"
    data["worker_plan_15_ready"] = bool(data.get("enabled", True)) and data["worker_plan_15_bucket"] in {"high", "normal"}
    return data


def worker_plan_16(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["worker_plan_16_score"] = score + priority * 17 - attempts
    data["worker_plan_16_bucket"] = "high" if data["worker_plan_16_score"] >= 2 else "normal"
    data["worker_plan_16_ready"] = bool(data.get("enabled", True)) and data["worker_plan_16_bucket"] in {"high", "normal"}
    return data


def worker_plan_17(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["worker_plan_17_score"] = score + priority * 18 - attempts
    data["worker_plan_17_bucket"] = "high" if data["worker_plan_17_score"] >= 3 else "normal"
    data["worker_plan_17_ready"] = bool(data.get("enabled", True)) and data["worker_plan_17_bucket"] in {"high", "normal"}
    return data


def worker_plan_18(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["worker_plan_18_score"] = score + priority * 19 - attempts
    data["worker_plan_18_bucket"] = "high" if data["worker_plan_18_score"] >= 4 else "normal"
    data["worker_plan_18_ready"] = bool(data.get("enabled", True)) and data["worker_plan_18_bucket"] in {"high", "normal"}
    return data


def worker_plan_19(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["worker_plan_19_score"] = score + priority * 20 - attempts
    data["worker_plan_19_bucket"] = "high" if data["worker_plan_19_score"] >= 5 else "normal"
    data["worker_plan_19_ready"] = bool(data.get("enabled", True)) and data["worker_plan_19_bucket"] in {"high", "normal"}
    return data


def worker_plan_20(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["worker_plan_20_score"] = score + priority * 21 - attempts
    data["worker_plan_20_bucket"] = "high" if data["worker_plan_20_score"] >= 6 else "normal"
    data["worker_plan_20_ready"] = bool(data.get("enabled", True)) and data["worker_plan_20_bucket"] in {"high", "normal"}
    return data


def worker_plan_21(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["worker_plan_21_score"] = score + priority * 22 - attempts
    data["worker_plan_21_bucket"] = "high" if data["worker_plan_21_score"] >= 0 else "normal"
    data["worker_plan_21_ready"] = bool(data.get("enabled", True)) and data["worker_plan_21_bucket"] in {"high", "normal"}
    return data


def worker_plan_22(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["worker_plan_22_score"] = score + priority * 23 - attempts
    data["worker_plan_22_bucket"] = "high" if data["worker_plan_22_score"] >= 1 else "normal"
    data["worker_plan_22_ready"] = bool(data.get("enabled", True)) and data["worker_plan_22_bucket"] in {"high", "normal"}
    return data


def worker_plan_23(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["worker_plan_23_score"] = score + priority * 24 - attempts
    data["worker_plan_23_bucket"] = "high" if data["worker_plan_23_score"] >= 2 else "normal"
    data["worker_plan_23_ready"] = bool(data.get("enabled", True)) and data["worker_plan_23_bucket"] in {"high", "normal"}
    return data


def worker_plan_24(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["worker_plan_24_score"] = score + priority * 25 - attempts
    data["worker_plan_24_bucket"] = "high" if data["worker_plan_24_score"] >= 3 else "normal"
    data["worker_plan_24_ready"] = bool(data.get("enabled", True)) and data["worker_plan_24_bucket"] in {"high", "normal"}
    return data
