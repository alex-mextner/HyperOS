# Public derived data

This directory contains machine-readable projections used by the public portal and import tooling.

## `tasks/`

An open JSON projection of the canonical 327-item planning dataset, partitioned by implementation phase.

- `tasks/index.json` is the manifest and authoritative published record count.
- `tasks/phase-0.json` through `tasks/phase-8.json` contain the task records.
- Stable `AOS-*` IDs are the reconciliation keys.
- The portal overlays live Issue state and URLs on matching planning records.
- GitHub Issues become the canonical write layer for imported work.
- JSON remains an auditable interchange and recovery representation.
- User-provided ZIP/PDF source archives are not included here or elsewhere in the public repository.

The portal projection includes titles, summaries, hierarchy, dependencies, specification links, dates, priority, risk, phase, documentation volume, claims, experiments, and review gates. Detailed acceptance and evidence text remains in the canonical planning corpus and is copied into Issues during import.
