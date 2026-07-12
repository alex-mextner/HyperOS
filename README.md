# Agent OS — Public Engineering Programme

> **Working title:** Agent OS. Stable technical identifiers use the `AOS-*` namespace while naming and trademark review remain open.

Agent OS is an original Rust-first mobile operating-system programme centred on an owned microkernel, capability-secured IPC, portable device-service contracts, and agent-oriented system layers.

## Architecture boundary

The native architecture does not depend on Android, Linux, POSIX, Binder, or Android HAL contracts. Android and Linux are permitted only inside the isolated Pixel 9 evidence and bring-up track as stock-device oracles, trace sources, recovery mechanisms, and explicitly temporary bridges with replacement criteria.

## Public engineering portal

This repository contains the source for a public Git-backed engineering environment:

- `knowledge/` — canonical Markdown Wiki and research records;
- GitHub Issues — executable work and public discussion;
- GitHub Projects — portfolio fields, schedule, roadmap, and board views;
- `portal/` — responsive Wiki, task, Gantt, and API frontend deployed on Vercel;
- `.github/workflows/` — validation, issue bootstrap, and derived-data automation;
- `docs/MOBILE-EDITING.md` — iPhone and iA Writer editing workflow.

## Current status

Foundation publication is in progress. The first release establishes the architecture boundaries, hardware tracks, public documentation model, task hierarchy, validation rules, and portal. It does **not** claim that the microkernel or native Pixel 9 support is already implemented.

## Start here

- [Executive briefing](knowledge/BRIEFING.md)
- [Documentation index](knowledge/docs/INDEX.md)
- [Portable architecture](knowledge/docs/architecture/ARCH-001-portable-system-architecture.md)
- [Microkernel specification](knowledge/docs/architecture/ARCH-002-microkernel.md)
- [Hardware target portfolio](knowledge/docs/hardware/HW-001-target-portfolio.md)
- [Roadmap and Gantt authority](knowledge/docs/planning/PLAN-002-roadmap-and-gantt.md)
- [Mobile editing](docs/MOBILE-EDITING.md)

## Contribution model

Specifications and code change through pull requests. Tasks live in Issues. Claims must link evidence and uncertainty. Large design changes require an ADR or RFC before implementation.
