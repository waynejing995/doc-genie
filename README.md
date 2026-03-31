# doc-genie

Extract black boxes from documents and code. Map relationships. Discover cross-doc insights.

> Pure-local. No external services. No LLM API calls.

## What It Does

1. **Extract** — Parse PDF/DOCX/Markdown/code into structured black boxes (inputs, outputs, constraints)
2. **Relate** — Map relationships: data flow, dependencies, calls, constraints
3. **Insight** — Deep analysis: implicit relationships, conflicts, patterns (AI-guided via SKILL)
4. **Report** — Generate reports: Markdown + Mermaid, tables, interactive web

## Quick Start

```bash
# Install
uv venv
uv pip install -e .

# Analyze documents
genie-extract spec1.pdf spec2.md src/
genie-analyze
genie-report --format markdown
```

## Skills

| Skill | Purpose | Triggers |
|-------|---------|----------|
| `genie-extract` | Extract black boxes | extract, parse, analyze |
| `genie-relations` | Map relationships | relationship, dependency |
| `genie-insights` | Deep analysis | conflicts, implicit, patterns |
| `genie-report` | Generate reports | report, visualize, diagram |

## Platform Support

| Platform | Integration |
|----------|-------------|
| Claude Code | `plugin.json` + `skills/` |
| OpenCode | `openclaw-plugin.json` + `skills/` |
| Cursor | `.cursor/rules/*.mdc` |
| Copilot | `.github/copilot-instructions.md` |
| CLI | `scripts/cli.py` |

## Architecture

```
Layer 1: Structure Extraction (ast-grep, pdfplumber, python-docx)
     │
     ▼
Layer 2: Pattern Detection (regex, IO matching, name references)
     │
     ▼
Layer 3: Semantic Analysis (SKILL-guided AI, no external LLM)
```

## License

MIT
