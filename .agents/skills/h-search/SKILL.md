---
name: h-search
description: "Search past decisions, problems, and notes"
---

## Codex Invocation

This skill is explicit-only. Use it only when the user invokes $h-search; treat the text after the skill name as the request context.

# Search

Full-text search across all Haft artifacts.

Use `haft_query` tool with `action="search"` and:
- `query`: search terms
- `limit`: max results (default 20)

Use the user's explicit skill invocation text as the request context.
