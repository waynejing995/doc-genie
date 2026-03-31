---
description: Extracts black boxes from a single chunk (file or section)
capabilities:
  - Parse code using tree-sitter
  - Parse documents using pdfplumber/python-docx
  - Extract structure (functions, classes, sections)
  - Output structured black boxes
---

# Extract Worker Agent

Performs actual extraction on a single chunk.

## Supported Formats

| Format | Parser | Extracts |
|--------|--------|----------|
| .py, .js, .ts, .c | tree-sitter | functions, classes, imports, variables |
| .md | markdown-it-py | headings, paragraphs, code blocks |
| .pdf | pdfplumber | pages, tables, headings |
| .docx | python-docx | paragraphs, headings, tables |

## Extraction Rules

Based on depth profile:

| Depth | Granularity | Example |
|-------|-------------|---------|
| quick | module/chapter | Whole file as one box |
| medium | function/paragraph | Each function as box |
| deep | statement/sentence | Each statement as box |

## Output Format

```json
{
  "boxes": [
    {
      "id": "box_001",
      "type": "function",
      "name": "process_data",
      "source": "file.py:10-25",
      "content": "...",
      "metadata": {...}
    }
  ]
}
```