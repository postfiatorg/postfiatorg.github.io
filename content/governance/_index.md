---
title: "Governance"
date: 2026-11-09T00:00:00Z
description: "Decisions made by deterministic judgment, each published with the receipts that let anyone check it."
---

Post Fiat proposes that what comes after fiat is a new social model, one where deterministic judgment plays a central role in governance in place of the opaque committees that run the XRPL.

Each decision starts with a submission from the operator. A pinned open-weight model answers it on independent machines under a fixed configuration, and the answer counts only if every machine produces the same output bytes. The model keeps no memory between requests, so a follow-up carries the full prior exchange in its input. Every answer is published with per-GPU receipts, a hash-chained log and a verifier, so anyone can check that the machines agreed.
