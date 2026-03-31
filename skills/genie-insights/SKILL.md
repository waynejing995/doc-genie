---
name: genie-insights
description: >
  Deep analysis: find implicit relationships, detect conflicts, discover patterns.
  Use after genie-extract and genie-relations to find insights rules cannot detect.
  Triggers: deep analysis, find conflicts, implicit relationships, semantic analysis.
---

# Deep Insight Analysis

Perform deeper analysis to find insights that automated rules cannot detect.

## Phase 1: Implicit Relationship Discovery

Analyze each component pair and ask:

1. **Semantic Dependency**: Does A's concept logically require B?
   - Example: "User Authentication" implicitly depends on "User Database"
   
2. **Data Transformation**: Does A output X and B input Y where X/Y are same data different form?
   - Example: A outputs "XML", B inputs "JSON" — same data, needs transformer
   
3. **Temporal Ordering**: Must A happen before B even if not stated?
   - Example: "Validate Input" must before "Process Payment"
   
4. **Constraint Propagation**: If A constrains X and B uses X, A indirectly constrains B?
   - Example: A says "max 100 items", B processes items — B is indirectly constrained

## Phase 2: Conflict Detection

Scan all components for:

1. **Parameter Conflicts**: Same parameter defined differently
   - Look for: timeout values, formats, limits, naming conventions
   
2. **Interface Mismatches**: Output format ≠ expected input format
   - Look for: data types, encoding, structure differences
   
3. **Constraint Contradictions**: Two rules that cannot both be true
   - Look for: "must be X" vs "must not be X"
   
4. **Terminology Inconsistency**: Same concept, different names
   - Look for: "user_id" vs "userId" vs "uid"

## Phase 3: Pattern Recognition

Identify recurring patterns:

1. **Design Patterns**: Observer, Factory, Strategy, etc.
2. **Anti-patterns**: God object, circular dependency, spaghetti
3. **Missing Components**: Gaps in the architecture
4. **Optimization Opportunities**: Redundancy, consolidation candidates

## Output Template

**ALWAYS use this exact format:**

```markdown
## Implicit Relationships

| Source | Target | Type | Confidence | Reasoning |
|--------|--------|------|------------|-----------|
| bb-001 | bb-002 | semantic_dependency | 0.85 | Auth conceptually requires user records |
| bb-003 | bb-004 | data_transform | 0.80 | Both handle same data, different formats |
| bb-005 | bb-006 | temporal | 0.90 | Validation must before processing |
| bb-007 | bb-008 | constraint_propagation | 0.75 | Shared resource constraints |

## Conflicts Detected

| Severity | Component A | Component B | Type | Issue |
|----------|-------------|-------------|------|-------|
| ❌ Error | bb-timeout-001 | bb-timeout-002 | parameter_conflict | timeout: 30s vs 60s |
| ❌ Error | bb-format-001 | bb-format-002 | interface_mismatch | Output XML ≠ Input JSON |
| ⚠️ Warning | bb-user-001 | bb-user-002 | terminology | user_id vs userId |
| ⚠️ Warning | bb-limit-001 | bb-limit-002 | constraint_conflict | max 100 vs min 200 |

## Patterns Found

### Design Patterns
- **Observer**: Event notifications between A→B→C
- **Factory**: Service creates instances of B, C, D

### Anti-patterns
- **God Object**: bb-service-001 has 15+ dependencies
- **Circular Dependency**: A→B→C→A

### Missing Components
- No error handling for Payment→Bank connection
- No retry logic for external API calls

### Optimization Opportunities
- User validation duplicated in Auth and User Service
- Three components independently implement rate limiting
```

## Example Output

```markdown
## Implicit Relationships

| Source | Target | Type | Confidence | Reasoning |
|--------|--------|------|------------|-----------|
| Auth Service | User DB | semantic_dependency | 0.95 | Authentication conceptually requires user records |
| XML Parser | JSON Builder | data_transform | 0.85 | Both handle order data, different formats |
| Input Validator | Payment Processor | temporal | 0.90 | Must validate before processing payment |

## Conflicts Detected

| Severity | Component A | Component B | Type | Issue |
|----------|-------------|-------------|------|-------|
| ❌ Error | Payment API | Order API | parameter_conflict | timeout: 30s vs 60s |
| ❌ Error | Auth Service | Legacy Auth | interface_mismatch | JWT token vs opaque token |
| ⚠️ Warning | User Service | Profile Service | terminology | user_id vs userId vs uid |

## Patterns Found

### Design Patterns
- **Observer**: Order→Payment→Notification event chain
- **Strategy**: Multiple auth providers (local, OAuth, SAML)

### Anti-patterns
- **Circular Dependency**: Auth→User→Permission→Auth
- **Duplicate Logic**: Rate limiting in 3 separate services

### Missing Components
- No circuit breaker for external payment gateway
- No dead letter queue for failed events

### Optimization Opportunities
- Consolidate 3 rate limiters into shared middleware
- Extract common validation logic into utility module
```
