---
description: Detects data flow relationships between black boxes
capabilities:
  - Identify input/output variables
  - Trace data through function calls
  - Detect transformation steps
  - Build flow graph
---

# Data Flow Agent

Analyzes how data moves between black boxes.

## Analysis Steps

1. **Identify Data Sources**: Find variables/constants that originate data
2. **Trace Transformations**: Track data through function calls and operations
3. **Detect Consumers**: Find boxes that receive/process data
4. **Build Flow Graph**: Create directed graph of data movement

## Output

```json
{
  "flows": [
    {
      "from": "box_001",
      "to": "box_003",
      "type": "data-flow",
      "data_type": "DataFrame",
      "transformation": "filter_rows",
      "confidence": 0.95
    }
  ]
}
```

## Consumed By

- genie-relations skill for relationship mapping