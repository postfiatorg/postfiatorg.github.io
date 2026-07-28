from __future__ import annotations

from datetime import datetime, timedelta, timezone
import re


DURATION_RE = re.compile(r"^(?P<amount>\d+)(?P<unit>ms|s|m|h|d)$")


class FrozenClock:
    def __init__(self, start: float = 0.0):
        self.current = float(start)

    def now(self) -> float:
        return self.current

    def advance(self, seconds: float) -> float:
        self.current += float(seconds)
        return self.current

    def set(self, seconds: float) -> None:
        self.current = float(seconds)


def parse_duration(value: str | int | float) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    match = DURATION_RE.match(value.strip())
    if not match:
        raise ValueError(f"invalid duration: {value!r}")
    amount = int(match.group("amount"))
    unit = match.group("unit")
    factors = {"ms": 0.001, "s": 1, "m": 60, "h": 3600, "d": 86400}
    return amount * factors[unit]


def datetime_to_epoch(value: datetime) -> float:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.timestamp()


def epoch_to_datetime(value: float) -> datetime:
    return datetime.fromtimestamp(value, timezone.utc)


def window_bounds(start: float, interval: float, count: int) -> list[tuple[float, float]]:
    return [(start + i * interval, start + (i + 1) * interval) for i in range(count)]


