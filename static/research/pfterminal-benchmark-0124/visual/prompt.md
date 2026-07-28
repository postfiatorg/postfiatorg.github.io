Build a polished, production-quality static marketing website for PfTerminal.

Product brief
- PfTerminal is a terminal-native AI coding environment.
- It can orchestrate multiple frontier models in one auditable workflow.
- It emphasizes fast execution, explicit model routing, resumable sessions,
  local workspace control, and visibility into timing, tokens, and cost.
- Illustrative model labels may include Opus 5, Grok 4.5, Fable, and Kimi K3.
- Audience: senior developers, technical founders, and engineering leads.
- Primary action: view the installation command.
- Secondary action: explore how multi-model orchestration works.
- Benchmark tagline: "One terminal. Many models. One auditable workflow."

Creative direction
- Make an original visual system appropriate for a premium developer tool.
- You own the art direction, layout, typography, animation, and component
  design. Do not copy an existing product site.
- Avoid a generic template, excessive gradients, illegible terminal text,
  fake customer logos, and unsupported performance or security claims.
- Any testimonials or usage numbers must be visibly labeled "demo" or
  "illustrative".

Required content and behavior
- A strong first viewport with product name, tagline, clear primary CTA, clear
  secondary CTA, and a meaningful generated visual.
- Sections explaining orchestration, workflow/observability, model routing,
  and who the product is for.
- A concrete CLI or workflow example.
- An installation panel or modal opened by the primary CTA. It must contain a
  copyable command and a working copy button with visible success feedback.
- A meaningful interactive orchestration demo. The user must be able to
  select or toggle at least two model roles and see the displayed workflow
  state change.
- A responsive mobile navigation that opens and closes.
- Desktop support at 1440px and mobile support at 390px.
- Keyboard-usable controls, visible focus states, sufficient contrast,
  semantic headings, and useful alternative text.
- No broken links, missing local assets, horizontal overflow, or console
  errors during the benchmark interactions.

Image requirement
- Use the OpenAI Image API with model gpt-image-2 to generate exactly three
  final site images.
- Save them under assets/generated or public/assets/generated.
- Create image_manifest.json with exactly three entries. Every entry must
  contain filename, model, prompt, size, quality, created_at, and the OpenAI
  response/request ID when the SDK exposes one.
- Reference at least two of the generated images visibly in the site.
- Generated images must be part of the art direction, not three hidden files.
- Do not keep throwaway image drafts in the final generated-assets directory.
- Never print, embed, or save an API key.

Implementation constraints
- Static HTML/CSS/JavaScript is preferred. A lightweight build tool is allowed
  only if the repository includes a deterministic start command.
- Do not use remote images, remote fonts, CDNs, analytics, or runtime assets.
- You may use inline SVG and CSS-drawn interface elements in addition to the
  three generated raster images.
- The environment provides OPENAI_API_KEY.

Benchmark hooks
- Put data-benchmark="primary-cta" on the control that opens installation.
- Put data-benchmark="install-panel" on the opened installation UI.
- Put data-benchmark="copy-command" on its copy control.
- Put data-benchmark="copy-success" on the visible copy confirmation.
- Put data-benchmark="orchestration-control" on each interactive model-role
  control.
- Put data-benchmark="orchestration-state" on the UI that changes in response.
- Put data-benchmark="mobile-menu" on the mobile menu toggle.
- Put data-benchmark="mobile-menu-panel" on the opened mobile navigation.
These attributes are mechanical test hooks, not a request for any particular
visual design.

Definition of done
- Start the site locally and inspect it at 1440x1000 and 390x844.
- Run:
  /home/pfrpc/repos/pfterminal-perf-probe/runs/opus5-visual-site-20260726T011738Z/.venv/bin/python /home/pfrpc/repos/pfterminal-perf-probe/runs/opus5-visual-site-20260726T011738Z/scripts/verify_site.py . --quick
- Fix failures until the verifier passes.
- Finish your response with BENCH_DONE.
