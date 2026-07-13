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
- engineering-bible/docs/research/ios-vs-android-vs-agent-os.md: 0 chars (translated to English in place)
- engineering-bible/docs/research/prior-art-atlas.md: 0 chars (translated to English in place)
- engineering-bible/docs/research/agent-os-wider-lens.md: 0 chars (translated to English in place)
- engineering-bible/docs/research/agentos-spec-digest-product-architecture.md: 935 chars
- engineering-bible/docs/research/RES-012-fuchsia-spec-lessons.md: 43 chars

Classification:
- **Normative specs with real cyrillic: 0** — none; the normative corpus is English.
- The three former Russian prior-art atlases (ios-vs-android, prior-art-atlas, agent-os-wider-lens) have been translated to English in place and carry zero Cyrillic. They remain non-normative research (`docs/research/`); normative requirements still live in the linked architecture/product/hardware/legal/planning documents.
- The two remaining flagged files contain Russian *source quotations* (RES-012 cites the source title; the digest quotes §-excerpts) — legitimate provenance kept in original language.

## Follow-ups (owned)
- `CHECKSUMS.sha256` was regenerated for the three translated atlases in the same change (`shasum -a 256 -c` passes repo-wide), and the zero-Cyrillic claim above was verified with `perl -CSD -ne 'print if /[\x{0400}-\x{04FF}]/'` (note the `-CSD` flag — without it Perl reads bytes, not decoded UTF-8, and silently fails to match multi-byte Cyrillic, giving a false "clean" result) and cross-checked with `rg '\p{Cyrillic}'`, both over the final files.
- `FILE-MANIFEST.csv`'s three rows for these atlases are still the pre-translation byte sizes/hashes (**stale, not regenerated**). Cause: `FILE-MANIFEST.csv` is the one CRLF file in this repo, and this repo's `review`-based pre-commit gate hashes the staged diff via a Python `subprocess(..., text=True)` call, which silently normalizes `\r\n` → `\n` before hashing — so the gate's internal hash can never match the shell `git diff --cached | shasum` hash it checks against, for any diff that touches this file. A commit that regenerates it cannot clear the review-stamp gate as currently written. Needs either a review-cli fix (read the diff in binary/bytes mode) or a deliberate one-time human-approved exception; not something a docs-translation change should route around unilaterally.
