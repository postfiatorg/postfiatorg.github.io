{{- $v := .Params.version -}}
{{- $plans := .Site.Data.pfterminal_plans -}}
# PFTerminal — The AI terminal that answers to you

Canonical: https://postfiat.org/terminal/
Markdown mirror of the page above. Release documented here: PFTerminal {{ $v }}.

One terminal. Every model. Your keys, your wallet, your chain of command.

PFTerminal is a crypto-native AI services terminal based on the open-source Codex CLI that
routes across six built-in providers, assigns a provider, model, and reasoning effort to each
spawned agent, and lets you buy prepaid inference in USDC from a Solana wallet you hold. It is
a Rust TUI.

Release and performance facts:

- 6 built-in providers
- {{ $v }} release documented here
- ~9.5 s -> ~1.6 s resumed native Z.AI local setup, measured 2026-06-28
- 4.05 s large resumed Vercel thread, fresh process, measured 2026-06-28
- 1-200 USDC prepaid plan range, 1M-200M tokens per month
- Apache-2.0, public repository, written in Rust

## 01 — Install it in one line.

Linux:

```
curl -fsSL https://github.com/agtico/PfTerminal/releases/latest/download/install.sh | sh
```

macOS (same installer; also available as `PFTerminal-aarch64-apple-darwin.dmg` and
`PFTerminal-x86_64-apple-darwin.dmg`):

```
curl -fsSL https://github.com/agtico/PfTerminal/releases/latest/download/install.sh | sh
```

