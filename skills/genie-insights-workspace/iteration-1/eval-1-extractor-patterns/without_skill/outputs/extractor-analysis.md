# Extractor Analysis: Patterns, Conflicts, and Implicit Relationships

## Overview

The `lib/extractors/` directory contains 5 extractor modules for different file types:
1. `code_analyzer.py` - Python AST-based code analyzer
2. `tree_sitter_extractor.py` - Multi-language code extractor using tree-sitter
3. `markdown_extractor.py` - Markdown section and I/O extractor
4. `pdf_extractor.py` - PDF document extractor
5. `docx_extractor.py` - DOCX document extractor

---

## Patterns

### 1. Common Entry Point Pattern
Most extractors follow a similar naming convention for their main extraction function:
- `code_analyzer.py`: `CodeAnalyzer.extract_from_file(filepath)`
- `markdown_extractor.py`: `MarkdownExtractor.extract_from_file(filepath)`
- `pdf_extractor.py`: `extract_from_pdf(filepath)` (module-level function)
- `docx_extractor.py`: `extract_from_docx(filepath)` (module-level function)
- `tree_sitter_extractor.py`: `extract_structure(filepath)` (module-level function)

**Pattern**: Main entry points accept `filepath: str` and return `dict[str, Any]`.

### 2. Common Return Structure Pattern
All extractors return a dictionary with a `file` key containing the filepath:
```python
# All extractors follow this pattern
return {
    "file": filepath,
    # ... other keys
}
```

### 3. Language Detection by File Suffix
Both code extractors use a mapping from file extensions to language names:
- `code_analyzer.py`: `LANGUAGE_MAP` dictionary
- `tree_sitter_extractor.py`: `LANGUAGE_MODULES` dictionary

### 4. Section-Based Extraction Pattern
Document extractors (PDF, DOCX, Markdown) all return a `sections` key with structured content:
```python
# PDF extractor
return {"file": filepath, "sections": sections, "pages": total_pages}

# DOCX extractor
return {"file": filepath, "sections": sections, "tables": tables}

# Markdown extractor
return {"file": filepath, "sections": sections}
```

### 5. Code Structure Extraction Pattern
Both `code_analyzer.py` and `tree_sitter_extractor.py` return similar structures for code:
```python
{
    "file": filepath,
    "language": "python",
    "functions": [...],
    "classes": [...],
    "imports": [...]
}
```

---

## Conflicts

### 1. Functional Overlap: code_analyzer.py vs tree_sitter_extractor.py

**Issue**: Both extractors analyze Python code with overlapping functionality.

| Aspect | code_analyzer.py | tree_sitter_extractor.py |
|--------|------------------|---------------------------|
| Approach | Python `ast` module | tree-sitter parsing |
| Python support | Full AST access | Tree-sitter Python grammar |
| Other languages | Maps names only | Full parsing for JS/TS/C |
| Dependencies | Standard library only | Requires tree-sitter packages |

**Conflict**: For Python files, which extractor should be used? No clear guidance exists.

### 2. Language Map Inconsistencies

| Extension | code_analyzer.py | tree_sitter_extractor.py |
|-----------|------------------|---------------------------|
| `.py` | python | python |
| `.js` | javascript | javascript |
| `.jsx` | javascript | javascript |
| `.ts` | typescript | typescript |
| `.tsx` | typescript | typescript |
| `.go` | go | go (optional) |
| `.java` | java | java (optional) |
| `.rs` | rust | rust (optional) |
| `.rb` | ruby | NOT SUPPORTED |
| `.c` | NOT SUPPORTED | c |
| `.h` | NOT SUPPORTED | c |

**Conflicts**:
- `code_analyzer.py` supports `.rb` (Ruby) but `tree_sitter_extractor.py` does not
- `tree_sitter_extractor.py` supports `.c`/`.h` (C) but `code_analyzer.py` does not
- The two modules have different strategies for optional/extended languages

### 3. API Style Inconsistency

| Extractor | API Style | Example |
|-----------|-----------|---------|
| code_analyzer.py | Class-based | `CodeAnalyzer().extract_from_file(path)` |
| markdown_extractor.py | Class-based | `MarkdownExtractor().extract_from_file(path)` |
| pdf_extractor.py | Module function | `extract_from_pdf(path)` |
| docx_extractor.py | Module function | `extract_from_docx(path)` |
| tree_sitter_extractor.py | Module function | `extract_structure(path)` |

**Conflict**: Inconsistent API design makes the module harder to use programmatically.

### 4. Missing `__init__.py`

The extractors directory lacks an `__init__.py` file, meaning:
- No unified public API
- No automatic exporter registration
- Users must import each extractor individually

---

## Implicit Relationships

### 1. Code Extractor Complementarity
`code_analyzer.py` and `tree_sitter_extractor.py` could be complementary:
- Use `code_analyzer.py` for Python when full AST analysis is needed
- Use `tree_sitter_extractor.py` for multi-language projects

**Implicit relationship**: Both could share a common base interface.

### 2. Document Extractor Similarity
PDF, DOCX, and Markdown extractors share a common pattern:
- Extract sections with hierarchical levels
- Extract titles/content
- Could potentially share a `DocumentExtractor` interface

### 3. Test Fixture Sharing
All extractors use `tests/fixtures/` directory with `sample.*` files:
- `tests/fixtures/sample.py` - Used by both code extractors
- `tests/fixtures/sample.pdf` - Used by PDF extractor
- `tests/fixtures/sample.docx` - Used by DOCX extractor

**Implicit relationship**: A unified test approach could verify cross-extractor consistency.

### 4. Heading Level Semantics
All document extractors (PDF, DOCX, Markdown) use `level` to indicate heading hierarchy:
- Markdown: `level` 1-6 (based on `#` count)
- DOCX: `level` 0-N (based on Heading styles, 0 for Title)
- PDF: `level` 1-4 (based on numbering patterns)

**Implicit relationship**: A shared heading level abstraction could normalize this.

### 5. Error Handling Pattern
`tree_sitter_extractor.py` returns `{"error": "...", "file": filepath}` for unsupported languages, while other extractors have no explicit error handling pattern.

---

## Recommendations

1. **Create a unified Extractor interface/protocol** with consistent method signatures
2. **Add `__init__.py`** to expose a clean public API
3. **Document which extractor to use for which purpose** (resolve code_analyzer vs tree_sitter overlap)
4. **Normalize language maps** between code extractors or consolidate into one
5. **Consider a factory pattern** to select the appropriate extractor based on file type
6. **Standardize error handling** across all extractors