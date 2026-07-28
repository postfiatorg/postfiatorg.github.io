# PFTerminal 0.1.24 release evidence

- Release: https://github.com/agtico/PfTerminal/releases/tag/rust-v0.1.24
- Workflow: https://github.com/agtico/PfTerminal/actions/runs/30322187861
- Published: `2026-07-28T03:40:18Z`
- Tag/target: `rust-v0.1.24` at
  `348afe4b3a41f82db3d15a488587e4aa08b959ec`
- Status: non-draft, non-prerelease, GitHub `latest`
- Assets: 11 (five package archives, two DMGs, two install scripts, two
  checksum manifests)

## Final Linux x86 verification

- Archive SHA-256:
  `03134697b4c6a96123eb36d1a54c6707b8f08879b5df80aa5da7c8fcca2c1837`
- The archive hash matches `pfterminal-package_SHA256SUMS`.
- Extracted binary SHA-256:
  `f80202257238de853c59a97a73b22aaf5d78071c0cbd898169f98e4cc94898d2`
- `pfterminal --version`: `pfterminal 0.1.24`
- `pfterminal telegram --help`: pass
- `pfterminal-walletd --help`: pass

## Benchmark-subject provenance

The paid campaign froze the Linux x86 artifact from the first release build at
product commit `81a6ff2f953ef5463e69e018e3c9515d0bd19ca3` before a transient macOS
`hdiutil create` failure stopped publication.

- Frozen benchmark binary SHA-256:
  `acbc8f89f35e2d29ba8304aee1d79911c0384905269ad662bbfcfda9f2a5cb0b`
- Final published binary SHA-256:
  `f80202257238de853c59a97a73b22aaf5d78071c0cbd898169f98e4cc94898d2`

The binaries are not claimed to be byte-identical. The complete source diff
from the frozen product commit to the published tag is only:

`scripts/install/build_macos_dmg.sh`

That change adds bounded retry around transient DMG creation. No Rust,
provider, model, orchestration, caching, or runtime product source changed.
The campaign therefore remains behaviorally representative of the published
0.1.24 product code while retaining its original immutable subject hash.
