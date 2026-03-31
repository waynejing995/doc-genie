# doc-genie

This project analyzes documents and code to extract structured black boxes and map relationships.

## What to do

When asked to analyze specs, documents, or code:

1. Extract black boxes with inputs, outputs, constraints
2. Map relationships: data flow, dependencies, interfaces
3. Find conflicts and implicit relationships
4. Generate reports with Mermaid diagrams

## Output Format

- Black boxes: YAML format (see `skills/genie-extract/OUTPUT.md`)
- Relationships: YAML format (see `skills/genie-relations/OUTPUT.md`)
- Insights: Markdown tables (see `skills/genie-insights/OUTPUT.md`)
- Reports: Markdown with Mermaid (see `skills/genie-report/OUTPUT.md`)

## Tools

- Use `ast-grep` for code structure analysis
- Use `pdfplumber` for PDF parsing
- Use `python-docx` for DOCX parsing
