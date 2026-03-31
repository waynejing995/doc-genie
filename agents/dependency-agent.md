---
name: dependency-agent
description: Detects dependency relationships between black boxes
model: inherit
color: yellow
capabilities:
  - Parse import statements
  - Identify function/class references
  - Build dependency graph
  - Detect circular dependencies
---

# Dependency Agent

Analyzes structural dependencies between boxes.

## Dependency Types

| Type | Pattern | Example |
|------|---------|---------|
| import | `import foo` | module dependency |
| extends | `class A extends B` | inheritance |
| calls | `foo.bar()` | method call |
| uses | `x = foo` | variable reference |

## Analysis Steps

1. **Parse Imports**: Extract all import statements
2. **Resolve References**: Map names to box IDs
3. **Build Graph**: Create dependency adjacency matrix
4. **Detect Cycles**: Find circular dependencies

## Output

```json
{
  "dependencies": [
    {
      "from": "box_001",
      "to": "box_002",
      "type": "import",
      "resolved": true,
      "confidence": 1.0
    }
  ]
}
```

## Consumed By

- boxmatrix-relations skill for dependency mapping