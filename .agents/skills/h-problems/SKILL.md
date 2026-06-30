---
name: h-problems
description: "List active engineering problems"
---

## Codex Invocation

This skill is explicit-only. Use it only when the user invokes $h-problems; treat the text after the skill name as the request context.

# Active Problems

Show active ProblemCards, optionally filtered by context.

Use `haft_problem` tool with `action="select"` and:
- `context`: optional filter by context name

Use the user's explicit skill invocation text as the request context.
