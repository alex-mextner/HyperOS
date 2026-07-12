---
id: AOS-ARCH-001
title: Portable System Architecture
status: foundation
---

# Portable System Architecture

## Principle

The operating system is divided into architecture packages, board packages, device services, and portable system/product layers. Product code depends on owned IDL contracts rather than SoC-, Linux-, Android-, or vendor-specific APIs.

## Layer model

1. **Microkernel** — scheduling, address spaces, interrupts, capabilities, IPC, timers, and minimal platform primitives.
2. **Architecture package** — AArch64 and later RISC-V/x86-64 CPU, MMU, interrupt, and boot implementations.
3. **Board package** — memory map, clocks, resets, buses, power domains, and device enumeration for one board.
4. **Device services** — display, GPU, camera, audio, storage, network, modem, sensor, power, and secure-service contracts.
5. **System services** — component lifecycle, package management, storage, identity, policy, update, recovery, and observability.
6. **Product layer** — entity graph, actions, history, agents, shell, integrations, backup, and sync.

## Portability rule

No portable layer may expose Linux file descriptors, ioctl values, Binder objects, Android HAL types, vendor structs, or board addresses. Platform adapters translate into native versioned IDL types.

## Pixel 9 boundary

Pixel 9 work may use stock Android/Linux only as an evidence oracle, trace source, recovery environment, or temporary sidecar. Every retained dependency requires a replacement issue, owner, legal basis, and stop date.

## Acceptance

A component is portable when it runs unchanged against QEMU and at least one physical board adapter, with conformance tests proving identical observable contract behaviour.
