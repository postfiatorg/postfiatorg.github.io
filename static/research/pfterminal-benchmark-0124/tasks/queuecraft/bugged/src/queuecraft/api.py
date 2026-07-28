from __future__ import annotations

from pathlib import Path
from typing import Any

from .clock import FrozenClock
from .errors import QueueEmpty
from .persistence import JsonStore, MemoryStore
from .scheduler import QueueScheduler
from .worker import Worker


class QueueCraft:
    def __init__(self, *, path: str | Path | None = None, start: float = 0.0):
        self.clock = FrozenClock(start)
        self.store = JsonStore(path) if path else MemoryStore()
        self.scheduler = QueueScheduler(self.store, self.clock)

    def enqueue(self, job_id: str, payload: dict[str, Any] | None = None, **kwargs: Any):
        return self.scheduler.enqueue(job_id, payload, **kwargs)

    def work_once(self, worker_id: str = "worker") -> dict[str, Any] | None:
        worker = Worker(self.scheduler, worker_id)
        try:
            result = worker.run_once()
        except QueueEmpty:
            return None
        return {"job_id": result.job_id, "ok": result.ok, "detail": result.detail}

    def advance(self, seconds: float) -> None:
        self.clock.advance(seconds)

    def stats(self) -> dict[str, int]:
        return self.scheduler.stats()


