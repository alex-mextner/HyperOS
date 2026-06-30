# Workflow

## Intent

Haft should bias toward small reversible changes, require explicit decisions for core/domain edits,
and always verify behavior with tests or concrete runtime evidence before calling work complete.

## Defaults

```yaml
mode: standard
require_decision: true
require_verify: true
allow_autonomy: false
```

## Path Policies

```yaml
- path: "internal/artifact/**"
  mode: standard
  require_decision: true
  require_verify: true
- path: "desktop/**"
  mode: tactical
  require_decision: true
  require_verify: true
- path: ".agents/skills/**"
  mode: standard
  require_decision: true
  require_verify: true
```

## Exceptions

Use tactical mode for narrow test-only fixes or low-risk docs updates. When a change touches a
policy-heavy path, keep the decision explicit even if the code delta is small.
