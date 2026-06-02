# Prompt Design Audit

Generated: 2026-06-02T18:26:12Z

- Valid: True
- Prompt count: 187
- Unique prompt hashes: 187

## Design Position

- Allowed labels are provided as output choices only.
- Expected labels are kept in `labels/` and not placed in packet facts.
- The prompt forbids outside knowledge, packet identity, label order, case numbering, and `held_out_fields` names as evidence.
- `vote_outcome` and `triage` packets exclude current enabled-state facts.
- `vote_state` packets intentionally include current or dated state facts.
- `triage` remains a frozen conservative policy-conformance lane, not an XRP vote replay lane.

## Errors

- None

## Warnings

- None
