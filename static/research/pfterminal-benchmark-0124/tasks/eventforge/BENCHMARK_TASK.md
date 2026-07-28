You are implementing the EventForge benchmark task.

Work in this repository only. Do not remove tests. Do not bypass the verifier.

Goal:
Implement the `eventforge` package so it can replay an event-sourced ledger and
produce monthly account reports. The visible tests are intentionally incomplete;
the hidden verifier checks the full contract below.

Core API:

```python
from eventforge import replay_events, monthly_report

state = replay_events(lines, as_of=None)
report = monthly_report(lines, month="2026-01")
```

`lines` is an iterable of JSONL strings. Blank lines are ignored.

`replay_events` must return:

```python
{
  "accounts": {
    "account-id": {
      "USD": {
        "posted": "100.00",
        "held": "10.00",
        "available": "90.00"
      }
    }
  },
  "applied_event_ids": ["e1", "e2"],
  "diagnostics": [
    {"code": "duplicate_event", "id": "e2", "message": "..."}
  ]
}
```

Money rules:
- Use `Decimal`, never floats.
- Accept amounts as strings, integers, or decimal-compatible values.
- Normalize output money to exactly two decimals with half-up rounding.
- Reject invalid, NaN, or infinite amounts with an `invalid_amount` diagnostic.

Ordering and idempotency:
- Sort valid events by timestamp, then by input order.
- `as_of` filters out events whose timestamp is after the supplied ISO timestamp.
- Duplicate event IDs are skipped after the first occurrence and emit
  `duplicate_event`.
- Invalid JSON emits `invalid_json`; missing required fields emit
  `invalid_event`; unknown event types emit `unknown_event_type`.
- Diagnostics must not crash replay.

Supported event types:

`deposit`
- Required: `id`, `ts`, `account`, `amount`, `currency`.
- Adds amount to posted balance.

`withdrawal`
- Required: `id`, `ts`, `account`, `amount`, `currency`.
- Subtracts amount from posted balance.

`fee`
- Required: `id`, `ts`, `account`, `amount`, `currency`.
- Subtracts amount from posted balance and counts as fees in monthly reports.

`adjustment`
- Required: `id`, `ts`, `account`, `amount`, `currency`.
- Adds signed amount to posted balance. Negative adjustment decreases posted.

`transfer`
- Required: `id`, `ts`, `from_account`, `to_account`, `amount`, `currency`.
- Subtracts amount from `from_account` posted balance and adds it to
  `to_account` posted balance.

`hold`
- Required: `id`, `ts`, `account`, `amount`, `currency`.
- Does not change posted balance. Increases held balance.
- If amount exceeds current available balance, skip and emit
  `insufficient_available`.

`release`
- Required: `id`, `ts`, `account`, `hold_id`, `amount`, `currency`.
- Decreases remaining held amount for the referenced hold.
- If hold is missing, account/currency mismatched, or amount exceeds remaining
  held amount, skip and emit `invalid_release`.

`reversal`
- Required: `id`, `ts`, `reverses`.
- Applies the inverse effect of the referenced applied event.
- A referenced event may only be reversed once; later attempts emit
  `already_reversed`.
- Missing referenced events emit `missing_reversal_target`.
- Reversing `deposit`, `withdrawal`, `fee`, `adjustment`, and `transfer` is
  required. Reversing `hold` should release any remaining held amount.

Monthly report:

```python
monthly_report(lines, month="2026-01")
```

Returns:

```python
{
  "month": "2026-01",
  "accounts": {
    "alice": {
      "USD": {
        "opening": "10.00",
        "inflow": "100.00",
        "outflow": "25.00",
        "fees": "2.00",
        "closing": "83.00"
      }
    }
  },
  "diagnostics": []
}
```

Monthly rules:
- `opening` is posted balance before the first instant of the month.
- `closing` is posted balance through the final instant of the month.
- `inflow` counts deposits, incoming transfers, and positive adjustments in the
  month.
- `outflow` counts withdrawals, outgoing transfers, and negative adjustments in
  the month as positive numbers.
- `fees` counts fee amounts in the month as positive numbers.
- Reversals inside the month count as inverse flow in the month they occur.
  Example: reversing an outgoing transfer counts as inflow for the original
  sender and outflow for the original receiver.
- Holds/releases affect held/available but not monthly posted flow.

CLI:

```bash
python -m eventforge.cli replay events.jsonl --as-of 2026-01-31T23:59:59Z --json
python -m eventforge.cli report events.jsonl --month 2026-01 --json
```

CLI output must be JSON when `--json` is supplied.

Definition of done:
- `python3 -m unittest discover -s tests` passes.
- `python /home/pfrpc/repos/glm52-agent-bench/verifier/verify.py <repo>` passes.
- Keep code readable and scoped. Do not add network dependencies.
