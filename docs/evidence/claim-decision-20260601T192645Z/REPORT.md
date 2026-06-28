# Claim Decision Packet

Generated: `20260601T192645Z`

Source whitepaper: `content/whitepaper.md`

Source whitepaper SHA-256: `dceec07dbbb9f2f82e72adbbe96d95303e109b9ead7f4a37732a2b937b06a677`

## Target Criticism

The central benchmark evidence is thin and self-referential: determinism results come from a single GPU class, a single model, and small cohorts of 29 and 42 validators, while the supporting references appear to point to internal project files rather than independently retrievable artifacts.

## Decision

`MATERIAL_NEW_INPUT_AVAILABLE`

There is a narrow material input available: several benchmark artifacts are publicly retrievable from `postfiat.org/benchmarks/`, and their public SHA-256 hashes match the repository files. That addresses the "internal files only" portion of the criticism for the static benchmark artifacts.

The same check does not address the broader evidence-breadth criticism. The current benchmark record is still one active model family, one pinned SGLang/Modal profile, and small validator cohorts. The public URLs make the artifacts checkable; they do not turn same-stack replay into cross-profile, cross-model, or production-sufficiency evidence.

## Completed Evidence Already Reviewed

- `docs/evidence/claim-decision-20260601T190931Z/`: public Qwen model-card decision. This resolves public model existence and SGLang-serving support, not benchmark breadth.
- `docs/evidence/whitepaper-provenance-20260601T175048Z/`: provenance packet. This resolves date/testnet/publication receipts, not cross-model or cross-hardware validation.
- `static/benchmarks/model-lift-baseline-20260601T154824Z/`: deterministic-baseline comparator. This resolves repeatable disagreement measurement, not model superiority.
- `static/benchmarks/model-lift-adjudication-20260601T165516Z/`: boundary adjudication. This establishes that current rows do not prove either model or baseline superiority.

Repeating those artifacts would add no information. The remaining question is whether the cited benchmark evidence can be made more externally checkable today, and whether any existing artifact expands the validation envelope beyond one model/profile/cohort family.

## New Input

Public benchmark URLs checked:

| Artifact | Public URL | Status | SHA-256 |
|---|---|---:|---|
| XRPL replay summary | `https://postfiat.org/benchmarks/xrpl-validator-sglang-determinism-20260505T205530Z-summary.json` | 200 | `7f73e8b2f255bf4a7d65ce2c30e7646a8a19b497a44ebc62febe9c9658589ed0` |
| XRPL replay raw packet | `https://postfiat.org/benchmarks/xrpl-validator-sglang-determinism-20260505T205530Z.json` | 200 | `de3076a5ec71f6e5ae81392ccda62b0880ec60c92b2b98a44812997186dcdcb4` |
| Model-lift baseline report | `https://postfiat.org/benchmarks/model-lift-baseline-20260601T154824Z/REPORT.md` | 200 | `c69e696d69be533e4f20ba07f0cc1a488ebbb377b6886f6234bb0360ea38db1f` |
| Model-lift adjudication report | `https://postfiat.org/benchmarks/model-lift-adjudication-20260601T165516Z/REPORT.md` | 200 | `061976ecf3105d8c0c58565f8d48a459c80f64e2463e642d46f197cba45a297f` |
| AI governance evidence challenge report | `https://postfiat.org/benchmarks/ai-governance-evidence-challenge-20260601T170829Z/REPORT.md` | 200 | `e2dbdf95d18d21553daa44abc3bd674586de227f161234dcd32790fd40dc4243` |

The repository tracks the static benchmark reports checked above. The dynamic-unl deployment documents cited by the current whitepaper remain local repository evidence unless separately published.

## What Would Change The Breadth Conclusion

The exact materially different measurement needed is:

1. A second independently rerun validator-scoring replay using a different public model profile on the same frozen inputs.
2. A cross-hardware replay using at least one non-H100/H200 profile, or a documented reason why replay agreement is only claimed within one hash-bound profile.
3. A larger or newer validator cohort, ideally including live testnet rounds, not only the saved 29-validator XRPL cohort and the 42-validator PFT Ledger snapshot.
4. A human or deterministic baseline label set that can adjudicate whether model disagreements are useful, rather than merely repeatable.

No existing repository artifact found in this pass changes those breadth limits.

## Document Action

Safe sentence for the document:

> The benchmark artifacts cited here are publicly retrievable and hash-checkable, but the current empirical claim remains deliberately narrow: same-stack replayability under one pinned Qwen/SGLang profile on the saved XRPL and PFT validator cohorts.

Stronger claim the document must not make:

> The published artifacts establish cross-model reproducibility, heterogeneous hardware replay, model superiority over deterministic or human baselines, or production-sufficient AI governance.

## Next Command

A later document-edit lane can try one compact public-artifact sentence and URL citation set. It should not present this as new validation breadth.

```bash
python3 -m text_improvement_harness.cli attempt content/whitepaper.md \
  --project postfiatorg-whitepaper \
  --modality add-details-address-criticisms \
  --instructions "Use docs/evidence/claim-decision-20260601T192645Z/REPORT.md. Add only a compact sentence that the benchmark artifacts are publicly retrievable and hash-checkable, while preserving the narrow same-stack replayability boundary."
```
