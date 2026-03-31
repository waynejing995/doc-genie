# doc-genie

A tool for extracting black boxes from documents and code, mapping relationships, and discovering cross-document insights.

## Skills

| Skill | Purpose |
|-------|---------|
| genie-extract | Extract black boxes (inputs, outputs, constraints) |
| genie-relations | Map relationships (data flow, dependencies, calls) |
| genie-insights | Deep analysis (implicit relationships, conflicts) |
| genie-report | Generate reports (Markdown, Mermaid, tables) |

## Usage

When analyzing documents or code:

1. **Extract**: Parse files into structured black boxes
2. **Relate**: Find connections between components
3. **Insight**: Discover implicit relationships and conflicts
4. **Report**: Generate documentation

## Output Templates

Each skill has an OUTPUT.md template in its directory:

- `skills/genie-extract/OUTPUT.md` — Black box YAML format
- `skills/genie-relations/OUTPUT.md` — Relationship YAML format
- `skills/genie-insights/OUTPUT.md` — Insight tables format
- `skills/genie-report/OUTPUT.md` — Report Markdown format

## Tools

- ast-grep (code parsing)
- pdfplumber (PDF parsing)
- python-docx (DOCX parsing)
- networkx (graph analysis)
