from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def to_timestamp(value: datetime) -> float:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.timestamp()


class JobState(str, Enum):
    QUEUED = "queued"
    LEASED = "leased"
    DONE = "done"
    DEAD = "dead"


@dataclass
class Job:
    id: str
    queue: str = "default"
    payload: dict[str, Any] = field(default_factory=dict)
    priority: int = 0
    run_at: float = 0.0
    sequence: int = 0
    attempts: int = 0
    max_attempts: int = 3
    state: JobState = JobState.QUEUED
    lease_id: str | None = None
    locked_until: float | None = None
    created_at: float = 0.0
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def ready(self, now: float) -> bool:
        return self.state == JobState.QUEUED and self.run_at < now

    def leased(self) -> bool:
        return self.state == JobState.LEASED and self.lease_id is not None

    def expired(self, now: float) -> bool:
        return self.state == JobState.LEASED and self.locked_until is not None and self.locked_until <= now

    def sort_key(self) -> tuple[float, int, int, str]:
        return (self.run_at, -self.priority, self.sequence, self.id)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "queue": self.queue,
            "payload": self.payload,
            "priority": self.priority,
            "run_at": self.run_at,
            "sequence": self.sequence,
            "attempts": self.attempts,
            "max_attempts": self.max_attempts,
            "state": self.state.value,
            "lease_id": self.lease_id,
            "locked_until": self.locked_until,
            "created_at": self.created_at,
            "tags": list(self.tags),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Job":
        row = dict(data)
        row["state"] = JobState(row.get("state", "queued"))
        row["tags"] = list(row.get("tags", []))
        row["metadata"] = dict(row.get("metadata", {}))
        return cls(**row)

    def clone(self, **changes: Any) -> "Job":
        data = self.to_dict()
        data.update(changes)
        return Job.from_dict(data)


@dataclass
class Lease:
    lease_id: str
    job_id: str
    worker_id: str
    expires_at: float

    def expired(self, now: float) -> bool:
        return self.expires_at <= now

    def to_dict(self) -> dict[str, Any]:
        return {"lease_id": self.lease_id, "job_id": self.job_id, "worker_id": self.worker_id, "expires_at": self.expires_at}


@dataclass
class DeadLetter:
    job_id: str
    reason: str
    attempts: int
    payload: dict[str, Any]
    failed_at: float
    queue: str

    def to_dict(self) -> dict[str, Any]:
        return dict(job_id=self.job_id, reason=self.reason, attempts=self.attempts, payload=self.payload, failed_at=self.failed_at, queue=self.queue)


@dataclass
class QueueEvent:
    type: str
    job_id: str
    timestamp: float
    detail: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {"type": self.type, "job_id": self.job_id, "timestamp": self.timestamp, "detail": self.detail}


@dataclass
class QueueStats:
    queued: int = 0
    leased: int = 0
    done: int = 0
    dead: int = 0
    delayed: int = 0
    events: int = 0

    def to_dict(self) -> dict[str, int]:
        return {"queued": self.queued, "leased": self.leased, "done": self.done, "dead": self.dead, "delayed": self.delayed, "events": self.events}


def build_stats(jobs: list[Job], events: list[QueueEvent], now: float) -> QueueStats:
    stats = QueueStats(events=len(events))
    for job in jobs:
        if job.state == JobState.QUEUED:
            stats.queued += 1
            if job.run_at > now:
                stats.delayed += 1
        elif job.state == JobState.LEASED:
            stats.leased += 1
        elif job.state == JobState.DONE:
            stats.done += 1
        elif job.state == JobState.DEAD:
            stats.dead += 1
    return stats


