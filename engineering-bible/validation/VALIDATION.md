# Engineering Bible Validation

Corrected report (a previous pass under-scoped the cyrillic check and wrongly reported 0).

- Markdown files total: 182
- Canonical docs: 162
- Unique AOS IDs: 158
- Duplicate IDs: 0
- Broken internal links: 0 OK
- Project name HyperOS in docs: 0
- Kernel approach: fork the entire Fuchsia tree (corrected; 0 owned-microkernel assertions)

## Cyrillic (honest accounting)
Real Cyrillic characters (Unicode U+0400–U+04FF), not em-dashes:
- engineering-bible/docs/research/ios-vs-android-vs-agent-os.md: 17210 chars
- engineering-bible/docs/research/prior-art-atlas.md: 6865 chars
- engineering-bible/docs/research/agent-os-wider-lens.md: 6607 chars
- engineering-bible/docs/research/agentos-spec-digest-product-architecture.md: 935 chars
- engineering-bible/docs/research/RES-012-fuchsia-spec-lessons.md: 43 chars

Classification:
- **Normative specs with real cyrillic: 0** — none; the normative corpus is English.
- The five flagged files are all under /research/: three are non-normative Russian prior-art analyses (now marked `Language: Russian`), and two contain Russian *source quotations* (RES-012 cites the source title; the digest quotes §-excerpts) — legitimate provenance kept in original language.

## Follow-ups (owned)
- English summaries of the three Russian atlases (ios-vs-android, prior-art-atlas, agent-os-wider-lens) — a research task, not a blocker.
