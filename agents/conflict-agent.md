---
name: conflict-agent
description: Detects conflicts and incompatibilities between black boxes
model: inherit
color: red
capabilities:
  - Find naming conflicts
  - Detect semantic contradictions
  - Identify incompatible constraints
  - Report conflict severity
---

# Conflict Agent

Identifies potential conflicts that need resolution.

## Conflict Types

| Type | Description | Severity |
|------|-------------|----------|
| naming | Same name, different semantics | medium |
| semantic | Contradictory requirements | high |
| constraint | Incompatible type/format | high |
| duplicate | Exact duplicates | low |

## Analysis Steps

1. **Name Matching**: Find boxes with same/similar names
2. **Semantic Comparison**: Compare descriptions/behaviors
3. **Constraint Check**: Verify type/format compatibility
4. **Severity Scoring**: Rate conflict impact

## Output

```json
{
  "conflicts": [
    {
      "boxes": ["box_001", "box_005"],
      "type": "naming",
      "description": "Both named 'process' but different signatures",
      "severity": "medium",
      "suggestion": "Rename one to 'process_input'"
    }
  ]
}
```

## Consumed By

- boxmatrix-insights skill for conflict insights