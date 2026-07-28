# PF Terminal OpenAI/Codex parity backtest

Date: July 28, 2026

## Result

The balanced comparison contains five PF Terminal and five Codex runs on each
of three tasks. Both harnesses passed all 15 runs. Three additional PF Terminal
QueueCraft runs also passed and are reported separately as a robustness check.

Every run used direct OpenAI API access with `gpt-5.6-sol`, high reasoning
effort, and the default service tier. Each began in a fresh workspace with an
isolated PF Terminal home. The same frozen prompts, task sources, hidden
verifiers, model, pricing, and settings were used in the preceding
PF Terminal/Codex regression campaign.

The 15 balanced PF Terminal runs produced 169 distinct captured OpenAI
Responses requests. Once a run began
using `previous_response_id`, every subsequent request preserved that
continuation. No request contained the synthetic `Continue.` message involved
in the prior failure. Two balanced QueueCraft runs emitted model commentary
before additional tool calls, directly exercising the former trigger, and both
retained continuation.

| Task | Fixed PF runs | Captured requests | Continuation drops | Weighted cache share |
| --- | ---: | ---: | ---: | ---: |
| QueueCraft | 5/5 | 46 | 0 | 83.0% |
| TextWright | 5/5 | 67 | 0 | 89.1% |
| QueryForge | 5/5 | 56 | 0 | 87.8% |
| **Balanced total** | **15/15** | **169** | **0** | **87.0%** |

Coding-model spend was $7.2408 for the balanced PF Terminal comparison. The
three extra QueueCraft robustness runs cost $1.4603, bringing total fixed-build
backtest spend to $8.7010.

## Comparison with frozen controls

The fixed PF lane was rerun after the repair. To avoid paying to regenerate
unchanged controls, the comparison uses five-run Codex 0.144.1 controls from
the immediately preceding campaign. They were run with the same tasks, direct
OpenAI route, model, reasoning effort, service tier, and token prices. Because
the controls were not rerun concurrently, the comparisons are descriptive.

| Task | Fixed PF median cost | Codex median cost | PF cost difference | Fixed PF median time | Codex median time | PF time difference |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| QueueCraft | $0.414 | $0.453 | 8.5% lower | 53.7s | 82.6s | 35.0% lower |
| TextWright | $0.494 | $0.522 | 5.3% lower | 70.5s | 74.5s | 5.4% lower |
| QueryForge | $0.478 | $0.518 | 7.8% lower | 154.1s | 136.4s | 13.0% higher |

The observed cache-cost regression was repaired. QueryForge wall time remains
behind the frozen Codex control and is a separate performance target.

## What failed before the fix

PF Terminal inserted a wire-only synthetic `Continue.` item after some
commentary-plus-tool responses. That item was mistakenly included in the
canonical request stored as the next continuation baseline. It was absent from
durable conversation history, so the following request could fail its prefix
comparison, drop `previous_response_id`, and replay full history.

The repair keeps the canonical OpenAI request free of the synthetic item.
Compatibility transforms for providers that require the item now apply only to
their outbound wire copy.

## Limits

- This is a first-party benchmark.
- The primary comparison contains five runs per task per harness. Three
  additional PF Terminal QueueCraft runs are excluded from its medians and
  reported only as robustness evidence.
- The Codex controls are frozen five-run results rather than contemporaneous
  reruns.
- Model output and wall time vary between runs.
- Zero failures across 169 balanced captured requests exercises the observed
  failure mode, including two trigger-bearing runs. Across all 18 PF Terminal
  runs, 198 requests contained zero continuation drops. This does not prove that no
  unrelated cache failure exists in every workflow.

The exact aggregate values are available in
[`summary.json`](./summary.json).