Windows (native PowerShell installer; PowerShell's curl alias is unsupported):

```
Invoke-RestMethod https://github.com/agtico/PfTerminal/releases/latest/download/install.ps1 | Invoke-Expression
```

PFTerminal is a Post Fiat product. Its source is published under the `agtico` GitHub
organisation and its npm package under the `@agticorp` scope.

Creates a `pfterminal` command. Does not touch an existing `codex` command. Stores all state in
`$HOME/.pfterminal`.

- npm package: `@agticorp/pfterminal`
- Bun: `bun add -g @agticorp/pfterminal`
- Releases: https://github.com/agtico/PfTerminal/releases
- Documented uninstall covers the binary, packages, and local state.
- For trusted workspaces, `pfterminal --yolo` launches without approval prompts.

## 02 — Every model, one terminal.

Ambient GLM 5.2 is the default model path. `/providers` grants provider access; `/model`
selects the provider, the model, and the reasoning effort. A spawned agent may differ from its
parent on all three.

| Provider id | Display name | Base URL | Credential | Wire API |
| --- | --- | --- | --- | --- |
| `openai` | OpenAI | `https://chatgpt.com/backend-api/codex` | Account login | Responses |
| `ambient` | Ambient | `https://api.ambient.xyz/v1` | `AMBIENT_API_KEY` | Chat Completions |
| `zai` | Z.AI | `https://api.z.ai/api/coding/paas/v4` | `ZAI_API_KEY` | Chat Completions |
| `openrouter` | OpenRouter | `https://openrouter.ai/api/v1` | `OPENROUTER_API_KEY` | Chat Completions |
| `baseten` | Baseten | `https://inference.baseten.co/v1` | `BASETEN_API_KEY` | Chat Completions |
| `vercel` | Vercel AI Gateway | `https://ai-gateway.vercel.sh/v1` | `AI_GATEWAY_API_KEY` | Responses |

Surfaces PFTerminal integrates with (systems it talks to, not partners, customers, or endorsers):
OpenAI, Ambient, Z.AI, OpenRouter, Baseten, Vercel AI Gateway, Anthropic, Moonshot Kimi, Vast.ai,
RunPod, Solana, and Post Fiat Task Node.

Kimi Code, Anthropic / Claude Plan, and the PfTerminal Plan are credentialed through
`/providers`. A rented GPU endpoint appears in `/model` once it reports `READY`. None of these
are counted among the six built-in providers.

## 03 — A chain of command, not a pile of tabs.

- **Nazgul** — root supervisor bound to the pane you talk to. Converts your objective into coordinated work.
- **Troll** — engineering-manager tier. Manages delegated execution, reviews Orc output, and reports upward.
- **Orc** — bounded IC executor. Performs implementation or investigation work and reports results upward.

`/orchestrate` attaches a lasting supervisory assignment to an existing worker or pane: attach,
pause, resume, extend, test/fire, detach. `/spawn` creates the crew; `/orchestrate` manages it.

Spawn tools serialize as plain functions rather than `ToolSpec::Namespace`, so the hierarchy
survives providers whose `namespace_tools` capability is false.

Claude Code headless panes run real `claude -p` turns against a local Anthropic Messages bridge
that translates to the chosen provider using the vault-held key. Ambient parity passed
2026-06-25.

## 04 — You hold the keys and the wallet.

`/vault` stores provider keys and arbitrary user secrets encrypted. `/vault list` and
`/vault show <label>` are metadata-only. `/vault credential add` refuses an inline secret and
opens the secure modal. Copy-to-clipboard never prints the secret into chat. Release {{ $v }}
hardened recovery: an existing vault validates every available key source against its own
ciphertext and never generates or overwrites a key during recovery.

`/wallet` manages a local Solana-mainnet wallet holding SOL and canonical USDC. Unlock grants
signing capability to the current TUI for one action or the selected duration; Lock revokes it.
Remove wallet from this device removes local custody and the local plan credential; it does not
move on-chain funds and does not cancel a paid period.

## 05 — Rent third-party GPU capacity with explicit spend limits.

`/gpu` rents third-party capacity on Vast.ai and RunPod. PFTerminal does not provide a free GPU
pool; the marketplace account you connect is billed.

Controls asked before the search: maximum hourly USD price, maximum total USD spend, and
duration in whole minutes. Setup, model download, and loading consume that duration.

Provisioning stages: hardware checks, runtime setup and build, model download, artifact
verification, loading, endpoint qualification. Only `READY` means the rented model is available
in `/model`.

Cleanup: **Stop serving** removes the endpoint from model selection and provider billing
continues. **Terminate rental** requests provider cleanup; treat billing as unresolved until
PFTerminal reports provider-confirmed termination. Exiting PFTerminal is never a substitute.

Qualified recipes on record: Vast.ai 4xH200 SGLang TP4 behind a token-authenticated HTTPS
tunnel; RunPod 2xH200 pinned SGLang TP2 behind the RunPod authenticated proxy boundary; official
`zai-org/GLM-5.2-FP8` weights served and qualified on Vast.ai.

## 06 — Measured, dated, and published.

Native provider performance report, 2026-06-28:

| Measurement | Before | After |
| --- | --- | --- |
| Local client and provider setup, resumed native Z.AI turn | ~9.5 s | ~1.6 s |
| Large resumed thread, fresh process, Vercel Responses, wall clock | — | 4.05 s |
| local setup / provider request and stream | — | ~1.6 s / ~1.6 s |

What changed locally: removed the hot-path vault fingerprint read, cached provider auth in the
model provider, cached decrypted local secrets inside the secrets backend. On the Vercel path:
Responses requests set `store: true`, persist `ModelResponseCompleted`, restore the last
response id on resume, and send only the incremental input.

Scope and method: measured 2026-06-28 on the `native-provider-performance` bench. Both figures
are fresh-process runs against a large resumed thread, not cold first turns. The Vercel figure is
corroborated by the dumped request: `store: true`, `previous_response_id` populated,
`input_len: 1`, `input_chars: 119`. These are self-measured, single-configuration numbers on one
machine, not a cross-vendor benchmark.

## 07 — It is a fork of a real runtime, not a wrapper.

Inherited runtime surfaces: tools and approvals, sandboxing and execpolicy, MCP servers,
non-interactive `exec` mode, review modes, `AGENTS.md` project instructions.

Skills and plugins: bundled system skills in `$HOME/.pfterminal/skills/.system/`, user skills in
`$HOME/.agents/skills/`, repo skills in `<repo>/.agents/skills/`, plugins with a
`.codex-plugin/plugin.json` manifest, and apps or connectors exposed as MCP tool sets.

Open source: Apache-2.0, public repository, written in Rust — https://github.com/agtico/PfTerminal

Guardrails: provider hammer reduction and a tool-call runaway guard. `/docs` browses the bundled
documentation inside the terminal.

## 08 — Wired into Post Fiat Task Node.

`/tasknode` forms: `link`, `status`, `tasks [tab]`, `outstanding`, `verification`, `refused`,
`rewarded`, `task <id>`, `request`, `request <text>`, `requests`, `context`, `chat`,
`chat <text>`, `balance`, `rewards`, `logout`.

Task Node: https://postfiat.org/task-node/ and https://tasknode.postfiat.org

## 09 — Buy AI inference with USDC. No credit card, no seat license, no account signup.

Provider access: use `/providers` to grant provider access and `/model` to select the provider,
model, and reasoning effort. Provider credentials can be stored in the encrypted `/vault`.

PfTerminal Plan: buy a prepaid plan from `/wallet` — unlock the wallet, review the tier and
exact USDC amount, then confirm. After activation, the plan's models appear in `/model`.

| Plan | Price | Term | Tokens / month | Tokens / week | Max output tokens |
| --- | ---: | ---: | ---: | ---: | ---: |
{{- range $plans.plans }}
| `{{ .id }}` | {{ .priceUsdc }} USDC | {{ .termMonths }} month | {{ lang.FormatNumberCustom 0 (float .monthlyTokenLimit) }} | {{ lang.FormatNumberCustom 0 (float .weeklyTokenLimit) }} | {{ lang.FormatNumberCustom 0 (float .maxOutputTokens) }} |
{{- end }}

Plan model allowlist as published by the plan gateway: {{ range $i, $m := (index $plans.plans 0).modelAllowlist }}{{ if $i }}, {{ end }}`{{ $m }}`{{ end }}. This describes plan scope, not a
complete PFTerminal model roster. Settlement is canonical USDC on Solana mainnet. Prices read
from the PfTerminal plan gateway on {{ dateFormat "2006-01-02" $plans.fetched_at_utc }};
`/wallet` is authoritative at purchase time.

- Plan details show prepaid tier, token use, limits, reset dates, and queued periods.
- Upgrade purchases the period shown on the confirmation screen.
- Recover existing plan signs an ownership proof and sends no USDC.
- Disconnect PfTerminal Plan removes the local plan credential while retaining the wallet and paid period.
- Durable payment receipts are the settlement evidence.

Third-party GPU rentals: Vast.ai and RunPod bill the marketplace account. PFTerminal requires a
max hourly USD price, max total USD spend, and duration in whole minutes before it searches
compatible offers.

Prepaid. Non-custodial. Revocable.

## 10 — The whole product-specific surface, in one screen.

24 product-specific command entries. Variants such as `/spawn status` are counted as entries.
The Task Node forms remain grouped under `/tasknode`.

`/model`, `/providers`, `/vault`, `/vault list`, `/vault show <label>`, `/vault credential add`,
`/wallet`, `/gpu`, `/spawn`, `/spawn status`, `/spawn nazgul`, `/spawn troll`, `/spawn orc`,
`/orchestrate`, `/orchestrate status`, `/panes`, `/agent`, `/tasknode`, `/skills`, `/docs`,
`/status`, `/usage`, `/ps`, `/stop`

## 11 — What is shipped, what is experimental, and what is not built.

**Shipped:** six built-in providers; encrypted vault; `/spawn` Nazgul, Troll, and Orc
orchestration; `/orchestrate` persistent supervision; Claude Code headless panes on Ambient;
`/wallet` and PfTerminal Plan purchase; `/gpu` rental on Vast.ai and RunPod; `/tasknode`,
`/docs`, skills, plugins, MCP.

**Experimental:** Claude pane profiles on Z.AI, Baseten, OpenRouter, Vercel, and Claude Plan.
Live-smoke-tested, and not yet through the four-workflow parity suite that Ambient passed.

**Not built or not verified:** Balrog planner and the Grimoire; Wyverns, Golems, and campaign
documents; Nostr reachability; Hyperliquid, staking, and borrowing; the `/subagents` diagnostics
view. These are specifications and backlog items, not features.

## Start with one command.

Install PFTerminal {{ $v }} on Linux, macOS, or Windows:
https://github.com/agtico/PfTerminal/releases
