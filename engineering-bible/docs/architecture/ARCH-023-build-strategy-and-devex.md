---
id: "AOS-ARCH-023"
title: "Build Strategy and Developer Experience for the Fuchsia Fork"
status: "Normative planning baseline"
version: "1.0.0"
baseline_date: "2026-07-13"
owners: "Architecture Council / Build & Infra"
audience: "Engineering"
summary: "How we neutralize the heavy Fuchsia full-tree build: a two-tier model where day-to-day product work uses the Bazel SDK against prebuilt platform artifacts (no platform build at all), and only kernel/driver deltas require the full GN/ninja tree; incremental ninja + ccache make the full tree a first-build-only cost; Apple Silicon guidance and prebuilt-bundle emulator path included."
---

# Build Strategy and Developer Experience for the Fuchsia Fork

> The scary sentence — "the Fuchsia build is heavy, you need a dedicated Linux box" — is true only for the **full platform tree**, and only for the **first** build. Most of our engineering (the entire product layer) never needs a platform build at all: it compiles in seconds-to-minutes against prebuilt platform artifacts via the SDK. This document makes that split normative.

## Table of Contents

- [Problem Statement](#problem)
- [Facts (verified)](#facts)
- [Two-Tier Build Model (normative)](#two-tier)
- [Tier 1: SDK-First Product Development](#tier1)
- [Tier 2: Full-Tree Platform Work](#tier2)
- [Incremental Builds and Caching](#incremental)
- [Apple Silicon (M-series) Guidance](#apple)
- [Try-It-Tonight Path (no build)](#tonight)
- [Requirements](#requirements)
- [Risks and Open Questions](#risks)
- [Related Documents](#related)

<a id="problem"></a>

## Problem Statement

The full Fuchsia tree builds through GN/ninja/fx, officially on x86-64 Linux (Debian-based), and the first build needs serious disk (~200 GB working set), RAM, and cores. Taken naively, that means every engineer needs a build server and every iteration costs a platform build. That would be a real velocity killer. This document exists because the naive reading is wrong: the platform build is a **rare, cacheable, CI-owned cost**, not the daily loop.

<a id="facts"></a>

## Facts (verified against fuchsia.dev)

- Full-tree host support: **x86-64 Linux (Debian-based)**; Windows unsupported; macOS is not a supported full-tree build host.
- **ccache** is officially supported for the full tree ("enabled automatically if CCACHE_DIR refers to an existing directory") and caches C/C++ artifacts across builds.
- GN/ninja is **incremental by design**: after the first build, `fx build` recompiles only changed targets.
- The **Fuchsia SDK (Bazel-based)** exists precisely so components, drivers, and even product assembly happen **out-of-tree against prebuilt platform artifacts** — the IDK/SDK "can be used to develop Fuchsia components without checking out Fuchsia's source code or using Fuchsia's own build system," and Fuchsia itself converged on Bazel+SDK as the well-lit path (RFC-0139, RFC-0186).
- **Prebuilt product bundles** are downloadable (`ffx product download`) and boot directly in the emulator — trying Fuchsia in FEMU requires **no build at all**.
- FEMU supports ARM64 hosts including Apple Silicon; the **qemu-arm64 target is documented as "very limited and not recommended"**, so arm64-target work carries friction; x64 remains the well-lit target.

<a id="two-tier"></a>

## Two-Tier Build Model (normative)

| Tier | Who | What builds | Where | Cost |
| --- | --- | --- | --- | --- |
| **Tier 1 — Product (default)** | Product-layer engineers (entity/agent, shell, services, apps) | Only our components, via Bazel SDK against prebuilt platform | Any decent laptop | Seconds–minutes |
| **Tier 2 — Platform (exception)** | Kernel/driver/platform-delta engineers + CI | The forked Fuchsia tree via fx/GN/ninja | Dedicated x86-64 Linux builder + CI | First build: hours; incremental: minutes |

Rules:
1. Product-layer code MUST build with the SDK workflow and MUST NOT require a platform checkout.
2. The fork pins an upstream revision; CI produces and publishes platform artifacts (IDK/SDK + product bundles) for Tier 1 to consume.
3. Only changes below the platform contract (kernel deltas, board drivers, platform patches) touch Tier 2.
4. CI is the canonical Tier-2 builder; local Tier-2 builds are for platform engineers only.

This is the same decoupling as substrate/platform/shell, applied to the build: the contract line is the SDK.

<a id="tier1"></a>

## Tier 1: SDK-First Product Development

Bootstrap (per sdk-samples/getting-started):

```bash
git clone https://fuchsia.googlesource.com/sdk-samples/getting-started fuchsia-getting-started --recurse-submodules
cd fuchsia-getting-started
scripts/bootstrap.sh          # fetches the Bazel-based SDK toolchain
tools/ffx sdk version         # verify
tools/ffx product download <bundle>   # prebuilt platform image
tools/ffx emu start           # boot the emulator from prebuilts
bazel build //src/...         # build only OUR components
```

Iteration on a component is a normal Bazel build: seconds-to-minutes, cached, hermetic. Our repo will vendor the same Bazel SDK rules and point them at OUR CI-published platform artifacts once the fork exists; until then, upstream bundles are the substrate for product-layer development — which is exactly the Track-A plan.

<a id="tier2"></a>

## Tier 2: Full-Tree Platform Work

```bash
curl -s "https://fuchsia.googlesource.com/fuchsia/+/HEAD/scripts/bootstrap?format=TEXT" | base64 --decode | bash
cd fuchsia
export CCACHE_DIR=$HOME/.ccache   # enables ccache automatically
fx set minimal.x64 --release       # or workbench_eng.x64 / our product.board
fx build                           # FIRST build: heavy. After: incremental.
fx ffx emu start --headless        # boot what you built
```

Sizing the builder: ≥16 modern cores, 64 GB RAM, ≥250 GB NVMe free. On such a box the first `minimal.x64` build is on the order of **1–3 hours**; a beefier CI machine (32–96 cores) brings it to tens of minutes. These are estimates from community experience, not vendor promises; our own CI will record real numbers as evidence.

<a id="incremental"></a>

## Incremental Builds and Caching

- **ninja incrementality**: `fx build` after a small change rebuilds only affected targets — typically **seconds to a few minutes**, not hours. The "heavy build" is a first-build/clean-build property.
- **ccache**: caches C/C++ compilation across builds and checkouts; officially supported.
- **Pinned upstream**: the fork pins a revision, so the expensive graph doesn't churn under us; controlled rebases are scheduled, and CI pre-warms caches after each rebase.
- **CI-published artifacts**: Tier 1 never pays the platform cost because CI publishes the IDK/SDK and product bundles per pinned revision.

<a id="apple"></a>

## Apple Silicon (M-series) Guidance

Native macOS is **not** a supported full-tree host. On an M4 Pro the realistic options, best first:

1. **Tier 1 only (recommended daily driver):** SDK/Bazel product development + emulator with prebuilt bundles. This is light and is most of our work anyway.
2. **Remote Tier-2 builder:** a rented x86-64 Linux box (Hetzner AX/EX class or cloud) as the platform builder; the Mac is the editor/terminal. This matches the "dedicated build machine/CI" the spec already assumed — but only for platform deltas.
3. **Linux VM on the Mac (arm64):** UTM/Parallels with 10–12 cores and ~250 GB disk can build the **arm64** target; expect a first build in the low single-digit hours (estimate; unverified on M4 Pro — record actual numbers as evidence) and note that host arm64 / target arm64 support is less trodden than x64 (the emulator docs call qemu-arm64 "very limited"). Treat this as an experiment, not the well-lit path.

Estimated M4 Pro numbers to validate by experiment (EXP): first full build in an arm64 Linux VM: ~2–6 h; incremental after small change: ~10 s–3 min; SDK component build: seconds–minutes; emulator boot from prebuilts: minutes.

<a id="tonight"></a>

## Try-It-Tonight Path (no build)

Booting Fuchsia in the emulator **tonight** does not require building anything: fetch the SDK tools, `ffx product download` a prebuilt bundle, `ffx emu start`. On Apple Silicon prefer the arm64 bundle if offered, x64 otherwise (slower under emulation). The full-tree first build is what runs overnight — on a Linux builder, via the script in `scripts/fuchsia-full-build.sh`.

<a id="requirements"></a>

## Requirements

- **R01.** Product-layer code builds via the SDK workflow with no platform checkout (Tier 1).
- **R02.** CI owns the Tier-2 full-tree build on a pinned revision and publishes IDK/SDK + product bundles.
- **R03.** ccache is enabled on all Tier-2 builders; incremental build health (time-to-rebuild after a 1-file change) is a tracked CI metric.
- **R04.** First-build, incremental-build, and emulator-boot times are recorded as evidence per builder class (CI box, M4 Pro VM) — estimates in this document are replaced by measurements.
- **R05.** Apple Silicon engineers default to Tier 1; Tier-2 access is via the remote builder.

<a id="risks"></a>

## Risks and Open Questions

- The SDK is a moving target (Bazel migration ongoing per RFC-0186); pinning SDK versions alongside the platform revision is mandatory.
- arm64-host/arm64-target support may lag x64; if VM builds on Apple Silicon prove painful, the remote x86-64 builder is the fallback (budgeted).
- Out-of-tree product **assembly** had gaps historically; verify current assembly-out-of-tree status when we vendor the SDK rules.
- **Open-question rule:** unanswered high-impact questions become claims/experiments.

<a id="related"></a>

## Related Documents

- [Fuchsia-fork spec digest (build section)](../research/RES-012-fuchsia-spec-lessons.md)
- [ADR-0001: Fork Fuchsia/Zircon](../decisions/AOS-ADR-0001.md)
- [Kickoff sequence and lanes](../planning/PLAN-018-kickoff-sequence.md)