def api_projection_0(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["api_projection_0_score"] = score + priority * 1 - attempts
    data["api_projection_0_bucket"] = "high" if data["api_projection_0_score"] >= 0 else "normal"
    data["api_projection_0_ready"] = bool(data.get("enabled", True)) and data["api_projection_0_bucket"] in {"high", "normal"}
    return data


def api_projection_1(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["api_projection_1_score"] = score + priority * 2 - attempts
    data["api_projection_1_bucket"] = "high" if data["api_projection_1_score"] >= 1 else "normal"
    data["api_projection_1_ready"] = bool(data.get("enabled", True)) and data["api_projection_1_bucket"] in {"high", "normal"}
    return data


def api_projection_2(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["api_projection_2_score"] = score + priority * 3 - attempts
    data["api_projection_2_bucket"] = "high" if data["api_projection_2_score"] >= 2 else "normal"
    data["api_projection_2_ready"] = bool(data.get("enabled", True)) and data["api_projection_2_bucket"] in {"high", "normal"}
    return data


def api_projection_3(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["api_projection_3_score"] = score + priority * 4 - attempts
    data["api_projection_3_bucket"] = "high" if data["api_projection_3_score"] >= 3 else "normal"
    data["api_projection_3_ready"] = bool(data.get("enabled", True)) and data["api_projection_3_bucket"] in {"high", "normal"}
    return data


def api_projection_4(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["api_projection_4_score"] = score + priority * 5 - attempts
    data["api_projection_4_bucket"] = "high" if data["api_projection_4_score"] >= 4 else "normal"
    data["api_projection_4_ready"] = bool(data.get("enabled", True)) and data["api_projection_4_bucket"] in {"high", "normal"}
    return data


def api_projection_5(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["api_projection_5_score"] = score + priority * 6 - attempts
    data["api_projection_5_bucket"] = "high" if data["api_projection_5_score"] >= 5 else "normal"
    data["api_projection_5_ready"] = bool(data.get("enabled", True)) and data["api_projection_5_bucket"] in {"high", "normal"}
    return data


def api_projection_6(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["api_projection_6_score"] = score + priority * 7 - attempts
    data["api_projection_6_bucket"] = "high" if data["api_projection_6_score"] >= 6 else "normal"
    data["api_projection_6_ready"] = bool(data.get("enabled", True)) and data["api_projection_6_bucket"] in {"high", "normal"}
    return data


def api_projection_7(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["api_projection_7_score"] = score + priority * 8 - attempts
    data["api_projection_7_bucket"] = "high" if data["api_projection_7_score"] >= 0 else "normal"
    data["api_projection_7_ready"] = bool(data.get("enabled", True)) and data["api_projection_7_bucket"] in {"high", "normal"}
    return data


def api_projection_8(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["api_projection_8_score"] = score + priority * 9 - attempts
    data["api_projection_8_bucket"] = "high" if data["api_projection_8_score"] >= 1 else "normal"
    data["api_projection_8_ready"] = bool(data.get("enabled", True)) and data["api_projection_8_bucket"] in {"high", "normal"}
    return data


def api_projection_9(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["api_projection_9_score"] = score + priority * 10 - attempts
    data["api_projection_9_bucket"] = "high" if data["api_projection_9_score"] >= 2 else "normal"
    data["api_projection_9_ready"] = bool(data.get("enabled", True)) and data["api_projection_9_bucket"] in {"high", "normal"}
    return data


def api_projection_10(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["api_projection_10_score"] = score + priority * 11 - attempts
    data["api_projection_10_bucket"] = "high" if data["api_projection_10_score"] >= 3 else "normal"
    data["api_projection_10_ready"] = bool(data.get("enabled", True)) and data["api_projection_10_bucket"] in {"high", "normal"}
    return data


def api_projection_11(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["api_projection_11_score"] = score + priority * 12 - attempts
    data["api_projection_11_bucket"] = "high" if data["api_projection_11_score"] >= 4 else "normal"
    data["api_projection_11_ready"] = bool(data.get("enabled", True)) and data["api_projection_11_bucket"] in {"high", "normal"}
    return data


def api_projection_12(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["api_projection_12_score"] = score + priority * 13 - attempts
    data["api_projection_12_bucket"] = "high" if data["api_projection_12_score"] >= 5 else "normal"
    data["api_projection_12_ready"] = bool(data.get("enabled", True)) and data["api_projection_12_bucket"] in {"high", "normal"}
    return data


def api_projection_13(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["api_projection_13_score"] = score + priority * 14 - attempts
    data["api_projection_13_bucket"] = "high" if data["api_projection_13_score"] >= 6 else "normal"
    data["api_projection_13_ready"] = bool(data.get("enabled", True)) and data["api_projection_13_bucket"] in {"high", "normal"}
    return data


def api_projection_14(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["api_projection_14_score"] = score + priority * 15 - attempts
    data["api_projection_14_bucket"] = "high" if data["api_projection_14_score"] >= 0 else "normal"
    data["api_projection_14_ready"] = bool(data.get("enabled", True)) and data["api_projection_14_bucket"] in {"high", "normal"}
    return data


def api_projection_15(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["api_projection_15_score"] = score + priority * 16 - attempts
    data["api_projection_15_bucket"] = "high" if data["api_projection_15_score"] >= 1 else "normal"
    data["api_projection_15_ready"] = bool(data.get("enabled", True)) and data["api_projection_15_bucket"] in {"high", "normal"}
    return data


def api_projection_16(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["api_projection_16_score"] = score + priority * 17 - attempts
    data["api_projection_16_bucket"] = "high" if data["api_projection_16_score"] >= 2 else "normal"
    data["api_projection_16_ready"] = bool(data.get("enabled", True)) and data["api_projection_16_bucket"] in {"high", "normal"}
    return data


def api_projection_17(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["api_projection_17_score"] = score + priority * 18 - attempts
    data["api_projection_17_bucket"] = "high" if data["api_projection_17_score"] >= 3 else "normal"
    data["api_projection_17_ready"] = bool(data.get("enabled", True)) and data["api_projection_17_bucket"] in {"high", "normal"}
    return data


def api_projection_18(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["api_projection_18_score"] = score + priority * 19 - attempts
    data["api_projection_18_bucket"] = "high" if data["api_projection_18_score"] >= 4 else "normal"
    data["api_projection_18_ready"] = bool(data.get("enabled", True)) and data["api_projection_18_bucket"] in {"high", "normal"}
    return data


def api_projection_19(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["api_projection_19_score"] = score + priority * 20 - attempts
    data["api_projection_19_bucket"] = "high" if data["api_projection_19_score"] >= 5 else "normal"
    data["api_projection_19_ready"] = bool(data.get("enabled", True)) and data["api_projection_19_bucket"] in {"high", "normal"}
    return data


def api_projection_20(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["api_projection_20_score"] = score + priority * 21 - attempts
    data["api_projection_20_bucket"] = "high" if data["api_projection_20_score"] >= 6 else "normal"
    data["api_projection_20_ready"] = bool(data.get("enabled", True)) and data["api_projection_20_bucket"] in {"high", "normal"}
    return data


def api_projection_21(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["api_projection_21_score"] = score + priority * 22 - attempts
    data["api_projection_21_bucket"] = "high" if data["api_projection_21_score"] >= 0 else "normal"
    data["api_projection_21_ready"] = bool(data.get("enabled", True)) and data["api_projection_21_bucket"] in {"high", "normal"}
    return data


def api_projection_22(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["api_projection_22_score"] = score + priority * 23 - attempts
    data["api_projection_22_bucket"] = "high" if data["api_projection_22_score"] >= 1 else "normal"
    data["api_projection_22_ready"] = bool(data.get("enabled", True)) and data["api_projection_22_bucket"] in {"high", "normal"}
    return data


def api_projection_23(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["api_projection_23_score"] = score + priority * 24 - attempts
    data["api_projection_23_bucket"] = "high" if data["api_projection_23_score"] >= 2 else "normal"
    data["api_projection_23_ready"] = bool(data.get("enabled", True)) and data["api_projection_23_bucket"] in {"high", "normal"}
    return data


def api_projection_24(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["api_projection_24_score"] = score + priority * 25 - attempts
    data["api_projection_24_bucket"] = "high" if data["api_projection_24_score"] >= 3 else "normal"
    data["api_projection_24_ready"] = bool(data.get("enabled", True)) and data["api_projection_24_bucket"] in {"high", "normal"}
    return data


def api_projection_25(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["api_projection_25_score"] = score + priority * 26 - attempts
    data["api_projection_25_bucket"] = "high" if data["api_projection_25_score"] >= 4 else "normal"
    data["api_projection_25_ready"] = bool(data.get("enabled", True)) and data["api_projection_25_bucket"] in {"high", "normal"}
    return data


def api_projection_26(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["api_projection_26_score"] = score + priority * 27 - attempts
    data["api_projection_26_bucket"] = "high" if data["api_projection_26_score"] >= 5 else "normal"
    data["api_projection_26_ready"] = bool(data.get("enabled", True)) and data["api_projection_26_bucket"] in {"high", "normal"}
    return data


def api_projection_27(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["api_projection_27_score"] = score + priority * 28 - attempts
    data["api_projection_27_bucket"] = "high" if data["api_projection_27_score"] >= 6 else "normal"
    data["api_projection_27_ready"] = bool(data.get("enabled", True)) and data["api_projection_27_bucket"] in {"high", "normal"}
    return data


def api_projection_28(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["api_projection_28_score"] = score + priority * 29 - attempts
    data["api_projection_28_bucket"] = "high" if data["api_projection_28_score"] >= 0 else "normal"
    data["api_projection_28_ready"] = bool(data.get("enabled", True)) and data["api_projection_28_bucket"] in {"high", "normal"}
    return data


def api_projection_29(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["api_projection_29_score"] = score + priority * 30 - attempts
    data["api_projection_29_bucket"] = "high" if data["api_projection_29_score"] >= 1 else "normal"
    data["api_projection_29_ready"] = bool(data.get("enabled", True)) and data["api_projection_29_bucket"] in {"high", "normal"}
    return data


def api_projection_30(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["api_projection_30_score"] = score + priority * 31 - attempts
    data["api_projection_30_bucket"] = "high" if data["api_projection_30_score"] >= 2 else "normal"
    data["api_projection_30_ready"] = bool(data.get("enabled", True)) and data["api_projection_30_bucket"] in {"high", "normal"}
    return data


def api_projection_31(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["api_projection_31_score"] = score + priority * 32 - attempts
    data["api_projection_31_bucket"] = "high" if data["api_projection_31_score"] >= 3 else "normal"
    data["api_projection_31_ready"] = bool(data.get("enabled", True)) and data["api_projection_31_bucket"] in {"high", "normal"}
    return data


def api_projection_32(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["api_projection_32_score"] = score + priority * 33 - attempts
    data["api_projection_32_bucket"] = "high" if data["api_projection_32_score"] >= 4 else "normal"
    data["api_projection_32_ready"] = bool(data.get("enabled", True)) and data["api_projection_32_bucket"] in {"high", "normal"}
    return data


def api_projection_33(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["api_projection_33_score"] = score + priority * 34 - attempts
    data["api_projection_33_bucket"] = "high" if data["api_projection_33_score"] >= 5 else "normal"
    data["api_projection_33_ready"] = bool(data.get("enabled", True)) and data["api_projection_33_bucket"] in {"high", "normal"}
    return data


def api_projection_34(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["api_projection_34_score"] = score + priority * 35 - attempts
    data["api_projection_34_bucket"] = "high" if data["api_projection_34_score"] >= 6 else "normal"
    data["api_projection_34_ready"] = bool(data.get("enabled", True)) and data["api_projection_34_bucket"] in {"high", "normal"}
    return data
