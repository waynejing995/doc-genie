# Output Template: Report

```markdown
# System Analysis Report

> Generated: YYYY-MM-DD HH:MM
> Documents: N | Black Boxes: N | Relationships: N | Issues: N

## Executive Summary

[2-3 sentence overview]

## Architecture

\`\`\`mermaid
graph TD
    A[Auth] -->|token| B[Gateway]
    B -->|route| C[Order]
\`\`\`

## Black Boxes

| ID | Name | Inputs | Outputs | Status |
|----|------|--------|---------|--------|
| bb-001 | Auth | credentials | token | ✅ |

## Relationships

| Source | → | Target | Type |
|--------|---|--------|------|
| bb-001 | → | bb-002 | data_flow |

## Issues

| Severity | Type | Description |
|----------|------|-------------|
| ❌ Error | interface_mismatch | Output format differs |

## Insights

[From genie-insights if available]

## Recommendations

1. [Recommendation 1]
2. [Recommendation 2]
```
