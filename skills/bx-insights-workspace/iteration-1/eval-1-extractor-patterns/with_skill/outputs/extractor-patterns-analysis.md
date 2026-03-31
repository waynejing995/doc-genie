# Extractor Patterns Analysis

## Implicit Relationships

| Source | Target | Type | Confidence | Reasoning |
|--------|--------|------|------------|-----------|
| code_analyzer.py | tree_sitter_extractor.py | semantic_dependency | 0.95 | Both extract identical structure (functions, classes, imports) from source code with overlapping language support (Python, JS, TS, Go, Java, Rust) |
| markdown_extractor.py | pdf_extractor.py | data_transform | 0.80 | Both output sections with title/level/content structure - same data model, different input formats |
| pdf_extractor.py | docx_extractor.py | data_transform | 0.85 | Both extract document sections with heading levels - could share common section model |
| tree_sitter_extractor.py | code_analyzer.py | temporal | 0.75 | tree-sitter provides more robust multi-language parsing; could be used as primary implementation with code_analyzer as fallback |
| markdown_extractor.py | docx_extractor.py | constraint_propagation | 0.70 | Both parse document structure; changes to section model would affect both |

## Conflicts Detected

| Severity | Component A | Component B | Type | Issue |
|----------|-------------|-------------|------|-------|
| Error | CodeAnalyzer | extract_from_pdf | interface_mismatch | Class-based API vs function-based API - no common interface |
| Error | CodeAnalyzer | tree_sitter_extractor | parameter_conflict | LANGUAGE_MAP dictionaries differ: code_analyzer includes Ruby, tree_sitter includes C |
| Error | CodeAnalyzer.extract_from_file | extract_structure | interface_mismatch | Different return keys: both have file/language/functions/classes/imports but tree_sitter adds "error" field |
| Warning | MarkdownExtractor.extract_from_file | extract_from_pdf | interface_mismatch | Same method purpose, different naming: extract_from_file() vs extract_from_pdf() |
| Warning | pdf_extractor._is_heading | docx_extractor._extract_heading_level | terminology | Different heading level detection: regex patterns vs Word style names |
| Warning | markdown_extractor | pdf_extractor | interface_mismatch | Section data structures differ: markdown has "line", pdf has "page" |

## Patterns Found

### Design Patterns

- **Strategy Pattern (implicit)**: Each extractor implements a different strategy for extracting content based on file type, but without a formal interface
- **Adapter Pattern**: Each extractor adapts a third-party library:
  - code_analyzer → Python `ast` module
  - tree_sitter_extractor → `tree-sitter` parsers
  - pdf_extractor → `pdfplumber`
  - docx_extractor → `python-docx`
  - markdown_extractor → Python `re` module

### Anti-patterns

- **Inconsistent Interface**: No common base class or protocol exists; mix of class-based (CodeAnalyzer, MarkdownExtractor) and function-based (extract_from_pdf, extract_from_docx, extract_structure) APIs
- **Duplicate Logic**: Language detection implemented in both CodeAnalyzer.LANGUAGE_MAP and tree_sitter_extractor.LANGUAGE_MODULES with different mappings
- **Incomplete Abstraction**: CodeAnalyzer has language detection for Ruby (.rb) but no implementation; tree_sitter_extractor has Go/Java/Rust as optional with None placeholders
- **Inconsistent Error Handling**: tree_sitter_extractor returns {"error": "..."} for unsupported languages; code_analyzer silently returns empty lists; document extractors have no error handling

### Missing Components

- **No __init__.py**: The extractors directory lacks an __init__.py to expose a unified API or base class
- **No Base Extractor Class/Protocol**: Missing common interface that defines extract_from_file(filepath) -> dict
- **No Factory/Router**: No mechanism to select appropriate extractor based on file type
- **No Common Output Model**: No shared Section or CodeStructure dataclass to ensure consistency

### Optimization Opportunities

- **Consolidate Language Detection**: Create shared language detection utility used by both code extractors
- **Unify Entry Point Naming**: Standardize to either all class-based (Extractor.extract_from_file()) or all function-based (extract_from_file(filepath))
- **Create Base Protocol**: Define `ExtractedContent` TypedDict or dataclass with common fields (file, type, metadata)
- **Merge Code Extractors**: tree_sitter_extractor provides more robust parsing; code_analyzer could be deprecated or merged
- **Share Section Model**: markdown/pdf/docx all extract sections - create shared `Section` dataclass with optional fields (page, line, level, title, content)

## Detailed Analysis

### API Design Comparison

| Extractor | Type | Entry Point | Return Keys |
|-----------|------|-------------|-------------|
| CodeAnalyzer | Class | extract_from_file(filepath) | file, language, functions, classes, imports |
| MarkdownExtractor | Class | extract_from_file(filepath) | file, sections |
| tree_sitter_extractor | Functions | extract_structure(filepath) | file, language, functions, classes, imports, error? |
| pdf_extractor | Function | extract_from_pdf(filepath) | file, sections, pages |
| docx_extractor | Function | extract_from_docx(filepath) | file, sections, tables |

### Language Support Matrix

| Language | code_analyzer | tree_sitter_extractor |
|----------|---------------|------------------------|
| Python | Full (ast) | Full (tree-sitter) |
| JavaScript | Stub | Full (tree-sitter) |
| TypeScript | Stub | Full (tree-sitter) |
| C | - | Full (tree-sitter) |
| Go | Stub | Optional |
| Java | Stub | Optional |
| Rust | Stub | Optional |
| Ruby | Detected only | - |

### Output Structure Comparison

**Code Extractors (code_analyzer, tree_sitter_extractor):**
```python
{
    "file": str,
    "language": str,
    "functions": [{"name", "line", "args?"}],
    "classes": [{"name", "line", "bases?"}],
    "imports": [{"module", "line", "names?"}],
    # tree_sitter only:
    "error": str  # optional, when unsupported
}
```

**Document Extractors (markdown, pdf, docx):**
```python
{
    "file": str,
    "sections": [
        {
            "title": str,
            "level": int,
            "content": str,
            # markdown only:
            "line": int,
            "io": {"inputs": [], "outputs": []},
            # pdf only:
            "page": int,
            # docx only:
            "type": "heading" | "content",
            "parent_heading": str?
        }
    ],
    # pdf only:
    "pages": int,
    # docx only:
    "tables": [[str]]
}
```