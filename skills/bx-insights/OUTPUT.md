# Output Template: Insights

## Implicit Relationships

| Source | Target | Type | Confidence | Reasoning |
|--------|--------|------|------------|-----------|
| bb-001 | bb-002 | semantic_dependency | 0.85 | Auth requires user records |

## Conflicts

| Severity | Component A | Component B | Type | Issue |
|----------|-------------|-------------|------|-------|
| ❌ Error | bb-001 | bb-002 | parameter_conflict | timeout: 30s vs 60s |

## Patterns

### Design Patterns
- **Observer**: Event chain A→B→C

### Anti-patterns
- **Circular Dependency**: A→B→C→A

### Missing Components
- No error handling for external API

## Subagent Chunk Format

When processing in parallel, each subagent analyzes a subset of boxes:

```json
{
  "implicit_relationships": [
    {
      "source": "bb-001",
      "target": "bb-002",
      "type": "semantic_dependency",
      "confidence": 0.85,
      "reasoning": "Why this exists"
    }
  ],
  "conflicts": [
    {
      "severity": "error",
      "component_a": "bb-001",
      "component_b": "bb-002",
      "type": "parameter_conflict",
      "description": "timeout: 30s vs 60s"
    }
  ]
}
```
