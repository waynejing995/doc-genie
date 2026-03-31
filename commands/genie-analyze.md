---
name: genie-analyze
description: Analyze relationships between extracted black boxes
---

# Analyze Relationships

Analyze relationships between black boxes: data flow, dependencies, conflicts, patterns.

## Usage

After extraction:
```
/genie-analyze
```

**Focus on specific relationship type:**
```
/genie-analyze --focus data-flow
```

## Relationship Types

| Type | Description |
|------|-------------|
| data-flow | Data moving between boxes |
| dependency | Box A requires Box B |
| conflict | Boxes with incompatible constraints |
| pattern | Similar structures across boxes |

## Process

1. Load black boxes from `.genie/store/boxes.yaml`

2. For each relationship type, invoke appropriate analysis:
   - **Data Flow**: Run data-flow-agent → genie-relations skill
   - **Dependency**: Run dependency-agent → genie-relations skill
   - **Conflict**: Run conflict-agent → genie-insights skill
   - **Pattern**: Run pattern-agent → genie-insights skill

3. Aggregate results into relationship graph

4. Store relationships in `.genie/store/relations.yaml`