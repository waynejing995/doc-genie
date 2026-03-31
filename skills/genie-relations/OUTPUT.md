# Output Template: Relationships

```yaml
relationships:
  - source: "bb-001"
    target: "bb-002"
    type: "data_flow" | "dependency" | "interface" | "sequence" | "constraint" | "conflict"
    confidence: 0.0-1.0
    evidence: "Why this relationship exists"
```

## Confidence Levels

- 0.9+: Clear match (input=output name, explicit reference)
- 0.7-0.9: Likely match (similar names, pattern match)
- <0.7: Possible (semantic similarity)

## Subagent Chunk Format

When processing in parallel, each subagent analyzes a subset:

```yaml
relationships:
  - source: "bb-auth-001"
    target: "bb-user-db-001"
    type: "dependency"
    confidence: 0.95
    evidence: "Auth queries user database for credentials"
```
