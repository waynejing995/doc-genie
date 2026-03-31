---
name: genie-extract
description: Extract black boxes from documents and code files
---

# Extract Black Boxes

Extract structured black boxes from files using tree-sitter (code) or document parsers (PDF/DOCX/Markdown).

## Usage

**Single file:**
```
/genie-extract path/to/file.py
```

**Directory:**
```
/genie-extract path/to/docs/
```

**With depth profile:**
```
/genie-extract path/to/code/ --depth deep
```

## Depth Profiles

| Depth | Abstraction Level | Box Size |
|-------|------------------|----------|
| quick | module/chapter | ~500 chars |
| medium | function/paragraph | ~100 chars |
| deep | statement/sentence | ~30 chars |

## Process

1. Run CLI for fast parsing:
   ```bash
   uv run --directory $CLAUDE_PLUGIN_ROOT genie extract <path> --output json --depth medium
   ```

2. Read JSON output from `.genie/cache/`

3. Apply genie-extract skill to transform raw boxes into structured black boxes

4. Return YAML formatted black boxes following OUTPUT.md template