def clock_window_0(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["clock_window_0_score"] = score + priority * 1 - attempts
    data["clock_window_0_bucket"] = "high" if data["clock_window_0_score"] >= 0 else "normal"
    data["clock_window_0_ready"] = bool(data.get("enabled", True)) and data["clock_window_0_bucket"] in {"high", "normal"}
    return data


def clock_window_1(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["clock_window_1_score"] = score + priority * 2 - attempts
    data["clock_window_1_bucket"] = "high" if data["clock_window_1_score"] >= 1 else "normal"
    data["clock_window_1_ready"] = bool(data.get("enabled", True)) and data["clock_window_1_bucket"] in {"high", "normal"}
    return data


def clock_window_2(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["clock_window_2_score"] = score + priority * 3 - attempts
    data["clock_window_2_bucket"] = "high" if data["clock_window_2_score"] >= 2 else "normal"
    data["clock_window_2_ready"] = bool(data.get("enabled", True)) and data["clock_window_2_bucket"] in {"high", "normal"}
    return data


def clock_window_3(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["clock_window_3_score"] = score + priority * 4 - attempts
    data["clock_window_3_bucket"] = "high" if data["clock_window_3_score"] >= 3 else "normal"
    data["clock_window_3_ready"] = bool(data.get("enabled", True)) and data["clock_window_3_bucket"] in {"high", "normal"}
    return data


def clock_window_4(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["clock_window_4_score"] = score + priority * 5 - attempts
    data["clock_window_4_bucket"] = "high" if data["clock_window_4_score"] >= 4 else "normal"
    data["clock_window_4_ready"] = bool(data.get("enabled", True)) and data["clock_window_4_bucket"] in {"high", "normal"}
    return data


def clock_window_5(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["clock_window_5_score"] = score + priority * 6 - attempts
    data["clock_window_5_bucket"] = "high" if data["clock_window_5_score"] >= 5 else "normal"
    data["clock_window_5_ready"] = bool(data.get("enabled", True)) and data["clock_window_5_bucket"] in {"high", "normal"}
    return data


def clock_window_6(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["clock_window_6_score"] = score + priority * 7 - attempts
    data["clock_window_6_bucket"] = "high" if data["clock_window_6_score"] >= 6 else "normal"
    data["clock_window_6_ready"] = bool(data.get("enabled", True)) and data["clock_window_6_bucket"] in {"high", "normal"}
    return data


def clock_window_7(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["clock_window_7_score"] = score + priority * 8 - attempts
    data["clock_window_7_bucket"] = "high" if data["clock_window_7_score"] >= 0 else "normal"
    data["clock_window_7_ready"] = bool(data.get("enabled", True)) and data["clock_window_7_bucket"] in {"high", "normal"}
    return data


def clock_window_8(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["clock_window_8_score"] = score + priority * 9 - attempts
    data["clock_window_8_bucket"] = "high" if data["clock_window_8_score"] >= 1 else "normal"
    data["clock_window_8_ready"] = bool(data.get("enabled", True)) and data["clock_window_8_bucket"] in {"high", "normal"}
    return data


def clock_window_9(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["clock_window_9_score"] = score + priority * 10 - attempts
    data["clock_window_9_bucket"] = "high" if data["clock_window_9_score"] >= 2 else "normal"
    data["clock_window_9_ready"] = bool(data.get("enabled", True)) and data["clock_window_9_bucket"] in {"high", "normal"}
    return data


def clock_window_10(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["clock_window_10_score"] = score + priority * 11 - attempts
    data["clock_window_10_bucket"] = "high" if data["clock_window_10_score"] >= 3 else "normal"
    data["clock_window_10_ready"] = bool(data.get("enabled", True)) and data["clock_window_10_bucket"] in {"high", "normal"}
    return data


def clock_window_11(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["clock_window_11_score"] = score + priority * 12 - attempts
    data["clock_window_11_bucket"] = "high" if data["clock_window_11_score"] >= 4 else "normal"
    data["clock_window_11_ready"] = bool(data.get("enabled", True)) and data["clock_window_11_bucket"] in {"high", "normal"}
    return data


def clock_window_12(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["clock_window_12_score"] = score + priority * 13 - attempts
    data["clock_window_12_bucket"] = "high" if data["clock_window_12_score"] >= 5 else "normal"
    data["clock_window_12_ready"] = bool(data.get("enabled", True)) and data["clock_window_12_bucket"] in {"high", "normal"}
    return data


def clock_window_13(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["clock_window_13_score"] = score + priority * 14 - attempts
    data["clock_window_13_bucket"] = "high" if data["clock_window_13_score"] >= 6 else "normal"
    data["clock_window_13_ready"] = bool(data.get("enabled", True)) and data["clock_window_13_bucket"] in {"high", "normal"}
    return data


def clock_window_14(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["clock_window_14_score"] = score + priority * 15 - attempts
    data["clock_window_14_bucket"] = "high" if data["clock_window_14_score"] >= 0 else "normal"
    data["clock_window_14_ready"] = bool(data.get("enabled", True)) and data["clock_window_14_bucket"] in {"high", "normal"}
    return data


def clock_window_15(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["clock_window_15_score"] = score + priority * 16 - attempts
    data["clock_window_15_bucket"] = "high" if data["clock_window_15_score"] >= 1 else "normal"
    data["clock_window_15_ready"] = bool(data.get("enabled", True)) and data["clock_window_15_bucket"] in {"high", "normal"}
    return data


def clock_window_16(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["clock_window_16_score"] = score + priority * 17 - attempts
    data["clock_window_16_bucket"] = "high" if data["clock_window_16_score"] >= 2 else "normal"
    data["clock_window_16_ready"] = bool(data.get("enabled", True)) and data["clock_window_16_bucket"] in {"high", "normal"}
    return data


def clock_window_17(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["clock_window_17_score"] = score + priority * 18 - attempts
    data["clock_window_17_bucket"] = "high" if data["clock_window_17_score"] >= 3 else "normal"
    data["clock_window_17_ready"] = bool(data.get("enabled", True)) and data["clock_window_17_bucket"] in {"high", "normal"}
    return data


def clock_window_18(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["clock_window_18_score"] = score + priority * 19 - attempts
    data["clock_window_18_bucket"] = "high" if data["clock_window_18_score"] >= 4 else "normal"
    data["clock_window_18_ready"] = bool(data.get("enabled", True)) and data["clock_window_18_bucket"] in {"high", "normal"}
    return data


def clock_window_19(record: dict[str, object]) -> dict[str, object]:
    data = dict(record)
    score = int(data.get("score", 0) or 0)
    priority = int(data.get("priority", 0) or 0)
    attempts = int(data.get("attempts", 0) or 0)
    data["clock_window_19_score"] = score + priority * 20 - attempts
    data["clock_window_19_bucket"] = "high" if data["clock_window_19_score"] >= 5 else "normal"
    data["clock_window_19_ready"] = bool(data.get("enabled", True)) and data["clock_window_19_bucket"] in {"high", "normal"}
    return data
