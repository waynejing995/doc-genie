---
name: genie-report
description: Generate analysis report with diagrams
---

# Generate Report

Generate structured report with Mermaid diagrams, tables, and insights.

## Usage

```
/genie-report [output.md]
```

**Format options:**
```
/genie-report --format html
/genie-report --format dot
```

## Output Sections

1. **Executive Summary**: Key findings and recommendations
2. **Black Box Inventory**: All extracted boxes by type
3. **Relationship Graph**: Mermaid diagram showing connections
4. **Insights**: Detected conflicts, patterns, opportunities
5. **Metrics**: Analysis statistics (boxes, relations, coverage)

## Process

1. Load black boxes and relationships from `.genie/store/`

2. Apply genie-report skill to format output

3. Generate Mermaid diagrams:
   - Flowchart for dependency chains
   - Graph for data flows
   - Table for conflicts

4. Write report to specified output path (default: `genie-report.md`)