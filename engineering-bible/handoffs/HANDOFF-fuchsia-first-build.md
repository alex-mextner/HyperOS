---
id: AOS-HANDOFF-003
title: "Handoff — First Fuchsia build + emulator boot (tonight)"
status: handoff
audience: "claude code on the founder's machine (M4 Pro) or a Linux builder"
---

# Handoff: First Fuchsia build + emulator boot

## Why a handoff
The docs agent's container has 1 core / 3 GB RAM / 10 GB free disk — a Fuchsia checkout alone
needs ~90 GB and the build hours of CPU. Infeasible there. Scripts are ready; run them where
the hardware is.

## Fast win tonight (minutes, NO build) — do this first
On the M4 Pro directly:
```bash
bash scripts/fuchsia-sdk-quickstart.sh
# then: tools/ffx product download <bundle-url> ~/fuchsia-bundles/x
#       tools/ffx emu start
```
Evidence to record: SDK version, bundle name, emulator boot OK/fail, notes on Apple Silicon friction.

## Full first build overnight (hours) — Tier 2
Preferred: an x86-64 Debian VM (UTM/Parallels, 10–12 cores, 24+ GB RAM, 250 GB disk) or a rented
x86-64 Linux box. Then:
```bash
bash scripts/fuchsia-full-build.sh
```
Evidence to record (this replaces estimates in ARCH-023): `fx set` time, first `fx build` wall time,
no-op rebuild time, one-file-touch rebuild time, disk used, `fx ffx emu start` boot OK.

## Acceptance
- Emulator booted from prebuilts (screenshot/console log).
- If the full build ran: the four timing numbers + disk usage posted to the tracker and ARCH-023.
