# Public derived data

This directory contains machine-readable projections used by the public portal and import tooling.

## `tasks.csv.gz`

A gzip-compressed snapshot of the canonical 327-item planning dataset.

- It is a derived publication artifact, not a substitute for live GitHub Issues after import.
- Stable `AOS-*` IDs are the reconciliation keys.
- The portal overlays live Issue state and URLs on matching planning records.
- GitHub Issues become the canonical write layer for imported work.
- CSV remains an auditable interchange and recovery representation.
- User-provided ZIP/PDF source archives are not included here or elsewhere in the public repository.

The dataset contains descriptions, acceptance criteria, dependencies, specification links, dates, evidence requirements, phases, documentation volumes, and review gates.
