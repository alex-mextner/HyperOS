---
id: "AOS-BRIEF"
title: "Executive Briefing"
status: "Research-backed normative foundation"
version: "2.0.0-foundation"
baseline_date: "2026-07-13"
owners: "Agent OS Architecture Council"
audience: "Engineering, product, security, legal, program, partner, and community readers"
summary: "Decision-oriented summary of the product thesis, owned microkernel, portable layers, hardware routes, legal controls, first actions, purchases, budget, and evidence gates."
---

# Executive Briefing

> Decision-oriented summary of the product thesis, owned microkernel, portable layers, hardware routes, legal controls, first actions, purchases, budget, and evidence gates.

## Table of Contents

- [Executive Decision](#executive-decision)
- [Product and Architecture](#product-and-architecture)
- [Hardware Routes](#hardware-routes)
- [Research and Legal Controls](#research-and-legal)
- [First 30 and 90 Days](#first-actions)
- [Initial Purchases and Budget](#budget)
- [Programme Structure](#programme-structure)
- [Primary Gates](#primary-gates)

<a id="executive-decision"></a>

## Executive Decision

Proceed as an **independently implemented, portable operating system** centered on a Rust-first microkernel and native capability-oriented contracts. Do not redefine the project as an Android distribution, Linux phone, Fuchsia fork, or Pixel-specific custom ROM.

Use Android/Linux only inside the Pixel 9 evidence programme and only to the minimum extent required for stock-baseline measurement, lawful trace collection, recovery, firmware acquisition where permitted, and temporary subsystem bridges. Every bridge has an isolated compatibility cell, source-taint class, owner, native replacement, and last acceptable milestone.

The product hypothesis is an entity- and action-first personal system with semantic history, malleable surfaces, local-first data authority, inspectable agent plans, capability-bounded providers, execution receipts, and reversible or compensating effects. The source-derived product model is summarized in [the product vision digest](sources/normalized/N001-agent-os-product-vision.md#thesis) <!-- xref:AOS-SRC-N001#thesis --> and normalized in [the product surface tiers](docs/product/PROD-012-product-tiers.md#tier-zero) <!-- xref:AOS-PROD-012#tier-zero -->.

<a id="product-and-architecture"></a>

## Product and Architecture

```mermaid
flowchart TB
    UX[IntentBox, FlexLight, stories, views, input] --> PR[Portable product runtime]
    PR --> SYS[Entity, action, history, identity, policy, package, update services]
    SYS --> DEV[Portable device-service contracts]
    DEV --> BK[Target backends and isolated user-space drivers]
    BK --> K[Native Agent OS microkernel]
    K --> AR[Architecture ports]
    AR --> BP[Board packages, boot, power, recovery]

    P9[Pixel 9 stock oracle / temporary sidecars] -. isolated adapter only .-> BK
    Q[QEMU] --> AR
    D[Documented boards] --> BP
    O[Open phone hardware] --> BP
    C[Future custom or ODM device] --> BP
```

Kernel policy remains minimal: isolation, objects, capabilities, IPC, scheduling, memory enforcement, interrupts, time, and architecture mechanisms. Drivers, compatibility, filesystems, networking, graphics, product semantics, and agents remain in user space. See [kernel scope](docs/architecture/ARCH-002-microkernel.md#kernel-scope) <!-- xref:AOS-ARCH-002#kernel-scope --> and [device-service contracts](docs/architecture/ARCH-020-device-service-contracts.md#contract-set) <!-- xref:AOS-ARCH-020#contract-set -->.

<a id="hardware-routes"></a>

## Hardware Routes

The programme runs complementary routes rather than searching for one perfect first device:

| Route | Purpose | Main compromise | Removal strategy |
| --- | --- | --- | --- |
| QEMU x86-64/AArch64 | deterministic kernel and contract evidence | no physical power, DMA, camera, RF, or timing | physical backends and trace comparison |
| Documentation-first boards | clean native ports, drivers, recovery, portability | board form factor and lower consumer quality | second SoC family, carrier board, quality backends |
| Camera-capable documented platforms | RAW, ISP control, calibration, portable pipeline | not flagship phone integration | Pixel oracle, better modules, tuning partners |
| Open phone-form hardware | display/touch/audio/power/modem integration | weaker camera, performance, industrial design | semi-open target, custom carrier, ODM route |
| Pixel 9 | flagship quality ceiling and hard native feasibility | undocumented/vendor subsystems and legal/access risk | strict experiments, partner access, stop criteria, native replacements |
| Semi-open quality phones | bridge between openness and consumer integration | incomplete native documentation | vendor engagement and replaceable service backends |
| Future custom/ODM device | controlled production quality and lifecycle | NRE, MOQ, contracts, certification | architecture readiness, rights, staged RFI and partner scorecard |

Candidate scoring and compromise-removal rules are in [the hardware catalog](docs/hardware/HW-011-open-documented-catalog.md#candidates) <!-- xref:AOS-HW-011#candidates --> and [the compromise ledger](docs/hardware/HW-013-compromise-elimination.md#ledger) <!-- xref:AOS-HW-013#ledger -->.

<a id="research-and-legal"></a>

## Research and Legal Controls

The source corpus, public prior art, runtime observations, NDA material, legal advice, and independent implementation are separate evidence classes. No assumption becomes a requirement merely because it appeared in a historical spec or another operating system.

Required controls include clean-room role separation, jurisdiction-specific reverse-engineering advice, anti-circumvention analysis, artifact redistribution rights, open-source provenance, trademark clearance, privacy impact assessment, product cybersecurity/update obligations, security disclosure, vendor NDA review, and future certification planning. See [clean-room roles](docs/legal/LEGAL-002-clean-room-reverse-engineering.md#roles) <!-- xref:AOS-LEGAL-002#roles -->, [jurisdiction matrix](docs/legal/LEGAL-008-re-jurisdiction.md#matrix) <!-- xref:AOS-LEGAL-008#matrix -->, and [contract red flags](docs/legal/LEGAL-007-vendor-contracts.md#red-flags) <!-- xref:AOS-LEGAL-007#red-flags -->.

<a id="first-actions"></a>

## First 30 and 90 Days

**Days 0–30:** freeze and checksum sources; accept architecture ADRs; create private repositories and CI; establish counsel and trademark work; validate task/spec/source links; acquire safe debug and power equipment; verify board and Pixel SKUs before purchase; complete QEMU bootstrap design; select two documentation-first SoC families.

**Days 31–90:** repeatable QEMU boot and first isolated user process; capability and IPC executable models; native IDL and device-service contracts; first physical-board recovery/diagnostic work; Pixel stock oracle and legally bounded experiment plan; camera reference bench; entity/action/history/receipt vertical schema; public/restricted evidence split; initial adviser and vendor outreach.

The operational sequence is [the First 90 Days plan](docs/planning/PLAN-007-first-90-days.md#day-zero) <!-- xref:AOS-PLAN-007#day-zero --> and the purchase ordering is [First Purchases](docs/planning/PLAN-013-first-purchases.md#first-30) <!-- xref:AOS-PLAN-013#first-30 -->.

<a id="budget"></a>

## Initial Purchases and Budget

The current procurement register contains gated, non-payroll estimates:

- **Wave 0 / first 90 days:** approximately **USD 28,940–79,080**.
- **Wave 1 / initial target expansion:** approximately **USD 6,600–12,700**.
- **Wave 2 / quality, cellular, and laboratory expansion:** approximately **USD 9,000–30,300**.
- **Total listed programme equipment and initial professional-services envelope:** approximately **USD 44,540–122,080** before payroll, tax, customs, ongoing cloud usage, large NRE, production tooling, and certification.

These are planning ranges, not quotes. Purchases are blocked until SKU, documentation, recovery, region, license, return, and unique-evidence checks pass. The canonical line items are `docs/hardware/procurement.csv` and [the procurement specification](docs/hardware/HW-009-lab-procurement-budget.md#purchase-waves) <!-- xref:AOS-HW-009#purchase-waves -->.

<a id="programme-structure"></a>

## Programme Structure

The documentation is organized into ten thematic volumes while implementation is organized into Phase 0–8. The canonical task graph contains detailed descriptions, acceptance criteria, dependencies, owners, dates, milestones, phase/volume mappings, source/claim/experiment references, and specialist-review flags.

Use [the phase table](docs/planning/PLAN-010-nine-phase-execution.md#phase-table) <!-- xref:AOS-PLAN-010#phase-table -->, [the volume table](docs/planning/PLAN-011-ten-volume-program.md#volumes) <!-- xref:AOS-PLAN-011#volumes -->, and [the task catalog](docs/planning/TASKS.md#catalog-rules) <!-- xref:AOS-TASKS#catalog-rules --> together.

<a id="primary-gates"></a>

## Primary Gates

- **Architecture gate:** no Android/Linux/vendor types above approved adapters.
- **Portability gate:** the same contract tests pass on QEMU and two unrelated native SoC families.
- **Pixel gate:** continue only with lawful diagnostics, bounded cost, viable power/display/storage path, and explicit replacement strategy.
- **Camera gate:** measurable RAW/metadata/control/calibration path before claims of good quality.
- **Phone gate:** data, SMS, voice, IMS, emergency, carrier, power, and certification remain separate claims.
- **Security gate:** update/recovery, key classes, driver/DMA confinement, provider authority, and agent action safety have scoped assurance evidence.
- **Publication gate:** no broken links, invalid task graph, unsupported claims, restricted-source leaks, or misleading completion language.

Failed hardware experiments may close a route without invalidating the portable architecture. A route is stopped when continued reverse engineering is less defensible than documented hardware, vendor access, a custom carrier, or a future partner device.
