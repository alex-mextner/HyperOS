# Server Data Contract

The server treats `vault/` as a trusted, static import.

Required directories:

- `vault/wiki/` — flat Markdown wiki pages.
- `vault/imports/` — CSV projections used by the dashboard, task table, and Gantt.
- `vault/diagrams/` — optional Mermaid `.mmd` diagrams.

Required CSV files:

- `imports/gantt.csv`: `id`, `title`, `project`, `phase`, `milestone`, `priority`, `risk`, `status`, `start_date`, `end_date`.
- `imports/phases.csv`: `phase`, `start_date`, `target_date`.
- `imports/milestones.csv`: `milestone`, `title`, `target_date`.
- `imports/projects.csv`: `project_name`.

Markdown support is intentionally small: frontmatter, headings, paragraphs,
inline emphasis/code, Markdown links, Obsidian links, ordered/unordered lists,
fenced code blocks, Mermaid fences, and pipe tables.

Some imported wiki links reference anchors that are absent from the generated
target page. The server inserts hidden alias anchors for those inbound links so
deep links remain navigable without rewriting the imported vault.

Mermaid runs with `securityLevel: 'loose'` because the vault is not user-editable
at runtime. Do not use this setting for untrusted collaborative content without
adding sanitization or a stricter Mermaid configuration.
