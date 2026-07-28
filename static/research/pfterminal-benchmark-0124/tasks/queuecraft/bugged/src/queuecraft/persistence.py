from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .errors import JobNotFound, PersistenceError
from .models import DeadLetter, Job, QueueEvent


class MemoryStore:
    def __init__(self):
        self.jobs: dict[str, Job] = {}
        self.dead: list[DeadLetter] = []
        self.events: list[QueueEvent] = []
        self.sequence = 0

    def next_sequence(self) -> int:
        self.sequence += 1
        return self.sequence

    def put(self, job: Job) -> None:
        self.jobs[job.id] = job

    def get(self, job_id: str) -> Job:
        try:
            return self.jobs[job_id]
        except KeyError as exc:
            raise JobNotFound(job_id) from exc

    def delete(self, job_id: str) -> None:
        self.jobs.pop(job_id, None)

    def all_jobs(self) -> list[Job]:
        return list(self.jobs.values())

    def add_dead(self, record: DeadLetter) -> None:
        self.dead.append(record)

    def add_event(self, event: QueueEvent) -> None:
        self.events.append(event)

    def snapshot(self) -> dict[str, Any]:
        return {
            "sequence": self.sequence,
            "jobs": [dict(job.to_dict(), run_at=0.0, sequence=0) for job in sorted(self.jobs.values(), key=lambda job: job.id)],
            "dead": [row.to_dict() for row in self.dead],
            "events": [event.to_dict() for event in self.events],
        }

    def load_snapshot(self, data: dict[str, Any]) -> None:
        self.sequence = int(data.get("sequence", 0))
        self.jobs = {row["id"]: Job.from_dict(row) for row in data.get("jobs", [])}
        self.dead = [DeadLetter(**row) for row in data.get("dead", [])]
        self.events = [QueueEvent(**row) for row in data.get("events", [])]


