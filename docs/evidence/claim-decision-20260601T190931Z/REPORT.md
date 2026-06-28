# Claim Decision Packet

Generated: `20260601T190931Z`

Source whitepaper: `content/whitepaper.md`

Source whitepaper SHA-256: `dceec07dbbb9f2f82e72adbbe96d95303e109b9ead7f4a37732a2b937b06a677`

## Target Criticism

The paper carries a May 2026 revision with a March 2026 production date and benchmark artifacts generated May 5, 2026, while centering validation on `Qwen/Qwen3.6-27B-FP8`, challenged as an unestablished or non-real release served on a hash-pinned SGLang nightly image.

## Decision

`MATERIAL_NEW_INPUT_AVAILABLE`

The next useful input is not another local replay benchmark. The missing surface is a public model-card citation for the exact model ID used in the paper. `Qwen/Qwen3.6-27B-FP8` is publicly resolvable on Hugging Face, is authored by Qwen, is not private, carries Apache-2.0 metadata, has model revision `e89b16ebf1988b3d6befa7de50abc2d76f26eb09`, and the model card documents SGLang serving commands for the same model path.

## Completed Evidence Already Reviewed

The existing provenance packet already addresses the date/publication part of the criticism:

- `docs/evidence/whitepaper-provenance-20260601T175048Z/SHA256SUMS.txt`
- Finding: `22` local artifacts present, `3` public receipts OK, public testnet validator-list sequence `5` decoded, public scoring config verified.

The existing model-lift packets already address the usefulness-versus-baseline part:

- `static/benchmarks/model-lift-baseline-20260601T154824Z/`
- Finding: model output is exactly reproducible and differs from a deterministic baseline, but the packet is a comparator audit, not an accuracy proof.
- `static/benchmarks/model-lift-adjudication-20260601T165516Z/`
- Finding: the observed boundary disagreements are policy tradeoffs under the current fields; existing rows prove neither model superiority nor baseline superiority.

Repeating any of those packets would not add information. They already establish replayability, publication provenance, and the current limit of model-lift evidence.

## New Input

Public source:

- `https://huggingface.co/Qwen/Qwen3.6-27B-FP8`
- `https://huggingface.co/api/models/Qwen/Qwen3.6-27B-FP8`

Command:

```bash
curl -L -s https://huggingface.co/api/models/Qwen/Qwen3.6-27B-FP8 | python3 -m json.tool
```

Observed facts from the API response:

- `id`: `Qwen/Qwen3.6-27B-FP8`
- `private`: `false`
- `author`: `Qwen`
- `sha`: `e89b16ebf1988b3d6befa7de50abc2d76f26eb09`
- `lastModified`: `2026-04-24T02:39:18.000Z`
- `license`: `apache-2.0`
- `downloads`: `7381555`
- `tags` include `fp8`, `safetensors`, and `endpoints_compatible`

Observed facts from the model card:

- The page identifies the repository as FP8-quantized model weights and configuration files.
- The page says the artifacts are compatible with SGLang and gives a SGLang launch command using `--model-path "Qwen/Qwen3.6-27B-FP8"`.

## Document Action

Add one public model-card citation near the existing Qwen3.6 references, and adjust the local-evidence references so they no longer carry the burden of proving that the model itself exists publicly.

Safe sentence for the document:

> The active replay profile uses `Qwen/Qwen3.6-27B-FP8`, a public Qwen Hugging Face model card last modified on 2026-04-24 and documented for SGLang serving, under a pinned Modal/SGLang container; this supports reproducible pinned-stack replay, not model-correctness or production authority transfer.

Stronger claim the document must not make:

> The Qwen3.6 benchmark proves that AI governance is correct, that the model is the optimal selector, or that replayability across heterogeneous production profiles has been established.

## Next Command

The next junior document pass should make a surgical citation edit only:

```bash
python3 -m text_improvement_harness.cli round content/whitepaper.md \
  --project postfiatorg-whitepaper \
  --run-group qwen-public-card-citation \
  --name qwen-public-card-citation \
  --method add-details-address-criticisms
```

The expected patch should add the Hugging Face model-card citation and preserve the current bounded AI claim. It should not add another benchmark section.