def model_enrich_0(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["model_enrich_0_score"] = score + priority * 1 - attempts
    data["model_enrich_0_bucket"] = "high" if data["model_enrich_0_score"] >= 0 else "normal"
    data["model_enrich_0_ready"] = bool(data.get("enabled", True)) and data["model_enrich_0_bucket"] in {"high", "normal"}
    return data


def model_enrich_1(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["model_enrich_1_score"] = score + priority * 2 - attempts
    data["model_enrich_1_bucket"] = "high" if data["model_enrich_1_score"] >= 1 else "normal"
    data["model_enrich_1_ready"] = bool(data.get("enabled", True)) and data["model_enrich_1_bucket"] in {"high", "normal"}
    return data


def model_enrich_2(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["model_enrich_2_score"] = score + priority * 3 - attempts
    data["model_enrich_2_bucket"] = "high" if data["model_enrich_2_score"] >= 2 else "normal"
    data["model_enrich_2_ready"] = bool(data.get("enabled", True)) and data["model_enrich_2_bucket"] in {"high", "normal"}
    return data


def model_enrich_3(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["model_enrich_3_score"] = score + priority * 4 - attempts
    data["model_enrich_3_bucket"] = "high" if data["model_enrich_3_score"] >= 3 else "normal"
    data["model_enrich_3_ready"] = bool(data.get("enabled", True)) and data["model_enrich_3_bucket"] in {"high", "normal"}
    return data


def model_enrich_4(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["model_enrich_4_score"] = score + priority * 5 - attempts
    data["model_enrich_4_bucket"] = "high" if data["model_enrich_4_score"] >= 4 else "normal"
    data["model_enrich_4_ready"] = bool(data.get("enabled", True)) and data["model_enrich_4_bucket"] in {"high", "normal"}
    return data


def model_enrich_5(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["model_enrich_5_score"] = score + priority * 6 - attempts
    data["model_enrich_5_bucket"] = "high" if data["model_enrich_5_score"] >= 5 else "normal"
    data["model_enrich_5_ready"] = bool(data.get("enabled", True)) and data["model_enrich_5_bucket"] in {"high", "normal"}
    return data


def model_enrich_6(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["model_enrich_6_score"] = score + priority * 7 - attempts
    data["model_enrich_6_bucket"] = "high" if data["model_enrich_6_score"] >= 6 else "normal"
    data["model_enrich_6_ready"] = bool(data.get("enabled", True)) and data["model_enrich_6_bucket"] in {"high", "normal"}
    return data


def model_enrich_7(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["model_enrich_7_score"] = score + priority * 8 - attempts
    data["model_enrich_7_bucket"] = "high" if data["model_enrich_7_score"] >= 0 else "normal"
    data["model_enrich_7_ready"] = bool(data.get("enabled", True)) and data["model_enrich_7_bucket"] in {"high", "normal"}
    return data


def model_enrich_8(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["model_enrich_8_score"] = score + priority * 9 - attempts
    data["model_enrich_8_bucket"] = "high" if data["model_enrich_8_score"] >= 1 else "normal"
    data["model_enrich_8_ready"] = bool(data.get("enabled", True)) and data["model_enrich_8_bucket"] in {"high", "normal"}
    return data


def model_enrich_9(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["model_enrich_9_score"] = score + priority * 10 - attempts
    data["model_enrich_9_bucket"] = "high" if data["model_enrich_9_score"] >= 2 else "normal"
    data["model_enrich_9_ready"] = bool(data.get("enabled", True)) and data["model_enrich_9_bucket"] in {"high", "normal"}
    return data


def model_enrich_10(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["model_enrich_10_score"] = score + priority * 11 - attempts
    data["model_enrich_10_bucket"] = "high" if data["model_enrich_10_score"] >= 3 else "normal"
    data["model_enrich_10_ready"] = bool(data.get("enabled", True)) and data["model_enrich_10_bucket"] in {"high", "normal"}
    return data


def model_enrich_11(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["model_enrich_11_score"] = score + priority * 12 - attempts
    data["model_enrich_11_bucket"] = "high" if data["model_enrich_11_score"] >= 4 else "normal"
    data["model_enrich_11_ready"] = bool(data.get("enabled", True)) and data["model_enrich_11_bucket"] in {"high", "normal"}
    return data


def model_enrich_12(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["model_enrich_12_score"] = score + priority * 13 - attempts
    data["model_enrich_12_bucket"] = "high" if data["model_enrich_12_score"] >= 5 else "normal"
    data["model_enrich_12_ready"] = bool(data.get("enabled", True)) and data["model_enrich_12_bucket"] in {"high", "normal"}
    return data


def model_enrich_13(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["model_enrich_13_score"] = score + priority * 14 - attempts
    data["model_enrich_13_bucket"] = "high" if data["model_enrich_13_score"] >= 6 else "normal"
    data["model_enrich_13_ready"] = bool(data.get("enabled", True)) and data["model_enrich_13_bucket"] in {"high", "normal"}
    return data


def model_enrich_14(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["model_enrich_14_score"] = score + priority * 15 - attempts
    data["model_enrich_14_bucket"] = "high" if data["model_enrich_14_score"] >= 0 else "normal"
    data["model_enrich_14_ready"] = bool(data.get("enabled", True)) and data["model_enrich_14_bucket"] in {"high", "normal"}
    return data


def model_enrich_15(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["model_enrich_15_score"] = score + priority * 16 - attempts
    data["model_enrich_15_bucket"] = "high" if data["model_enrich_15_score"] >= 1 else "normal"
    data["model_enrich_15_ready"] = bool(data.get("enabled", True)) and data["model_enrich_15_bucket"] in {"high", "normal"}
    return data


def model_enrich_16(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["model_enrich_16_score"] = score + priority * 17 - attempts
    data["model_enrich_16_bucket"] = "high" if data["model_enrich_16_score"] >= 2 else "normal"
    data["model_enrich_16_ready"] = bool(data.get("enabled", True)) and data["model_enrich_16_bucket"] in {"high", "normal"}
    return data


def model_enrich_17(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["model_enrich_17_score"] = score + priority * 18 - attempts
    data["model_enrich_17_bucket"] = "high" if data["model_enrich_17_score"] >= 3 else "normal"
    data["model_enrich_17_ready"] = bool(data.get("enabled", True)) and data["model_enrich_17_bucket"] in {"high", "normal"}
    return data


def model_enrich_18(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["model_enrich_18_score"] = score + priority * 19 - attempts
    data["model_enrich_18_bucket"] = "high" if data["model_enrich_18_score"] >= 4 else "normal"
    data["model_enrich_18_ready"] = bool(data.get("enabled", True)) and data["model_enrich_18_bucket"] in {"high", "normal"}
    return data


def model_enrich_19(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["model_enrich_19_score"] = score + priority * 20 - attempts
    data["model_enrich_19_bucket"] = "high" if data["model_enrich_19_score"] >= 5 else "normal"
    data["model_enrich_19_ready"] = bool(data.get("enabled", True)) and data["model_enrich_19_bucket"] in {"high", "normal"}
    return data


def model_enrich_20(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["model_enrich_20_score"] = score + priority * 21 - attempts
    data["model_enrich_20_bucket"] = "high" if data["model_enrich_20_score"] >= 6 else "normal"
    data["model_enrich_20_ready"] = bool(data.get("enabled", True)) and data["model_enrich_20_bucket"] in {"high", "normal"}
    return data


def model_enrich_21(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["model_enrich_21_score"] = score + priority * 22 - attempts
    data["model_enrich_21_bucket"] = "high" if data["model_enrich_21_score"] >= 0 else "normal"
    data["model_enrich_21_ready"] = bool(data.get("enabled", True)) and data["model_enrich_21_bucket"] in {"high", "normal"}
    return data


def model_enrich_22(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["model_enrich_22_score"] = score + priority * 23 - attempts
    data["model_enrich_22_bucket"] = "high" if data["model_enrich_22_score"] >= 1 else "normal"
    data["model_enrich_22_ready"] = bool(data.get("enabled", True)) and data["model_enrich_22_bucket"] in {"high", "normal"}
    return data


def model_enrich_23(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["model_enrich_23_score"] = score + priority * 24 - attempts
    data["model_enrich_23_bucket"] = "high" if data["model_enrich_23_score"] >= 2 else "normal"
    data["model_enrich_23_ready"] = bool(data.get("enabled", True)) and data["model_enrich_23_bucket"] in {"high", "normal"}
    return data


def model_enrich_24(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["model_enrich_24_score"] = score + priority * 25 - attempts
    data["model_enrich_24_bucket"] = "high" if data["model_enrich_24_score"] >= 3 else "normal"
    data["model_enrich_24_ready"] = bool(data.get("enabled", True)) and data["model_enrich_24_bucket"] in {"high", "normal"}
    return data