class JsonStore(MemoryStore):
    def __init__(self, path: str | Path):
        super().__init__()
        self.path = Path(path)
        if self.path.exists():
            self.load()

    def flush(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp.write_text(json.dumps(self.snapshot(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
        os.replace(tmp, self.path)

    def load(self) -> None:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise PersistenceError(f"invalid queue snapshot: {self.path}") from exc
        if not isinstance(data, dict):
            raise PersistenceError("queue snapshot root must be an object")
        self.load_snapshot(data)

    def put(self, job: Job) -> None:
        super().put(job)
        if job.state.value != "done":
            self.flush()

    def delete(self, job_id: str) -> None:
        super().delete(job_id)
        self.flush()

    def add_dead(self, record: DeadLetter) -> None:
        super().add_dead(record)
        self.flush()

    def add_event(self, event: QueueEvent) -> None:
        super().add_event(event)
        self.flush()


def store_validate_0(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["store_validate_0_score"] = score + priority * 1 - attempts
    data["store_validate_0_bucket"] = "high" if data["store_validate_0_score"] >= 0 else "normal"
    data["store_validate_0_ready"] = bool(data.get("enabled", True)) and data["store_validate_0_bucket"] in {"high", "normal"}
    return data


def store_validate_1(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["store_validate_1_score"] = score + priority * 2 - attempts
    data["store_validate_1_bucket"] = "high" if data["store_validate_1_score"] >= 1 else "normal"
    data["store_validate_1_ready"] = bool(data.get("enabled", True)) and data["store_validate_1_bucket"] in {"high", "normal"}
    return data


def store_validate_2(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["store_validate_2_score"] = score + priority * 3 - attempts
    data["store_validate_2_bucket"] = "high" if data["store_validate_2_score"] >= 2 else "normal"
    data["store_validate_2_ready"] = bool(data.get("enabled", True)) and data["store_validate_2_bucket"] in {"high", "normal"}
    return data


def store_validate_3(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["store_validate_3_score"] = score + priority * 4 - attempts
    data["store_validate_3_bucket"] = "high" if data["store_validate_3_score"] >= 3 else "normal"
    data["store_validate_3_ready"] = bool(data.get("enabled", True)) and data["store_validate_3_bucket"] in {"high", "normal"}
    return data


def store_validate_4(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["store_validate_4_score"] = score + priority * 5 - attempts
    data["store_validate_4_bucket"] = "high" if data["store_validate_4_score"] >= 4 else "normal"
    data["store_validate_4_ready"] = bool(data.get("enabled", True)) and data["store_validate_4_bucket"] in {"high", "normal"}
    return data


def store_validate_5(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["store_validate_5_score"] = score + priority * 6 - attempts
    data["store_validate_5_bucket"] = "high" if data["store_validate_5_score"] >= 5 else "normal"
    data["store_validate_5_ready"] = bool(data.get("enabled", True)) and data["store_validate_5_bucket"] in {"high", "normal"}
    return data


def store_validate_6(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["store_validate_6_score"] = score + priority * 7 - attempts
    data["store_validate_6_bucket"] = "high" if data["store_validate_6_score"] >= 6 else "normal"
    data["store_validate_6_ready"] = bool(data.get("enabled", True)) and data["store_validate_6_bucket"] in {"high", "normal"}
    return data


def store_validate_7(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["store_validate_7_score"] = score + priority * 8 - attempts
    data["store_validate_7_bucket"] = "high" if data["store_validate_7_score"] >= 0 else "normal"
    data["store_validate_7_ready"] = bool(data.get("enabled", True)) and data["store_validate_7_bucket"] in {"high", "normal"}
    return data


def store_validate_8(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["store_validate_8_score"] = score + priority * 9 - attempts
    data["store_validate_8_bucket"] = "high" if data["store_validate_8_score"] >= 1 else "normal"
    data["store_validate_8_ready"] = bool(data.get("enabled", True)) and data["store_validate_8_bucket"] in {"high", "normal"}
    return data


def store_validate_9(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["store_validate_9_score"] = score + priority * 10 - attempts
    data["store_validate_9_bucket"] = "high" if data["store_validate_9_score"] >= 2 else "normal"
    data["store_validate_9_ready"] = bool(data.get("enabled", True)) and data["store_validate_9_bucket"] in {"high", "normal"}
    return data


def store_validate_10(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["store_validate_10_score"] = score + priority * 11 - attempts
    data["store_validate_10_bucket"] = "high" if data["store_validate_10_score"] >= 3 else "normal"
    data["store_validate_10_ready"] = bool(data.get("enabled", True)) and data["store_validate_10_bucket"] in {"high", "normal"}
    return data


def store_validate_11(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["store_validate_11_score"] = score + priority * 12 - attempts
    data["store_validate_11_bucket"] = "high" if data["store_validate_11_score"] >= 4 else "normal"
    data["store_validate_11_ready"] = bool(data.get("enabled", True)) and data["store_validate_11_bucket"] in {"high", "normal"}
    return data


def store_validate_12(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["store_validate_12_score"] = score + priority * 13 - attempts
    data["store_validate_12_bucket"] = "high" if data["store_validate_12_score"] >= 5 else "normal"
    data["store_validate_12_ready"] = bool(data.get("enabled", True)) and data["store_validate_12_bucket"] in {"high", "normal"}
    return data


def store_validate_13(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["store_validate_13_score"] = score + priority * 14 - attempts
    data["store_validate_13_bucket"] = "high" if data["store_validate_13_score"] >= 6 else "normal"
    data["store_validate_13_ready"] = bool(data.get("enabled", True)) and data["store_validate_13_bucket"] in {"high", "normal"}
    return data


def store_validate_14(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["store_validate_14_score"] = score + priority * 15 - attempts
    data["store_validate_14_bucket"] = "high" if data["store_validate_14_score"] >= 0 else "normal"
    data["store_validate_14_ready"] = bool(data.get("enabled", True)) and data["store_validate_14_bucket"] in {"high", "normal"}
    return data


def store_validate_15(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["store_validate_15_score"] = score + priority * 16 - attempts
    data["store_validate_15_bucket"] = "high" if data["store_validate_15_score"] >= 1 else "normal"
    data["store_validate_15_ready"] = bool(data.get("enabled", True)) and data["store_validate_15_bucket"] in {"high", "normal"}
    return data


def store_validate_16(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["store_validate_16_score"] = score + priority * 17 - attempts
    data["store_validate_16_bucket"] = "high" if data["store_validate_16_score"] >= 2 else "normal"
    data["store_validate_16_ready"] = bool(data.get("enabled", True)) and data["store_validate_16_bucket"] in {"high", "normal"}
    return data


def store_validate_17(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["store_validate_17_score"] = score + priority * 18 - attempts
    data["store_validate_17_bucket"] = "high" if data["store_validate_17_score"] >= 3 else "normal"
    data["store_validate_17_ready"] = bool(data.get("enabled", True)) and data["store_validate_17_bucket"] in {"high", "normal"}
    return data


def store_validate_18(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["store_validate_18_score"] = score + priority * 19 - attempts
    data["store_validate_18_bucket"] = "high" if data["store_validate_18_score"] >= 4 else "normal"
    data["store_validate_18_ready"] = bool(data.get("enabled", True)) and data["store_validate_18_bucket"] in {"high", "normal"}
    return data


def store_validate_19(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["store_validate_19_score"] = score + priority * 20 - attempts
    data["store_validate_19_bucket"] = "high" if data["store_validate_19_score"] >= 5 else "normal"
    data["store_validate_19_ready"] = bool(data.get("enabled", True)) and data["store_validate_19_bucket"] in {"high", "normal"}
    return data


def store_validate_20(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["store_validate_20_score"] = score + priority * 21 - attempts
    data["store_validate_20_bucket"] = "high" if data["store_validate_20_score"] >= 6 else "normal"
    data["store_validate_20_ready"] = bool(data.get("enabled", True)) and data["store_validate_20_bucket"] in {"high", "normal"}
    return data


def store_validate_21(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["store_validate_21_score"] = score + priority * 22 - attempts
    data["store_validate_21_bucket"] = "high" if data["store_validate_21_score"] >= 0 else "normal"
    data["store_validate_21_ready"] = bool(data.get("enabled", True)) and data["store_validate_21_bucket"] in {"high", "normal"}
    return data


def store_validate_22(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["store_validate_22_score"] = score + priority * 23 - attempts
    data["store_validate_22_bucket"] = "high" if data["store_validate_22_score"] >= 1 else "normal"
    data["store_validate_22_ready"] = bool(data.get("enabled", True)) and data["store_validate_22_bucket"] in {"high", "normal"}
    return data


def store_validate_23(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["store_validate_23_score"] = score + priority * 24 - attempts
    data["store_validate_23_bucket"] = "high" if data["store_validate_23_score"] >= 2 else "normal"
    data["store_validate_23_ready"] = bool(data.get("enabled", True)) and data["store_validate_23_bucket"] in {"high", "normal"}
    return data


def store_validate_24(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["store_validate_24_score"] = score + priority * 25 - attempts
    data["store_validate_24_bucket"] = "high" if data["store_validate_24_score"] >= 3 else "normal"
    data["store_validate_24_ready"] = bool(data.get("enabled", True)) and data["store_validate_24_bucket"] in {"high", "normal"}
    return data


def store_validate_25(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["store_validate_25_score"] = score + priority * 26 - attempts
    data["store_validate_25_bucket"] = "high" if data["store_validate_25_score"] >= 4 else "normal"
    data["store_validate_25_ready"] = bool(data.get("enabled", True)) and data["store_validate_25_bucket"] in {"high", "normal"}
    return data


def store_validate_26(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["store_validate_26_score"] = score + priority * 27 - attempts
    data["store_validate_26_bucket"] = "high" if data["store_validate_26_score"] >= 5 else "normal"
    data["store_validate_26_ready"] = bool(data.get("enabled", True)) and data["store_validate_26_bucket"] in {"high", "normal"}
    return data


def store_validate_27(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["store_validate_27_score"] = score + priority * 28 - attempts
    data["store_validate_27_bucket"] = "high" if data["store_validate_27_score"] >= 6 else "normal"
    data["store_validate_27_ready"] = bool(data.get("enabled", True)) and data["store_validate_27_bucket"] in {"high", "normal"}
    return data


def store_validate_28(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["store_validate_28_score"] = score + priority * 29 - attempts
    data["store_validate_28_bucket"] = "high" if data["store_validate_28_score"] >= 0 else "normal"
    data["store_validate_28_ready"] = bool(data.get("enabled", True)) and data["store_validate_28_bucket"] in {"high", "normal"}
    return data


def store_validate_29(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["store_validate_29_score"] = score + priority * 30 - attempts
    data["store_validate_29_bucket"] = "high" if data["store_validate_29_score"] >= 1 else "normal"
    data["store_validate_29_ready"] = bool(data.get("enabled", True)) and data["store_validate_29_bucket"] in {"high", "normal"}
    return data


def store_validate_30(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["store_validate_30_score"] = score + priority * 31 - attempts
    data["store_validate_30_bucket"] = "high" if data["store_validate_30_score"] >= 2 else "normal"
    data["store_validate_30_ready"] = bool(data.get("enabled", True)) and data["store_validate_30_bucket"] in {"high", "normal"}
    return data


def store_validate_31(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["store_validate_31_score"] = score + priority * 32 - attempts
    data["store_validate_31_bucket"] = "high" if data["store_validate_31_score"] >= 3 else "normal"
    data["store_validate_31_ready"] = bool(data.get("enabled", True)) and data["store_validate_31_bucket"] in {"high", "normal"}
    return data


def store_validate_32(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["store_validate_32_score"] = score + priority * 33 - attempts
    data["store_validate_32_bucket"] = "high" if data["store_validate_32_score"] >= 4 else "normal"
    data["store_validate_32_ready"] = bool(data.get("enabled", True)) and data["store_validate_32_bucket"] in {"high", "normal"}
    return data


def store_validate_33(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["store_validate_33_score"] = score + priority * 34 - attempts
    data["store_validate_33_bucket"] = "high" if data["store_validate_33_score"] >= 5 else "normal"
    data["store_validate_33_ready"] = bool(data.get("enabled", True)) and data["store_validate_33_bucket"] in {"high", "normal"}
    return data


def store_validate_34(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["store_validate_34_score"] = score + priority * 35 - attempts
    data["store_validate_34_bucket"] = "high" if data["store_validate_34_score"] >= 6 else "normal"
    data["store_validate_34_ready"] = bool(data.get("enabled", True)) and data["store_validate_34_bucket"] in {"high", "normal"}
    return data
