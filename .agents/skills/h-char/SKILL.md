---
name: h-char
description: "Define comparison dimensions for a framed problem"
---

## Codex Invocation

This skill is explicit-only. Use it only when the user invokes $h-char; treat the text after the skill name as the request context.

# Characterize

Define the characteristic space — what dimensions matter and how they're measured. Without this, comparisons are arbitrary.

Current runtime persists characterization on the ProblemCard via `haft_problem(action="characterize")`. Define dimensions once, keep parity rules explicit, then carry that same characterized space into `$h-explore` and `$h-compare`.

Recommended fields to define in your reasoning:
- `name`: dimension name (e.g., "throughput", "ops complexity")
- `scale_type`: ordinal, ratio, nominal
- `unit`: measurement unit
- `polarity`: higher_better or lower_better
- `how_to_measure`: measurement procedure
- `parity_rules`: what must be equal across variants for fair comparison

Before calling `haft_problem(action="characterize")`, validate your own
dimension fields: `scale_type` must be one of `ordinal`, `ratio`, or
`nominal`, and `polarity` must be `higher_better` or `lower_better`. If a
dimension does not fit those values, either normalize it into one of them or ask
for a clearer measurement definition.

Use the user's explicit skill invocation text as the request context.
