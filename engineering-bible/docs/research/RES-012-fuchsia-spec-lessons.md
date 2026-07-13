---
id: "AOS-RES-012"
title: "Lessons from the Fuchsia/Pixel-9 Custom-OS Specification (Prior Art)"
status: "Prior-art digest, actualized"
version: "1.0.0"
baseline_date: "2026-07-13"
owners: "Architecture / Research Council"
audience: "Engineering, product, research"
summary: "The earlier 60-page Fuchsia/Zircon-on-Pixel-9 specification is superseded as an implementation plan (AgentOS now owns its microkernel and targets the demo brick), but several of its frameworks are platform-independent and are carried forward here: the reuse taxonomy, the two-track strategy, the substrate/platform/shell decoupling, the entity/agent data model, and the honest camera/telephony ceilings."
---

# Lessons from the Fuchsia/Pixel-9 Custom-OS Specification (Prior Art)

> **Superseded as a plan, mined for its frameworks.** The source document specified a Fuchsia/Zircon fork on Pixel 9. AgentOS has since chosen an owned Rust-first microkernel and an interim demo brick; Fuchsia, FEMU, Starnix, and Pixel-9 bring-up are prior art, not the roadmap. What survives the platform change is captured below and mapped to current AgentOS documents. Original illustrations are retained under `diagrams/prior-art-fuchsia-spec/` with provenance.

## Table of Contents

