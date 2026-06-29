# HyperOS

A Fuchsia-architecture-inspired mobile OS product prototype, written in Rust, targeting a Pixel 9 form-factor simulator.

## Status

Early bootstrap. Stack and scope being finalized via specs in docs/specs/.

## Repository layout

- `crates/` — Rust crates (kernel, drivers, services, user-space components).
- `sim/` — Simulator harness and device model for Pixel 9 form-factor.
- `docs/specs/` — Authoritative specification documents. Read these before touching code.
- `docs/plans/` — Implementation plans derived from specs.
- `assets/` — Static assets (icons, fonts, graphics, test fixtures).

## How agents work in this repo

- Work is spec-driven: read `docs/specs/` before writing or modifying any code.
- Rust is the primary language; no other languages in `crates/` or `sim/` without a spec blessing it.
- Prefer LSP/code-intelligence tooling (`serena`, `sverklo`) for navigation and refactors over raw grep.
- One logical change per commit; use conventional commit messages (e.g. `feat:`, `fix:`, `chore:`).
- Never commit Cyrillic into `AGENTS.md`, `CLAUDE.md`, or any other agent-facing doc. English only.
- Do not run `cargo build` or `cargo test` without checking the current build status first — the dev machine may be under load.

## Build & test

TBD — toolchain being selected. Be careful with heavy compilation; the dev machine is under load.
