# HyperOS

A Fuchsia-architecture-inspired mobile OS product prototype, written in Rust, targeting a Pixel 9 form-factor simulator.

## Vision

HyperOS explores what a modern, capability-based mobile operating system could look like if designed from the ground up with Rust's safety guarantees and a Fuchsia-style microkernel architecture. The goal is a working prototype that runs in a Pixel 9 form-factor simulator — demonstrating secure process isolation, a capability-passing IPC model, and a composable UI surface — while keeping the codebase small enough for a single team to reason about.

## Status

Bootstrapping. Architecture specs are being written in `docs/specs/`. No runnable code yet.

## Repository layout

See [AGENTS.md](AGENTS.md) for a full description of the directory structure and agent workflow conventions.
