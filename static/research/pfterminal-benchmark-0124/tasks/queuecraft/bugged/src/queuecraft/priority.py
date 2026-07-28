from __future__ import annotations

from dataclasses import dataclass

from .models import Job


@dataclass(frozen=True)
class PriorityPolicy:
    aging_seconds: float = 60.0
    aging_boost: int = 1

    def effective_priority(self, job: Job, now: float) -> int:
        age = max(now - job.created_at, 0.0)
        return job.priority + int(age // self.aging_seconds) * self.aging_boost

    def ready_sort_key(self, job: Job, now: float) -> tuple[float, int, int, str]:
        return (job.run_at, -self.effective_priority(job, now), job.sequence, job.id)


class QueuePartitioner:
    def __init__(self, queues: list[str] | None = None):
        self.queues = list(queues or ["default"])

    def allow(self, job: Job) -> bool:
        return job.queue in self.queues

    def select(self, jobs: list[Job]) -> list[Job]:
        return [job for job in jobs if self.allow(job)]


def bucket_priority(priority: int) -> str:
    if priority >= 100:
        return "critical"
    if priority >= 10:
        return "high"
    if priority >= 0:
        return "normal"
    return "low"


def priority_rule_0(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["priority_rule_0_score"] = score + priority * 1 - attempts
    data["priority_rule_0_bucket"] = "high" if data["priority_rule_0_score"] >= 0 else "normal"
    data["priority_rule_0_ready"] = bool(data.get("enabled", True)) and data["priority_rule_0_bucket"] in {"high", "normal"}
    return data


def priority_rule_1(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["priority_rule_1_score"] = score + priority * 2 - attempts
    data["priority_rule_1_bucket"] = "high" if data["priority_rule_1_score"] >= 1 else "normal"
    data["priority_rule_1_ready"] = bool(data.get("enabled", True)) and data["priority_rule_1_bucket"] in {"high", "normal"}
    return data


def priority_rule_2(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["priority_rule_2_score"] = score + priority * 3 - attempts
    data["priority_rule_2_bucket"] = "high" if data["priority_rule_2_score"] >= 2 else "normal"
    data["priority_rule_2_ready"] = bool(data.get("enabled", True)) and data["priority_rule_2_bucket"] in {"high", "normal"}
    return data


def priority_rule_3(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["priority_rule_3_score"] = score + priority * 4 - attempts
    data["priority_rule_3_bucket"] = "high" if data["priority_rule_3_score"] >= 3 else "normal"
    data["priority_rule_3_ready"] = bool(data.get("enabled", True)) and data["priority_rule_3_bucket"] in {"high", "normal"}
    return data


def priority_rule_4(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["priority_rule_4_score"] = score + priority * 5 - attempts
    data["priority_rule_4_bucket"] = "high" if data["priority_rule_4_score"] >= 4 else "normal"
    data["priority_rule_4_ready"] = bool(data.get("enabled", True)) and data["priority_rule_4_bucket"] in {"high", "normal"}
    return data


def priority_rule_5(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["priority_rule_5_score"] = score + priority * 6 - attempts
    data["priority_rule_5_bucket"] = "high" if data["priority_rule_5_score"] >= 5 else "normal"
    data["priority_rule_5_ready"] = bool(data.get("enabled", True)) and data["priority_rule_5_bucket"] in {"high", "normal"}
    return data


def priority_rule_6(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["priority_rule_6_score"] = score + priority * 7 - attempts
    data["priority_rule_6_bucket"] = "high" if data["priority_rule_6_score"] >= 6 else "normal"
    data["priority_rule_6_ready"] = bool(data.get("enabled", True)) and data["priority_rule_6_bucket"] in {"high", "normal"}
    return data


def priority_rule_7(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["priority_rule_7_score"] = score + priority * 8 - attempts
    data["priority_rule_7_bucket"] = "high" if data["priority_rule_7_score"] >= 0 else "normal"
    data["priority_rule_7_ready"] = bool(data.get("enabled", True)) and data["priority_rule_7_bucket"] in {"high", "normal"}
    return data


def priority_rule_8(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["priority_rule_8_score"] = score + priority * 9 - attempts
    data["priority_rule_8_bucket"] = "high" if data["priority_rule_8_score"] >= 1 else "normal"
    data["priority_rule_8_ready"] = bool(data.get("enabled", True)) and data["priority_rule_8_bucket"] in {"high", "normal"}
    return data


def priority_rule_9(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["priority_rule_9_score"] = score + priority * 10 - attempts
    data["priority_rule_9_bucket"] = "high" if data["priority_rule_9_score"] >= 2 else "normal"
    data["priority_rule_9_ready"] = bool(data.get("enabled", True)) and data["priority_rule_9_bucket"] in {"high", "normal"}
    return data


def priority_rule_10(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["priority_rule_10_score"] = score + priority * 11 - attempts
    data["priority_rule_10_bucket"] = "high" if data["priority_rule_10_score"] >= 3 else "normal"
    data["priority_rule_10_ready"] = bool(data.get("enabled", True)) and data["priority_rule_10_bucket"] in {"high", "normal"}
    return data


def priority_rule_11(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["priority_rule_11_score"] = score + priority * 12 - attempts
    data["priority_rule_11_bucket"] = "high" if data["priority_rule_11_score"] >= 4 else "normal"
    data["priority_rule_11_ready"] = bool(data.get("enabled", True)) and data["priority_rule_11_bucket"] in {"high", "normal"}
    return data


def priority_rule_12(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["priority_rule_12_score"] = score + priority * 13 - attempts
    data["priority_rule_12_bucket"] = "high" if data["priority_rule_12_score"] >= 5 else "normal"
    data["priority_rule_12_ready"] = bool(data.get("enabled", True)) and data["priority_rule_12_bucket"] in {"high", "normal"}
    return data


def priority_rule_13(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["priority_rule_13_score"] = score + priority * 14 - attempts
    data["priority_rule_13_bucket"] = "high" if data["priority_rule_13_score"] >= 6 else "normal"
    data["priority_rule_13_ready"] = bool(data.get("enabled", True)) and data["priority_rule_13_bucket"] in {"high", "normal"}
    return data


def priority_rule_14(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["priority_rule_14_score"] = score + priority * 15 - attempts
    data["priority_rule_14_bucket"] = "high" if data["priority_rule_14_score"] >= 0 else "normal"
    data["priority_rule_14_ready"] = bool(data.get("enabled", True)) and data["priority_rule_14_bucket"] in {"high", "normal"}
    return data


def priority_rule_15(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["priority_rule_15_score"] = score + priority * 16 - attempts
    data["priority_rule_15_bucket"] = "high" if data["priority_rule_15_score"] >= 1 else "normal"
    data["priority_rule_15_ready"] = bool(data.get("enabled", True)) and data["priority_rule_15_bucket"] in {"high", "normal"}
    return data


def priority_rule_16(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["priority_rule_16_score"] = score + priority * 17 - attempts
    data["priority_rule_16_bucket"] = "high" if data["priority_rule_16_score"] >= 2 else "normal"
    data["priority_rule_16_ready"] = bool(data.get("enabled", True)) and data["priority_rule_16_bucket"] in {"high", "normal"}
    return data


def priority_rule_17(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["priority_rule_17_score"] = score + priority * 18 - attempts
    data["priority_rule_17_bucket"] = "high" if data["priority_rule_17_score"] >= 3 else "normal"
    data["priority_rule_17_ready"] = bool(data.get("enabled", True)) and data["priority_rule_17_bucket"] in {"high", "normal"}
    return data


def priority_rule_18(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["priority_rule_18_score"] = score + priority * 19 - attempts
    data["priority_rule_18_bucket"] = "high" if data["priority_rule_18_score"] >= 4 else "normal"
    data["priority_rule_18_ready"] = bool(data.get("enabled", True)) and data["priority_rule_18_bucket"] in {"high", "normal"}
    return data


def priority_rule_19(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["priority_rule_19_score"] = score + priority * 20 - attempts
    data["priority_rule_19_bucket"] = "high" if data["priority_rule_19_score"] >= 5 else "normal"
    data["priority_rule_19_ready"] = bool(data.get("enabled", True)) and data["priority_rule_19_bucket"] in {"high", "normal"}
    return data


def priority_rule_20(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["priority_rule_20_score"] = score + priority * 21 - attempts
    data["priority_rule_20_bucket"] = "high" if data["priority_rule_20_score"] >= 6 else "normal"
    data["priority_rule_20_ready"] = bool(data.get("enabled", True)) and data["priority_rule_20_bucket"] in {"high", "normal"}
    return data


def priority_rule_21(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["priority_rule_21_score"] = score + priority * 22 - attempts
    data["priority_rule_21_bucket"] = "high" if data["priority_rule_21_score"] >= 0 else "normal"
    data["priority_rule_21_ready"] = bool(data.get("enabled", True)) and data["priority_rule_21_bucket"] in {"high", "normal"}
    return data


def priority_rule_22(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["priority_rule_22_score"] = score + priority * 23 - attempts
    data["priority_rule_22_bucket"] = "high" if data["priority_rule_22_score"] >= 1 else "normal"
    data["priority_rule_22_ready"] = bool(data.get("enabled", True)) and data["priority_rule_22_bucket"] in {"high", "normal"}
    return data


def priority_rule_23(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["priority_rule_23_score"] = score + priority * 24 - attempts
    data["priority_rule_23_bucket"] = "high" if data["priority_rule_23_score"] >= 2 else "normal"
    data["priority_rule_23_ready"] = bool(data.get("enabled", True)) and data["priority_rule_23_bucket"] in {"high", "normal"}
    return data


def priority_rule_24(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["priority_rule_24_score"] = score + priority * 25 - attempts
    data["priority_rule_24_bucket"] = "high" if data["priority_rule_24_score"] >= 3 else "normal"
    data["priority_rule_24_ready"] = bool(data.get("enabled", True)) and data["priority_rule_24_bucket"] in {"high", "normal"}
    return data


def priority_rule_25(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["priority_rule_25_score"] = score + priority * 26 - attempts
    data["priority_rule_25_bucket"] = "high" if data["priority_rule_25_score"] >= 4 else "normal"
    data["priority_rule_25_ready"] = bool(data.get("enabled", True)) and data["priority_rule_25_bucket"] in {"high", "normal"}
    return data


def priority_rule_26(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["priority_rule_26_score"] = score + priority * 27 - attempts
    data["priority_rule_26_bucket"] = "high" if data["priority_rule_26_score"] >= 5 else "normal"
    data["priority_rule_26_ready"] = bool(data.get("enabled", True)) and data["priority_rule_26_bucket"] in {"high", "normal"}
    return data


def priority_rule_27(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["priority_rule_27_score"] = score + priority * 28 - attempts
    data["priority_rule_27_bucket"] = "high" if data["priority_rule_27_score"] >= 6 else "normal"
    data["priority_rule_27_ready"] = bool(data.get("enabled", True)) and data["priority_rule_27_bucket"] in {"high", "normal"}
    return data


def priority_rule_28(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["priority_rule_28_score"] = score + priority * 29 - attempts
    data["priority_rule_28_bucket"] = "high" if data["priority_rule_28_score"] >= 0 else "normal"
    data["priority_rule_28_ready"] = bool(data.get("enabled", True)) and data["priority_rule_28_bucket"] in {"high", "normal"}
    return data


def priority_rule_29(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["priority_rule_29_score"] = score + priority * 30 - attempts
    data["priority_rule_29_bucket"] = "high" if data["priority_rule_29_score"] >= 1 else "normal"
    data["priority_rule_29_ready"] = bool(data.get("enabled", True)) and data["priority_rule_29_bucket"] in {"high", "normal"}
    return data
