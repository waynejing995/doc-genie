---
name: boxmatrix-relations
description: >
  Map relationships between black boxes: data flow, dependencies, calls, constraints.
  Use after boxmatrix-extract to find connections between components.
  Triggers: relationship, dependency, data flow, connection, architecture.
---

# Map Relationships

Analyze relationships between extracted black boxes.

## Agent Integration

This skill consumes outputs from specialized agents:

| Agent | Relationship Types | Output |
|-------|-------------------|--------|
| data-flow-agent | data_flow, transform, aggregate | Flow graph |
| dependency-agent | dependency, interface, sequence | Dependency graph |

## Relationship Types

| Category | Type | Symbol | Description |
|----------|------|--------|-------------|
| Data | data_flow | → | A's output feeds B's input |
| Data | transform | ⟹ | A converts data format for B |
| Data | aggregate | ⊕ | A combines outputs from B, C, D |
| Control | dependency | ⟵ | A requires B to exist |
| Control | sequence | → | A must happen before B |
| Control | preempt | ⇏ | A can interrupt B |
| Structure | composition | ◆ | A contains B |
| Structure | extension | + | A extends B |
| Structure | version | v | A is newer version of B |
| Interaction | interface | ⟶ | A calls B's API |
| Interaction | notification | ! | A notifies B |
| Constraint | constraint | ⊢ | A limits B's behavior |
| Constraint | validation | ✓ | A validates B's output |
| Issue | conflict | ⚡ | A contradicts B |
| Issue | replication | ≡ | A duplicates B |

## Detection Methods

### Layer 1: Structural (automated via tree-sitter)
- Import/dependency analysis
- Function call detection
- Inheritance mapping

### Layer 2: Pattern-based (automated via CLI)
- Input/Output name matching
- Text reference detection (A mentions B)
- Regex pattern matching

### Layer 3: Semantic (SKILL-guided)
- Implicit dependencies
- Data transformation chains
- Temporal ordering

## Output Template

**ALWAYS use this exact format:**

```yaml
relationships:
  - source: "bb-001"
    target: "bb-002"
    type: "data_flow" | "dependency" | "interface" | etc.
    confidence: 0.0-1.0
    evidence: "Why this relationship exists"
    detection: "structural" | "pattern" | "semantic"

  - source: "bb-002"
    target: "bb-003"
    type: "dependency"
    confidence: 0.9
    evidence: "Auth service requires user database"
    detection: "structural"
```

## Example Output

```yaml
relationships:
  - source: "bb-auth-001"
    target: "bb-user-db-001"
    type: "dependency"
    confidence: 0.95
    evidence: "Authentication queries user database for credentials"
    detection: "structural"
  
  - source: "bb-auth-001"
    target: "bb-api-gateway-001"
    type: "data_flow"
    confidence: 0.9
    evidence: "Auth returns JWT token consumed by API gateway"
    detection: "pattern"
  
  - source: "bb-order-001"
    target: "bb-auth-001"
    type: "interface"
    confidence: 0.85
    evidence: "Order service calls auth to validate token"
    detection: "structural"
  
  - source: "bb-payment-001"
    target: "bb-order-001"
    type: "sequence"
    confidence: 0.8
    evidence: "Payment must process before order completes"
    detection: "semantic"
```
