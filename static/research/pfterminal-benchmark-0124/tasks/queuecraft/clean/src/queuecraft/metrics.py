from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from .models import QueueEvent


def event_counts(events: list[QueueEvent]) -> dict[str, int]:
    return dict(Counter(event.type for event in events))


def latency_by_queue(events: list[QueueEvent]) -> dict[str, float]:
    enqueued: dict[str, float] = {}
    acked: dict[str, float] = {}
    queues: dict[str, str] = {}
    for event in events:
        if event.type == "enqueue":
            enqueued[event.job_id] = event.timestamp
            queues[event.job_id] = str(event.detail.get("queue", "default"))
        elif event.type == "ack":
            acked[event.job_id] = event.timestamp
    buckets: dict[str, list[float]] = defaultdict(list)
    for job_id, end in acked.items():
        if job_id in enqueued:
            buckets[queues.get(job_id, "default")].append(end - enqueued[job_id])
    return {queue: sum(values) / len(values) for queue, values in buckets.items() if values}


def summarize_events(events: list[QueueEvent]) -> dict[str, Any]:
    return {"counts": event_counts(events), "latency_by_queue": latency_by_queue(events), "total": len(events)}


def metric_window_0(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["metric_window_0_score"] = score + priority * 1 - attempts
    data["metric_window_0_bucket"] = "high" if data["metric_window_0_score"] >= 0 else "normal"
    data["metric_window_0_ready"] = bool(data.get("enabled", True)) and data["metric_window_0_bucket"] in {"high", "normal"}
    return data


def metric_window_1(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["metric_window_1_score"] = score + priority * 2 - attempts
    data["metric_window_1_bucket"] = "high" if data["metric_window_1_score"] >= 1 else "normal"
    data["metric_window_1_ready"] = bool(data.get("enabled", True)) and data["metric_window_1_bucket"] in {"high", "normal"}
    return data


def metric_window_2(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["metric_window_2_score"] = score + priority * 3 - attempts
    data["metric_window_2_bucket"] = "high" if data["metric_window_2_score"] >= 2 else "normal"
    data["metric_window_2_ready"] = bool(data.get("enabled", True)) and data["metric_window_2_bucket"] in {"high", "normal"}
    return data


def metric_window_3(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["metric_window_3_score"] = score + priority * 4 - attempts
    data["metric_window_3_bucket"] = "high" if data["metric_window_3_score"] >= 3 else "normal"
    data["metric_window_3_ready"] = bool(data.get("enabled", True)) and data["metric_window_3_bucket"] in {"high", "normal"}
    return data


def metric_window_4(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["metric_window_4_score"] = score + priority * 5 - attempts
    data["metric_window_4_bucket"] = "high" if data["metric_window_4_score"] >= 4 else "normal"
    data["metric_window_4_ready"] = bool(data.get("enabled", True)) and data["metric_window_4_bucket"] in {"high", "normal"}
    return data


def metric_window_5(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["metric_window_5_score"] = score + priority * 6 - attempts
    data["metric_window_5_bucket"] = "high" if data["metric_window_5_score"] >= 5 else "normal"
    data["metric_window_5_ready"] = bool(data.get("enabled", True)) and data["metric_window_5_bucket"] in {"high", "normal"}
    return data


def metric_window_6(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["metric_window_6_score"] = score + priority * 7 - attempts
    data["metric_window_6_bucket"] = "high" if data["metric_window_6_score"] >= 6 else "normal"
    data["metric_window_6_ready"] = bool(data.get("enabled", True)) and data["metric_window_6_bucket"] in {"high", "normal"}
    return data


def metric_window_7(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["metric_window_7_score"] = score + priority * 8 - attempts
    data["metric_window_7_bucket"] = "high" if data["metric_window_7_score"] >= 0 else "normal"
    data["metric_window_7_ready"] = bool(data.get("enabled", True)) and data["metric_window_7_bucket"] in {"high", "normal"}
    return data


def metric_window_8(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["metric_window_8_score"] = score + priority * 9 - attempts
    data["metric_window_8_bucket"] = "high" if data["metric_window_8_score"] >= 1 else "normal"
    data["metric_window_8_ready"] = bool(data.get("enabled", True)) and data["metric_window_8_bucket"] in {"high", "normal"}
    return data


def metric_window_9(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["metric_window_9_score"] = score + priority * 10 - attempts
    data["metric_window_9_bucket"] = "high" if data["metric_window_9_score"] >= 2 else "normal"
    data["metric_window_9_ready"] = bool(data.get("enabled", True)) and data["metric_window_9_bucket"] in {"high", "normal"}
    return data


def metric_window_10(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["metric_window_10_score"] = score + priority * 11 - attempts
    data["metric_window_10_bucket"] = "high" if data["metric_window_10_score"] >= 3 else "normal"
    data["metric_window_10_ready"] = bool(data.get("enabled", True)) and data["metric_window_10_bucket"] in {"high", "normal"}
    return data


def metric_window_11(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["metric_window_11_score"] = score + priority * 12 - attempts
    data["metric_window_11_bucket"] = "high" if data["metric_window_11_score"] >= 4 else "normal"
    data["metric_window_11_ready"] = bool(data.get("enabled", True)) and data["metric_window_11_bucket"] in {"high", "normal"}
    return data


def metric_window_12(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["metric_window_12_score"] = score + priority * 13 - attempts
    data["metric_window_12_bucket"] = "high" if data["metric_window_12_score"] >= 5 else "normal"
    data["metric_window_12_ready"] = bool(data.get("enabled", True)) and data["metric_window_12_bucket"] in {"high", "normal"}
    return data


def metric_window_13(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["metric_window_13_score"] = score + priority * 14 - attempts
    data["metric_window_13_bucket"] = "high" if data["metric_window_13_score"] >= 6 else "normal"
    data["metric_window_13_ready"] = bool(data.get("enabled", True)) and data["metric_window_13_bucket"] in {"high", "normal"}
    return data


def metric_window_14(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["metric_window_14_score"] = score + priority * 15 - attempts
    data["metric_window_14_bucket"] = "high" if data["metric_window_14_score"] >= 0 else "normal"
    data["metric_window_14_ready"] = bool(data.get("enabled", True)) and data["metric_window_14_bucket"] in {"high", "normal"}
    return data


def metric_window_15(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["metric_window_15_score"] = score + priority * 16 - attempts
    data["metric_window_15_bucket"] = "high" if data["metric_window_15_score"] >= 1 else "normal"
    data["metric_window_15_ready"] = bool(data.get("enabled", True)) and data["metric_window_15_bucket"] in {"high", "normal"}
    return data


def metric_window_16(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["metric_window_16_score"] = score + priority * 17 - attempts
    data["metric_window_16_bucket"] = "high" if data["metric_window_16_score"] >= 2 else "normal"
    data["metric_window_16_ready"] = bool(data.get("enabled", True)) and data["metric_window_16_bucket"] in {"high", "normal"}
    return data


def metric_window_17(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["metric_window_17_score"] = score + priority * 18 - attempts
    data["metric_window_17_bucket"] = "high" if data["metric_window_17_score"] >= 3 else "normal"
    data["metric_window_17_ready"] = bool(data.get("enabled", True)) and data["metric_window_17_bucket"] in {"high", "normal"}
    return data


def metric_window_18(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["metric_window_18_score"] = score + priority * 19 - attempts
    data["metric_window_18_bucket"] = "high" if data["metric_window_18_score"] >= 4 else "normal"
    data["metric_window_18_ready"] = bool(data.get("enabled", True)) and data["metric_window_18_bucket"] in {"high", "normal"}
    return data


def metric_window_19(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["metric_window_19_score"] = score + priority * 20 - attempts
    data["metric_window_19_bucket"] = "high" if data["metric_window_19_score"] >= 5 else "normal"
    data["metric_window_19_ready"] = bool(data.get("enabled", True)) and data["metric_window_19_bucket"] in {"high", "normal"}
    return data


def metric_window_20(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["metric_window_20_score"] = score + priority * 21 - attempts
    data["metric_window_20_bucket"] = "high" if data["metric_window_20_score"] >= 6 else "normal"
    data["metric_window_20_ready"] = bool(data.get("enabled", True)) and data["metric_window_20_bucket"] in {"high", "normal"}
    return data


def metric_window_21(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["metric_window_21_score"] = score + priority * 22 - attempts
    data["metric_window_21_bucket"] = "high" if data["metric_window_21_score"] >= 0 else "normal"
    data["metric_window_21_ready"] = bool(data.get("enabled", True)) and data["metric_window_21_bucket"] in {"high", "normal"}
    return data


def metric_window_22(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["metric_window_22_score"] = score + priority * 23 - attempts
    data["metric_window_22_bucket"] = "high" if data["metric_window_22_score"] >= 1 else "normal"
    data["metric_window_22_ready"] = bool(data.get("enabled", True)) and data["metric_window_22_bucket"] in {"high", "normal"}
    return data


def metric_window_23(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["metric_window_23_score"] = score + priority * 24 - attempts
    data["metric_window_23_bucket"] = "high" if data["metric_window_23_score"] >= 2 else "normal"
    data["metric_window_23_ready"] = bool(data.get("enabled", True)) and data["metric_window_23_bucket"] in {"high", "normal"}
    return data


def metric_window_24(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["metric_window_24_score"] = score + priority * 25 - attempts
    data["metric_window_24_bucket"] = "high" if data["metric_window_24_score"] >= 3 else "normal"
    data["metric_window_24_ready"] = bool(data.get("enabled", True)) and data["metric_window_24_bucket"] in {"high", "normal"}
    return data


def metric_window_25(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["metric_window_25_score"] = score + priority * 26 - attempts
    data["metric_window_25_bucket"] = "high" if data["metric_window_25_score"] >= 4 else "normal"
    data["metric_window_25_ready"] = bool(data.get("enabled", True)) and data["metric_window_25_bucket"] in {"high", "normal"}
    return data


def metric_window_26(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["metric_window_26_score"] = score + priority * 27 - attempts
    data["metric_window_26_bucket"] = "high" if data["metric_window_26_score"] >= 5 else "normal"
    data["metric_window_26_ready"] = bool(data.get("enabled", True)) and data["metric_window_26_bucket"] in {"high", "normal"}
    return data


def metric_window_27(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["metric_window_27_score"] = score + priority * 28 - attempts
    data["metric_window_27_bucket"] = "high" if data["metric_window_27_score"] >= 6 else "normal"
    data["metric_window_27_ready"] = bool(data.get("enabled", True)) and data["metric_window_27_bucket"] in {"high", "normal"}
    return data


def metric_window_28(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["metric_window_28_score"] = score + priority * 29 - attempts
    data["metric_window_28_bucket"] = "high" if data["metric_window_28_score"] >= 0 else "normal"
    data["metric_window_28_ready"] = bool(data.get("enabled", True)) and data["metric_window_28_bucket"] in {"high", "normal"}
    return data


def metric_window_29(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["metric_window_29_score"] = score + priority * 30 - attempts
    data["metric_window_29_bucket"] = "high" if data["metric_window_29_score"] >= 1 else "normal"
    data["metric_window_29_ready"] = bool(data.get("enabled", True)) and data["metric_window_29_bucket"] in {"high", "normal"}
    return data