- [Status and Provenance](#status)
- [What Transfers vs What Is Superseded](#transfer)
- [The Reuse Taxonomy (carried forward)](#taxonomy)
- [The Two-Track Strategy (carried forward)](#two-track)
- [Substrate / Platform / Shell Decoupling](#decoupling)
- [Entity / Agent Data Model](#entity)
- [Camera and Telephony Ceilings](#ceilings)
- [Reverse-Engineering Legal Frame](#legal)
- [Precedent Lessons](#precedents)
- [Related Documents](#related)

<a id="status"></a>

## Status and Provenance

Source: a founder-supplied 60-page engineering specification, "Спецификация кастомной мобильной ОС на базе форка Fuchsia/Zircon · Pixel 9" (Russian). SHA-256 and redistribution status recorded in `sources/provenance/PROVENANCE.md`. The binary is not redistributed (integrate-not-store); seven key illustrations are retained locally as prior art. This document is the English, actualized digest of its transferable content.

<a id="transfer"></a>

## What Transfers vs What Is Superseded

| Concept | Status now | Where it lives in AgentOS |
| --- | --- | --- |
| Reuse taxonomy (as-is/wrap/port/reverse/fork/from-scratch) | **Transfers** | This doc; applied to demo-brick modules |
| Two-track strategy (product-in-emulator / hardware separately) | **Transfers** | QEMU track + demo brick (HW-017) |
| substrate/platform/shell + typed contracts | **Transfers** (as our IDL + capabilities) | AOS-ARCH-005, AOS-ARCH-022 |
| entity/agent data model, CRDT, global history | **Transfers** (core product) | AOS-ARCH-001, product vision |
| Camera two-layer tuning, HDR+, honest ceiling | **Transfers** | AOS-HW-018 tuning rule, RES-011 |
| RE legal frame, clean-room | **Transfers** | AOS-LEGAL-003, PROD-014 |
| Precedent lessons (Asahi/Replicant/dahliaOS/Genode) | **Transfers** | This doc |
| Fuchsia/Zircon as the kernel | **Superseded** | Owned microkernel (AOS-ARCH-002) |
| FEMU as acceptance target | **Superseded** | QEMU harness |
| Starnix as compat basis | **Superseded** | Compatibility layer (PROD-014) |
| Pixel 9 / Tensor G4 bring-up | **Superseded / archived** | ADR-0007, demo brick |
| Exynos 5400 modem RE | **Superseded** | Pre-certified module (HW-018) |

<a id="taxonomy"></a>

## The Reuse Taxonomy (carried forward)

Every module is classified by one of six statuses; the status sets the effort, the legal regime, and the risk. This is platform-independent and is the recommended lens for demo-brick modules too.

| Status | Meaning | When | Typical risk |
| --- | --- | --- | --- |
| AS-IS | take ready-made unchanged | fits directly | low |
| WRAP | run existing in a wrapper/compat layer | Linux-form userspace not worth rewriting | medium (ABI) |
| PORT | move code/knowledge to our platform | RE knowledge exists under another framework | high (volume) |
| REVERSE | clean-room reverse engineering | closed interface, no open implementation | very high |
| FORK | fork and maintain a branch | need a divergent base | medium (maintenance) |
| FROM-SCRATCH | write new code | original functionality | scales with scope |

Applied to the demo brick, most hardware is AS-IS (pre-certified modules), drivers are PORT (from RP1/PiSP docs), the product layer is FROM-SCRATCH, and there is almost no REVERSE — which is precisely why the demo brick is faster than the Pixel-9 plan, where REVERSE dominated.

<a id="two-track"></a>

## The Two-Track Strategy (carried forward)

The central strategic decision transfers directly: decouple product from hardware into two parallel tracks with different risk profiles. Track A (product) is built and demonstrated in emulation now, delivering most of the vision with no hardware blockers; Track B (hardware) is the slower bring-up. They converge only at the end. For AgentOS this is the QEMU/simulator track (product, capability model, instant modes, entity/agent) running now, and the demo-brick hardware track proceeding in parallel — exactly the PLAN-018 lane structure.

<a id="decoupling"></a>

## Substrate / Platform / Shell Decoupling

Three horizons with explicit contracts so the product never depends on hardware: substrate (kernel, drivers, HAL, firmware), platform services (entity store, sync, history, integrations, camera/modem as services), and shell/UI. The contract between platform and substrate is stable typed interfaces, so the same product runs on a mock substrate in emulation and on real drivers on hardware without changes above the contract line. In AgentOS this is the IDL/type system (AOS-ARCH-005) plus the capability model (AOS-ARCH-022): the mock-substrate idea becomes the simulator target of AOS-DEMO-012.

<a id="entity"></a>

## Entity / Agent Data Model

The product core is a typed entity graph — nodes (person, project/task, document, event/place, message, device) with typed edges (participates-in, relates-to, derived-from) carrying time, source, and confidence — over which agents with scoped capabilities extract, deduplicate, and link entities and maintain a global history. Deduplication is reversible and auditable (false merges destroy trust). State is local-first with optional CRDT sync; the cloud is transport/backup, never the source of truth. This is the platform-independent heart of the product and aligns with the portable system architecture (AOS-ARCH-001) and the voice agent's typed-action model (AOS-PROD-015).

<a id="ceilings"></a>

## Camera and Telephony Ceilings (honest)

Two ceilings stated plainly in the source, both still true and already reflected in current docs:

- **Camera.** Open computational photography (HDR+ / Halide, libcamera) is real and portable, but the quality ceiling is manual per-sensor tuning (CCM, black level, noise profile, AWB/AE), not the algorithm. Result is "decent," not flagship, without closed tuning. This is the two-layer tuning-portability rule now in AOS-HW-018.
- **Telephony.** On the Pixel-9 plan, the modem was a black box requiring transport + boot-sequence + command-set reverse engineering, with voice the riskiest milestone. The demo brick sidesteps this entirely by using a pre-certified cellular module with a documented interface (AOS-HW-018) — a concrete example of choosing AS-IS over REVERSE.

<a id="legal"></a>

## Reverse-Engineering Legal Frame

Interoperability RE is broadly permitted: EU Software Directive Art. 6 (decompilation for interoperability), US DMCA §1201(f) exception. Safe practice is clean-room: one side observes and documents the hardware interface and writes a specification; another implements from the specification without seeing original code (how Panfrost/Freedreno were built). Firmware blobs are used as-is, never modified; radio behavior is never altered. This is consistent with AOS-LEGAL-003 and the hard rules of AOS-PROD-014, and it applies unchanged regardless of kernel choice.

<a id="precedents"></a>

## Precedent Lessons

- **Asahi Linux** — a small team reverse-engineering modern silicon takes years, and its key multiplier was targeting Linux, where the driver ecosystem exists. Targeting a bespoke stack on undocumented silicon is harder — which is why decoupling tracks is mandatory. (Reinforces the demo-brick choice: buy documented modules, don't reverse a flagship.)
- **Replicant / libsamsung-ipc** — years on one modem class, still not covering modern models: the modem is the most time-consuming block; live on data/SMS and treat voice as a risky milestone. (The demo brick avoids this via a pre-certified module.)
- **dahliaOS** — a real Fuchsia fork exists; the value is not the act of forking but what is built on it. (Generalizes: owning a kernel is not the achievement; the product and the bring-up are.)
- **postmarketOS / Megapixels** — open computational photography is real and portable, but the ceiling is sensor tuning, not the algorithm; calibrate camera expectations to "decent."
- **Genode / Sculpt** — a microkernel capability OS can be a daily driver on open phone hardware (PinePhone); on a closed flagship the driver wall remains the barrier. (Supports building on documented hardware first.)

<a id="related"></a>

## Related Documents

- [Portable system architecture](../architecture/AOS-ARCH-001.md)
- [Microkernel specification](../architecture/AOS-ARCH-002.md)
- [Layer manifest and capabilities](../architecture/ARCH-022-layer-manifest-and-capabilities.md)
- [Interim demo device](../hardware/HW-017-interim-demo-device.md)
- [Demo brick configuration (camera tuning rule)](../hardware/HW-018-demo-brick-v1-configuration.md)
- [Native app clients (RE legality)](../product/PROD-014-native-app-clients.md)
- [ADR-0007: archive the Pixel 9 route](../decisions/ADR-0007-archive-pixel-9-route.md)
