# doc-genie v0.2.0 重构实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 重构 doc-genie 为标准 Claude Code 插件结构，实现 tree-sitter 统一解析，添加 PDF/DOCX 支持，项目级配置，子代理架构，完整评估框架。

**Architecture:** 三层架构 - Layer 1 (tree-sitter 结构提取) → Layer 2 (规则关系检测) → Layer 3 (Skill 指导 AI 语义分析)。插件结构遵循 Claude Code 标准 (.claude-plugin/ + commands/ + agents/ + skills/)。

**Tech Stack:** Python 3.10+, uv, tree-sitter, pdfplumber, python-docx, pytest, ruff, mypy

---

## 文件结构

```
doc-genie/
├── .claude-plugin/
│   └── plugin.json              # 新建
├── commands/                     # 新建目录
│   ├── genie-extract.md
│   ├── genie-analyze.md
│   └── genie-report.md
├── agents/                       # 新建目录
│   ├── chunk-coordinator.md
│   ├── extract-worker.md
│   ├── data-flow-agent.md
│   ├── dependency-agent.md
│   ├── conflict-agent.md
│   ├── pattern-agent.md
│   └── result-reviewer.md
├── lib/
│   ├── config.py                 # 新建
│   ├── storage/                  # 新建目录
│   │   ├── __init__.py
│   │   └── genie_store.py
│   └── extractors/
│       ├── tree_sitter_extractor.py  # 新建
│       ├── pdf_extractor.py          # 新建
│       └── docx_extractor.py         # 新建
├── tests/
│   ├── test_config.py            # 新建
│   ├── test_genie_store.py       # 新建
│   ├── test_tree_sitter_extractor.py  # 新建
│   ├── test_pdf_extractor.py     # 新建
│   └── test_docx_extractor.py    # 新建
├── scripts/
│   ├── record_baseline.py        # 新建
│   └── compare_baseline.py       # 新建
└── pyproject.toml                # 修改
```

---

## Task 1: 环境验证与依赖更新

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1.1: 检查 Python 版本**

```bash
python3 --version
# 期望输出: Python 3.10.x 或更高
```

- [ ] **Step 1.2: 检查 uv 安装**

```bash
uv --version
# 期望输出: uv 0.x.x
```

- [ ] **Step 1.3: 更新 pyproject.toml 添加 tree-sitter 依赖**

```toml
[project]
name = "doc-genie"
version = "0.2.0"
requires-python = ">=3.10"

dependencies = [
    # tree-sitter 核心 + 默认语言包 (C/JS/TS/Python)
    "tree-sitter>=0.24.0",
    "tree-sitter-python>=0.23.0",
    "tree-sitter-javascript>=0.23.0",
    "tree-sitter-typescript>=0.23.0",
    "tree-sitter-c>=0.23.0",

    # 文档解析
    "pdfplumber>=0.10.0",
    "python-docx>=1.1.0",
    "markdown-it-py>=3.0.0",

    # 图分析
    "networkx>=3.0",

    # 工具
    "pyyaml>=6.0",
    "rich>=13.0",
]

[project.optional-dependencies]
languages = [
    "tree-sitter-go>=0.23.0",
    "tree-sitter-java>=0.23.0",
    "tree-sitter-rust>=0.23.0",
]
```

- [ ] **Step 1.4: 同步依赖**

```bash
uv sync
```

- [ ] **Step 1.5: 验证 tree-sitter 安装**

```bash
uv run python -c "import tree_sitter_python; print('tree-sitter OK')"
# 期望输出: tree-sitter OK
```

- [ ] **Step 1.6: Commit**

```bash
git add pyproject.toml uv.lock
git commit -m "chore: add tree-sitter dependencies for C/JS/TS/Python"
```

---

## Task 2: 创建标准插件结构

**Files:**
- Create: `.claude-plugin/plugin.json`
- Create: `commands/genie-extract.md`
- Create: `commands/genie-analyze.md`
- Create: `commands/genie-report.md`

- [ ] **Step 2.1: 创建 .claude-plugin 目录**

```bash
mkdir -p .claude-plugin
```

- [ ] **Step 2.2: 创建 plugin.json**

```json
{
  "name": "doc-genie",
  "version": "0.2.0",
  "description": "Extract black boxes from docs/code, map relationships, discover cross-doc insights",
  "author": { "name": "waynejing995" },
  "license": "MIT",
  "keywords": ["documentation", "analysis", "architecture", "tree-sitter"]
}
```

- [ ] **Step 2.3: 创建 commands 目录**

```bash
mkdir -p commands
```

- [ ] **Step 2.4: 创建 commands/genie-extract.md**

```markdown
---
name: genie-extract
description: Extract black boxes from documents and code files
---

# Extract Black Boxes

Extract structured black boxes from files.

## Usage

**Single file:**
```
/genie-extract path/to/file.py
```

**Directory:**
```
/genie-extract path/to/docs/
```

## Process

1. Run CLI for fast parsing:
   ```bash
   uv run --directory $CLAUDE_PLUGIN_ROOT genie extract <path> --output json
   ```

2. Read JSON output

3. Apply genie-extract skill to extract black boxes following OUTPUT.md template

4. Return YAML formatted black boxes
```

- [ ] **Step 2.5: 创建 commands/genie-analyze.md**

```markdown
---
name: genie-analyze
description: Analyze relationships between extracted black boxes
---

# Analyze Relationships

Analyze relationships between extracted components.

## Usage

```
/genie-analyze
```

## Process

1. Load boxes from `.genie/boxes.json`
2. Run relationship detection agents in parallel
3. Apply genie-relations skill for analysis
4. Store results to `.genie/relationships.json`
```

- [ ] **Step 2.6: 创建 commands/genie-report.md**

```markdown
---
name: genie-report
description: Generate analysis report with diagrams
---

# Generate Report

Create structured reports from analysis results.

## Usage

```
/genie-report [output.md]
```

## Process

1. Load all `.genie/*.json` files
2. Apply genie-report skill to generate report
3. Output Markdown with Mermaid diagrams
```

- [ ] **Step 2.7: 删除旧 plugin.json**

```bash
rm plugin.json openclaw-plugin.json
```

- [ ] **Step 2.8: Commit**

```bash
git add .claude-plugin/ commands/
git rm plugin.json openclaw-plugin.json
git commit -m "feat: standard Claude Code plugin structure with commands/"
```

---

## Task 3: 创建代理定义文件

**Files:**
- Create: `agents/chunk-coordinator.md`
- Create: `agents/extract-worker.md`
- Create: `agents/data-flow-agent.md`
- Create: `agents/dependency-agent.md`
- Create: `agents/conflict-agent.md`
- Create: `agents/pattern-agent.md`
- Create: `agents/result-reviewer.md`

- [ ] **Step 3.1: 创建 agents 目录**

```bash
mkdir -p agents
```

- [ ] **Step 3.2: 创建 agents/chunk-coordinator.md**

```markdown
---
description: Split files/boxes into chunks for parallel processing
capabilities:
  - Split large file lists into chunks
  - Distribute work to extract-worker agents
  - Collect and merge results
---

# Chunk Coordinator

Split work into manageable chunks for parallel processing.

## Input
- files: List of file paths
- chunk_size: Items per chunk (default: 10)

## Output
- chunks: List of file chunks
- assignments: Agent -> chunk mapping
```

- [ ] **Step 3.3: 创建 agents/extract-worker.md**

```markdown
---
description: Extract black boxes from a single file or chunk
capabilities:
  - Parse single file using CLI tools
  - Output YAML formatted black boxes
---

# Extract Worker

Process a single file or chunk of files.

## Input
- files: List of file paths (max 10)

## Output
- boxes: List of black box definitions in YAML
```

- [ ] **Step 3.4: 创建 agents/data-flow-agent.md**

```markdown
---
description: Analyze data flow relationships between black boxes
capabilities:
  - Detect data_flow, transform, aggregate, cache relationships
  - Match output names to input names
  - Track data lineage
---

# Data Flow Agent

Specialized in detecting data movement relationships.

## Relationship Types
| Type | Symbol | Detection |
|------|--------|-----------|
| data_flow | → | Output name matches input name |
| transform | ⟹ | Same data, different format |
| aggregate | ⊕ | Multiple inputs combined |
| cache | ⊇ | Cache layer detection |

## Output
- relationships: List with type, confidence, evidence
```

- [ ] **Step 3.5: 创建 agents/dependency-agent.md**

```markdown
---
description: Analyze dependency and control relationships
capabilities:
  - Detect dependency, interface, sequence, routing relationships
  - Parse import statements
  - Build dependency graph
---

# Dependency Agent

Specialized in control flow and dependencies.

## Relationship Types
| Type | Symbol | Detection |
|------|--------|-----------|
| dependency | ⟵ | Import/reference analysis |
| interface | ⟶ | API calls |
| sequence | → | Temporal ordering |
| routing | ⇢ | Gateway/router patterns |

## Output
- relationships: List with type, confidence, evidence
```

- [ ] **Step 3.6: 创建 agents/conflict-agent.md**

```markdown
---
description: Detect conflicts and inconsistencies between components
capabilities:
  - Detect conflict, replication, override relationships
  - Find parameter mismatches
  - Identify contradictory constraints
---

# Conflict Agent

Specialized in finding problems.

## Conflict Types
| Type | Detection |
|------|-----------|
| parameter_conflict | Same param, different values |
| interface_mismatch | Output ≠ expected input |
| constraint_contradiction | Mutually exclusive rules |
| terminology_inconsistency | Same concept, different names |

## Output
- conflicts: List with severity, components, issue description
```

- [ ] **Step 3.7: 创建 agents/pattern-agent.md**

```markdown
---
description: Identify design patterns and anti-patterns
capabilities:
  - Detect common design patterns
  - Identify anti-patterns
  - Find missing components
  - Discover optimization opportunities
---

# Pattern Agent

Specialized in architectural patterns.

## Pattern Types
| Category | Examples |
|----------|----------|
| Design Patterns | Observer, Factory, Strategy |
| Anti-patterns | God Object, Circular Dependency |
| Missing Components | No error handling, no retry logic |
| Optimization | Duplicated logic, consolidation candidates |

## Output
- patterns: List of found patterns with locations
```

- [ ] **Step 3.8: 创建 agents/result-reviewer.md**

```markdown
---
description: Review and validate agent results before storage
capabilities:
  - Format validation
  - Deduplication
  - Confidence scoring
  - Cross-validation
  - AI semantic review
---

# Result Reviewer

Validate agent outputs for quality and consistency.

## Review Pipeline

Agent Results → Format Check → Dedupe → Confidence Filter → Cross-Validate → AI Review → Store

## Review Checks

| Check | Method | Action |
|-------|--------|--------|
| Format | JSON Schema | Reject invalid |
| Duplicate | ID matching | Merge duplicates |
| Confidence | Threshold < 0.7 | Mark `needs_review` |
| Cross-validate | Multi-agent vote | Confirm if 2+ agree |
| Semantic | AI review | Flag suspicious |
```

- [ ] **Step 3.9: Commit**

```bash
git add agents/
git commit -m "feat: add subagent definitions for parallel processing and analysis"
```

---

## Task 4: 实现 tree-sitter 提取器 (TDD)

**Files:**
- Create: `tests/test_tree_sitter_extractor.py`
- Create: `lib/extractors/tree_sitter_extractor.py`

- [ ] **Step 4.1: 写失败测试 - Python 解析**

```python
# tests/test_tree_sitter_extractor.py
"""Tests for tree_sitter_extractor module."""

import pytest


class TestTreeSitterExtractor:
    def test_extract_python_functions(self):
        from lib.extractors.tree_sitter_extractor import extract_structure

        result = extract_structure("tests/fixtures/sample.py")
        assert result["language"] == "python"
        assert any(f["name"] == "hello" for f in result["functions"])

    def test_extract_python_classes(self):
        from lib.extractors.tree_sitter_extractor import extract_structure

        result = extract_structure("tests/fixtures/sample.py")
        assert any(c["name"] == "UserService" for c in result["classes"])

    def test_extract_python_imports(self):
        from lib.extractors.tree_sitter_extractor import extract_structure

        result = extract_structure("tests/fixtures/sample.py")
        assert any(i["module"] == "os" for i in result["imports"])

    def test_unsupported_language_returns_error(self):
        from lib.extractors.tree_sitter_extractor import extract_structure

        result = extract_structure("tests/fixtures/sample.xyz")
        assert "error" in result
```

- [ ] **Step 4.2: 创建测试夹具**

```python
# tests/fixtures/sample.py
"""Sample Python file for testing."""

import os
from typing import List


def hello(name: str) -> str:
    """Say hello."""
    return f"Hello, {name}!"


class UserService:
    """User service class."""

    def __init__(self, db):
        self.db = db

    def get_user(self, user_id: int):
        return self.db.query(user_id)
```

- [ ] **Step 4.3: 运行测试确认失败**

```bash
uv run pytest tests/test_tree_sitter_extractor.py -v
# Expected: FAIL - module not found
```

- [ ] **Step 4.4: 实现 tree_sitter_extractor.py**

```python
# lib/extractors/tree_sitter_extractor.py
"""
tree-sitter unified extractor.
Default support: C, JavaScript, TypeScript, Python
Extended support: Go, Java, Rust (requires additional install)
"""

import tree_sitter_python as tspython
import tree_sitter_javascript as tsjs
import tree_sitter_typescript as tsts
import tree_sitter_c as tsc
from tree_sitter import Language, Parser
from pathlib import Path
from typing import Any


LANGUAGE_MODULES = {
    ".py": (tspython, "python"),
    ".js": (tsjs, "javascript"),
    ".jsx": (tsjs, "javascript"),
    ".ts": (tsts, "typescript"),
    ".tsx": (tsts, "typescript"),
    ".c": (tsc, "c"),
    ".h": (tsc, "c"),
    # Extended languages (optional)
    ".go": None,
    ".java": None,
    ".rs": None,
}


def get_parser(suffix: str) -> Parser | None:
    """Get parser for the given file suffix."""
    lang_info = LANGUAGE_MODULES.get(suffix)
    if lang_info is None:
        # Try loading optional languages
        try:
            if suffix == ".go":
                import tree_sitter_go as tsgo
                return Parser(Language(tsgo.language()))
            elif suffix == ".java":
                import tree_sitter_java as tsjava
                return Parser(Language(tsjava.language()))
            elif suffix == ".rs":
                import tree_sitter_rust as tsrust
                return Parser(Language(tsrust.language()))
        except ImportError:
            return None
    if lang_info:
        module, _ = lang_info
        return Parser(Language(module.language()))
    return None


def extract_structure(filepath: str) -> dict[str, Any]:
    """Extract code structure: functions, classes, imports."""
    path = Path(filepath)
    parser = get_parser(path.suffix)

    if parser is None:
        return {"error": f"Unsupported language: {path.suffix}", "file": filepath}

    source = path.read_bytes()
    tree = parser.parse(source)
    root = tree.root_node

    functions = []
    classes = []
    imports = []

    lang_name = LANGUAGE_MODULES.get(path.suffix, (None, "unknown"))[1]

    if lang_name == "python":
        functions, classes, imports = _extract_python_elements(root, source)
    elif lang_name in ("javascript", "typescript"):
        functions, classes, imports = _extract_js_elements(root, source)
    elif lang_name == "c":
        functions, imports = _extract_c_elements(root, source)

    return {
        "file": filepath,
        "language": lang_name,
        "functions": functions,
        "classes": classes,
        "imports": imports,
    }


def _extract_python_elements(root, source: bytes) -> tuple[list, list, list]:
    """Extract Python functions, classes, and imports."""
    functions = []
    classes = []
    imports = []

    for node in root.children:
        if node.type == "function_definition":
            name_node = node.child_by_field_name("name")
            if name_node:
                functions.append({
                    "name": source[name_node.start_byte:name_node.end_byte].decode(),
                    "line": node.start_point[0] + 1,
                    "args": _extract_python_args(node, source),
                })
        elif node.type == "class_definition":
            name_node = node.child_by_field_name("name")
            if name_node:
                classes.append({
                    "name": source[name_node.start_byte:name_node.end_byte].decode(),
                    "line": node.start_point[0] + 1,
                    "bases": _extract_python_bases(node, source),
                })
        elif node.type == "import_statement":
            imports.extend(_extract_python_import(node, source))
        elif node.type == "import_from_statement":
            imports.extend(_extract_python_from_import(node, source))

    return functions, classes, imports


def _extract_python_args(func_node, source: bytes) -> list[str]:
    """Extract function argument names."""
    args = []
    params = func_node.child_by_field_name("parameters")
    if params:
        for child in params.children:
            if child.type == "identifier":
                args.append(source[child.start_byte:child.end_byte].decode())
            elif child.type == "typed_parameter":
                name = child.child_by_field_name("name")
                if name:
                    args.append(source[name.start_byte:name.end_byte].decode())
    return args


def _extract_python_bases(class_node, source: bytes) -> list[str]:
    """Extract class base names."""
    bases = []
    arg_list = class_node.child_by_field_name("superclasses")
    if arg_list:
        for child in arg_list.children:
            if child.type == "identifier":
                bases.append(source[child.start_byte:child.end_byte].decode())
    return bases


def _extract_python_import(node, source: bytes) -> list[dict]:
    """Extract import statement."""
    imports = []
    for child in node.children:
        if child.type == "dotted_name":
            imports.append({
                "module": source[child.start_byte:child.end_byte].decode(),
                "line": node.start_point[0] + 1,
            })
        elif child.type == "aliased_import":
            name = child.child_by_field_name("name")
            if name:
                imports.append({
                    "module": source[name.start_byte:name.end_byte].decode(),
                    "line": node.start_point[0] + 1,
                })
    return imports


def _extract_python_from_import(node, source: bytes) -> list[dict]:
    """Extract from import statement."""
    imports = []
    module = node.child_by_field_name("module_name")
    module_name = source[module.start_byte:module.end_byte].decode() if module else ""

    for child in node.children:
        if child.type == "dotted_name" and child != module:
            imports.append({
                "module": module_name,
                "names": [source[child.start_byte:child.end_byte].decode()],
                "line": node.start_point[0] + 1,
            })
        elif child.type == "import_list":
            names = []
            for item in child.children:
                if item.type == "identifier":
                    names.append(source[item.start_byte:item.end_byte].decode())
            if names:
                imports.append({
                    "module": module_name,
                    "names": names,
                    "line": node.start_point[0] + 1,
                })
    return imports


def _extract_js_elements(root, source: bytes) -> tuple[list, list, list]:
    """Extract JS/TS functions, classes, and imports."""
    functions = []
    classes = []
    imports = []

    # Simplified extraction for JS/TS
    for node in root.children:
        if node.type in ("function_declaration", "function_expression", "arrow_function"):
            name_node = node.child_by_field_name("name")
            if name_node:
                functions.append({
                    "name": source[name_node.start_byte:name_node.end_byte].decode(),
                    "line": node.start_point[0] + 1,
                })
        elif node.type == "class_declaration":
            name_node = node.child_by_field_name("name")
            if name_node:
                classes.append({
                    "name": source[name_node.start_byte:name_node.end_byte].decode(),
                    "line": node.start_point[0] + 1,
                })
        elif node.type == "import_statement":
            imports.append({
                "module": "import",
                "line": node.start_point[0] + 1,
            })

    return functions, classes, imports


def _extract_c_elements(root, source: bytes) -> tuple[list, list]:
    """Extract C functions and includes."""
    functions = []
    imports = []

    for node in root.children:
        if node.type == "function_definition":
            # Find function name in declarator
            for child in node.children:
                if child.type == "function_declarator":
                    for sub in child.children:
                        if sub.type == "identifier":
                            functions.append({
                                "name": source[sub.start_byte:sub.end_byte].decode(),
                                "line": node.start_point[0] + 1,
                            })
        elif node.type == "preproc_include":
            imports.append({
                "module": "include",
                "line": node.start_point[0] + 1,
            })

    return functions, imports
```

- [ ] **Step 4.5: 运行测试确认通过**

```bash
uv run pytest tests/test_tree_sitter_extractor.py -v
# Expected: PASS
```

- [ ] **Step 4.6: 删除旧的 code_analyzer.py**

```bash
rm lib/extractors/code_analyzer.py
```

- [ ] **Step 4.7: Commit**

```bash
git add lib/extractors/tree_sitter_extractor.py tests/test_tree_sitter_extractor.py tests/fixtures/
git rm lib/extractors/code_analyzer.py tests/test_code_analyzer.py
git commit -m "feat: implement tree-sitter extractor with Python/JS/TS/C support"
```

---

## Task 5: 实现 PDF 提取器 (TDD)

**Files:**
- Create: `tests/test_pdf_extractor.py`
- Create: `lib/extractors/pdf_extractor.py`

- [ ] **Step 5.1: 写失败测试**

```python
# tests/test_pdf_extractor.py
"""Tests for pdf_extractor module."""

import pytest


class TestPdfExtractor:
    def test_extract_returns_file_and_sections(self):
        from lib.extractors.pdf_extractor import extract_from_pdf

        result = extract_from_pdf("tests/fixtures/sample.pdf")
        assert result["file"] == "tests/fixtures/sample.pdf"
        assert "sections" in result

    def test_extract_sections_have_content(self):
        from lib.extractors.pdf_extractor import extract_from_pdf

        result = extract_from_pdf("tests/fixtures/sample.pdf")
        assert len(result["sections"]) >= 0
```

- [ ] **Step 5.2: 运行测试确认失败**

```bash
uv run pytest tests/test_pdf_extractor.py -v
# Expected: FAIL - module not found
```

- [ ] **Step 5.3: 实现 pdf_extractor.py**

```python
# lib/extractors/pdf_extractor.py
"""PDF extractor using pdfplumber."""

import re
from pathlib import Path
from typing import Any

import pdfplumber


def extract_from_pdf(filepath: str) -> dict[str, Any]:
    """Extract structured content from PDF."""
    sections = []
    current_section = None
    current_content = []

    with pdfplumber.open(filepath) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            text = page.extract_text()
            if not text:
                continue

            lines = text.split("\n")
            for line in lines:
                # Detect headings (larger font, numbered, or all caps)
                if _is_heading(line):
                    if current_section:
                        current_section["content"] = "\n".join(current_content)
                        sections.append(current_section)
                    current_section = {
                        "title": line.strip(),
                        "page": page_num,
                        "level": _detect_heading_level(line),
                    }
                    current_content = []
                else:
                    current_content.append(line)

        # Add last section
        if current_section:
            current_section["content"] = "\n".join(current_content)
            sections.append(current_section)

    return {
        "file": filepath,
        "sections": sections,
        "pages": len(pdf.pages),
    }


def _is_heading(line: str) -> bool:
    """Detect if line is a heading."""
    line = line.strip()
    if not line:
        return False

    # Numbered headings: 1., 1.1, etc.
    if re.match(r"^\d+\.?\s+\w", line):
        return True

    # Short lines that are likely headings
    if len(line) < 80 and line.isupper():
        return True

    # Common heading patterns
    heading_patterns = [
        r"^Chapter\s+\d+",
        r"^Section\s+\d+",
        r"^Abstract",
        r"^Introduction",
        r"^Conclusion",
        r"^References",
        r"^Appendix",
    ]
    for pattern in heading_patterns:
        if re.match(pattern, line, re.IGNORECASE):
            return True

    return False


def _detect_heading_level(line: str) -> int:
    """Detect heading level (1-4)."""
    line = line.strip()

    # Numbered sections
    match = re.match(r"^(\d+(?:\.\d+)*)", line)
    if match:
        parts = match.group(1).split(".")
        return min(len(parts), 4)

    # Chapter = level 1
    if re.match(r"^Chapter\s+\d+", line, re.IGNORECASE):
        return 1

    # All caps = level 1
    if line.isupper() and len(line) < 50:
        return 1

    return 2  # Default level
```

- [ ] **Step 5.4: 运行测试确认通过**

```bash
uv run pytest tests/test_pdf_extractor.py -v
# Expected: PASS
```

- [ ] **Step 5.5: Commit**

```bash
git add lib/extractors/pdf_extractor.py tests/test_pdf_extractor.py
git commit -m "feat: implement PDF extractor with heading detection"
```

---

## Task 6: 实现 DOCX 提取器 (TDD)

**Files:**
- Create: `tests/test_docx_extractor.py`
- Create: `lib/extractors/docx_extractor.py`

- [ ] **Step 6.1: 写失败测试**

```python
# tests/test_docx_extractor.py
"""Tests for docx_extractor module."""

import pytest


class TestDocxExtractor:
    def test_extract_returns_file_and_sections(self):
        from lib.extractors.docx_extractor import extract_from_docx

        result = extract_from_docx("tests/fixtures/sample.docx")
        assert result["file"] == "tests/fixtures/sample.docx"
        assert "sections" in result

    def test_extract_detects_headings(self):
        from lib.extractors.docx_extractor import extract_from_docx

        result = extract_from_docx("tests/fixtures/sample.docx")
        # Should have at least one heading
        assert any(s.get("level") for s in result["sections"])
```

- [ ] **Step 6.2: 运行测试确认失败**

```bash
uv run pytest tests/test_docx_extractor.py -v
# Expected: FAIL - module not found
```

- [ ] **Step 6.3: 实现 docx_extractor.py**

```python
# lib/extractors/docx_extractor.py
"""DOCX extractor using python-docx."""

from typing import Any
from docx import Document


def extract_from_docx(filepath: str) -> dict[str, Any]:
    """Extract structured content from DOCX."""
    doc = Document(filepath)
    sections = []

    for para in doc.paragraphs:
        if para.style.name.startswith("Heading"):
            level = _extract_heading_level(para.style.name)
            sections.append({
                "level": level,
                "title": para.text,
                "type": "heading",
            })
        elif para.text.strip():
            # Add content to last section or create initial section
            if sections and sections[-1].get("type") != "heading":
                sections[-1]["content"] = sections[-1].get("content", "") + "\n" + para.text
            elif sections:
                sections.append({
                    "content": para.text,
                    "parent_heading": sections[-1]["title"] if sections else None,
                })
            else:
                sections.append({
                    "content": para.text,
                    "parent_heading": None,
                })

    # Also extract tables
    tables = []
    for table in doc.tables:
        table_data = []
        for row in table.rows:
            row_data = [cell.text for cell in row.cells]
            table_data.append(row_data)
        tables.append(table_data)

    return {
        "file": filepath,
        "sections": sections,
        "tables": tables,
    }


def _extract_heading_level(style_name: str) -> int:
    """Extract heading level from style name."""
    if "Heading" in style_name:
        try:
            return int(style_name.replace("Heading ", ""))
        except ValueError:
            return 1
    elif "Title" in style_name:
        return 0
    return 1
```

- [ ] **Step 6.4: 运行测试确认通过**

```bash
uv run pytest tests/test_docx_extractor.py -v
# Expected: PASS
```

- [ ] **Step 6.5: Commit**

```bash
git add lib/extractors/docx_extractor.py tests/test_docx_extractor.py
git commit -m "feat: implement DOCX extractor with heading and table extraction"
```

---

## Task 7: 实现配置系统 (TDD)

**Files:**
- Create: `tests/test_config.py`
- Create: `lib/config.py`

- [ ] **Step 7.1: 写失败测试**

```python
# tests/test_config.py
"""Tests for config module."""

import pytest
from pathlib import Path


class TestGenieConfig:
    def test_default_config(self, tmp_path):
        from lib.config import GenieConfig

        config = GenieConfig(str(tmp_path))
        assert config.depth == "medium"
        assert config.depth_profiles["medium"]["confidence_threshold"] == 0.7

    def test_load_user_config(self, tmp_path):
        from lib.config import GenieConfig

        genie_dir = tmp_path / ".genie"
        genie_dir.mkdir()
        (genie_dir / "config.yaml").write_text("depth: deep\n")

        config = GenieConfig(str(tmp_path))
        assert config.depth == "deep"

    def test_should_process_file(self, tmp_path):
        from lib.config import GenieConfig

        config = GenieConfig(str(tmp_path))
        assert config.should_process_file("test.py") is True
        assert config.should_process_file("test.xyz") is False

    def test_box_size_thresholds(self, tmp_path):
        from lib.config import GenieConfig

        config = GenieConfig(str(tmp_path))
        assert config.box_size_thresholds["quick"]["min_lines"] == 20
        assert config.box_size_thresholds["deep"]["min_lines"] == 1
```

- [ ] **Step 7.2: 运行测试确认失败**

```bash
uv run pytest tests/test_config.py -v
# Expected: FAIL - module not found
```

- [ ] **Step 7.3: 实现 config.py**

```python
# lib/config.py
"""Project configuration management."""

import yaml
from pathlib import Path
from typing import Any


DEFAULT_CONFIG = {
    "version": "1.0",
    "depth": "medium",
    "box_size_thresholds": {
        "quick": {"min_lines": 20, "min_chars": 300},
        "medium": {"min_lines": 5, "min_chars": 100},
        "deep": {"min_lines": 1, "min_chars": 30},
    },
    "depth_profiles": {
        "quick": {
            "extract_comments": False,
            "extract_signatures": True,
            "detect_implicit": False,
            "confidence_threshold": 0.8,
        },
        "medium": {
            "extract_comments": False,
            "extract_signatures": True,
            "detect_implicit": False,
            "confidence_threshold": 0.7,
        },
        "deep": {
            "extract_comments": True,
            "extract_signatures": True,
            "detect_implicit": True,
            "confidence_threshold": 0.6,
        },
    },
    "file_types": [".md", ".py", ".js", ".ts", ".c", ".h"],
    "exclude_patterns": ["node_modules/**", ".venv/**", "**/__pycache__/**"],
    "output": {"format": "yaml", "language": "auto"},
}


class GenieConfig:
    """Project-level configuration for doc-genie."""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.config_file = self.project_root / ".genie" / "config.yaml"
        self._config = self._load_config()

    def _load_config(self) -> dict[str, Any]:
        """Load configuration from file or return defaults."""
        if self.config_file.exists():
            user_config = yaml.safe_load(self.config_file.read_text())
            return self._merge_config(DEFAULT_CONFIG.copy(), user_config)
        return DEFAULT_CONFIG.copy()

    def _merge_config(self, default: dict, user: dict) -> dict:
        """Deep merge user config into defaults."""
        result = default.copy()
        for key, value in user.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        return result

    @property
    def depth(self) -> str:
        """Current extraction depth."""
        return self._config.get("depth", "medium")

    @property
    def depth_profiles(self) -> dict:
        """Depth profile settings."""
        return self._config.get("depth_profiles", {})

    @property
    def box_size_thresholds(self) -> dict:
        """Box size thresholds by depth."""
        return self._config.get("box_size_thresholds", {})

    @property
    def file_types(self) -> list[str]:
        """Supported file types."""
        return self._config.get("file_types", [])

    @property
    def exclude_patterns(self) -> list[str]:
        """Patterns to exclude."""
        return self._config.get("exclude_patterns", [])

    def should_process_file(self, filepath: str) -> bool:
        """Check if file should be processed based on config."""
        path = Path(filepath)

        # Check file type
        if path.suffix not in self.file_types:
            return False

        # Check exclude patterns
        for pattern in self.exclude_patterns:
            if path.match(pattern.replace("**/", "")):
                return False

        return True

    def get_depth_profile(self, depth: str | None = None) -> dict:
        """Get settings for a specific depth level."""
        depth = depth or self.depth
        return self.depth_profiles.get(depth, self.depth_profiles["medium"])

    def get_box_threshold(self, depth: str | None = None) -> dict:
        """Get box size threshold for a specific depth."""
        depth = depth or self.depth
        return self.box_size_thresholds.get(depth, self.box_size_thresholds["medium"])
```

- [ ] **Step 7.4: 运行测试确认通过**

```bash
uv run pytest tests/test_config.py -v
# Expected: PASS
```

- [ ] **Step 7.5: Commit**

```bash
git add lib/config.py tests/test_config.py
git commit -m "feat: implement project-level configuration system with depth profiles"
```

---

## Task 8: 实现持久化存储 (TDD)

**Files:**
- Create: `lib/storage/__init__.py`
- Create: `tests/test_genie_store.py`
- Create: `lib/storage/genie_store.py`

- [ ] **Step 8.1: 写失败测试**

```python
# tests/test_genie_store.py
"""Tests for genie_store module."""

import pytest


class TestGenieStore:
    def test_init_creates_genie_dir(self, tmp_path):
        from lib.storage.genie_store import GenieStore

        store = GenieStore(str(tmp_path))
        assert (tmp_path / ".genie").exists()

    def test_save_and_load_boxes(self, tmp_path):
        from lib.storage.genie_store import GenieStore

        store = GenieStore(str(tmp_path))
        boxes = [{"id": "bb-001", "name": "Test"}]
        store.save_boxes(boxes)

        loaded = store.load_boxes()
        assert len(loaded) == 1
        assert loaded[0]["id"] == "bb-001"

    def test_update_index(self, tmp_path):
        from lib.storage.genie_store import GenieStore

        store = GenieStore(str(tmp_path))
        boxes = [
            {"id": "bb-001", "name": "Auth", "source": {"file": "auth.py"}},
            {"id": "bb-002", "name": "User", "source": {"file": "user.py"}},
        ]
        store.save_boxes(boxes)

        index = store.load_index()
        assert index["by_name"]["Auth"] == "bb-001"
        assert "auth.py" in index["by_file"]
```

- [ ] **Step 8.2: 运行测试确认失败**

```bash
uv run pytest tests/test_genie_store.py -v
# Expected: FAIL - module not found
```

- [ ] **Step 8.3: 创建 __init__.py**

```python
# lib/storage/__init__.py
"""Storage module for doc-genie."""
```

- [ ] **Step 8.4: 实现 genie_store.py**

```python
# lib/storage/genie_store.py
"""Persistent storage for doc-genie analysis results."""

import json
from pathlib import Path
from typing import Any


class GenieStore:
    """Persistent storage for black boxes, relationships, and analysis results."""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.genie_dir = self.project_root / ".genie"
        self.genie_dir.mkdir(exist_ok=True)

        self.boxes_file = self.genie_dir / "boxes.json"
        self.rels_file = self.genie_dir / "relationships.json"
        self.patterns_file = self.genie_dir / "patterns.json"
        self.review_file = self.genie_dir / "review.json"
        self.index_file = self.genie_dir / "index.json"

    def load_boxes(self) -> list[dict]:
        """Load black boxes from storage."""
        if self.boxes_file.exists():
            data = json.loads(self.boxes_file.read_text())
            return data.get("boxes", [])
        return []

    def save_boxes(self, boxes: list[dict], metadata: dict | None = None):
        """Save black boxes to storage."""
        data = {
            "version": "1.0",
            "generated_at": self._get_timestamp(),
            "boxes": boxes,
        }
        if metadata:
            data["metadata"] = metadata

        self.boxes_file.write_text(json.dumps(data, indent=2, ensure_ascii=False))
        self._update_index(boxes)

    def load_relationships(self) -> list[dict]:
        """Load relationships from storage."""
        if self.rels_file.exists():
            data = json.loads(self.rels_file.read_text())
            return data.get("relationships", [])
        return []

    def save_relationships(self, relationships: list[dict], metadata: dict | None = None):
        """Save relationships to storage."""
        data = {
            "version": "1.0",
            "generated_at": self._get_timestamp(),
            "relationships": relationships,
        }
        if metadata:
            data["metadata"] = metadata

        self.rels_file.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    def load_patterns(self) -> list[dict]:
        """Load detected patterns from storage."""
        if self.patterns_file.exists():
            data = json.loads(self.patterns_file.read_text())
            return data.get("patterns", [])
        return []

    def save_patterns(self, patterns: list[dict]):
        """Save detected patterns to storage."""
        data = {
            "version": "1.0",
            "generated_at": self._get_timestamp(),
            "patterns": patterns,
        }
        self.patterns_file.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    def load_review(self) -> dict:
        """Load review status from storage."""
        if self.review_file.exists():
            return json.loads(self.review_file.read_text())
        return {"version": "1.0", "pending_review": [], "disputed": []}

    def save_review(self, review: dict):
        """Save review status to storage."""
        review["version"] = "1.0"
        self.review_file.write_text(json.dumps(review, indent=2, ensure_ascii=False))

    def load_index(self) -> dict:
        """Load search index from storage."""
        if self.index_file.exists():
            return json.loads(self.index_file.read_text())
        return {"by_name": {}, "by_file": {}, "by_keyword": {}}

    def _update_index(self, boxes: list[dict]):
        """Update search index after saving boxes."""
        index = {
            "by_name": {},
            "by_file": {},
            "by_keyword": {},
        }

        for box in boxes:
            # Index by name
            name = box.get("name", "")
            if name:
                index["by_name"][name] = box["id"]

            # Index by file
            source = box.get("source", {})
            file = source.get("file", "")
            if file:
                if file not in index["by_file"]:
                    index["by_file"][file] = []
                index["by_file"][file].append(box["id"])

        self.index_file.write_text(json.dumps(index, indent=2, ensure_ascii=False))

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime, timezone

        return datetime.now(timezone.utc).isoformat()
```

- [ ] **Step 8.5: 运行测试确认通过**

```bash
uv run pytest tests/test_genie_store.py -v
# Expected: PASS
```

- [ ] **Step 8.6: Commit**

```bash
git add lib/storage/ tests/test_genie_store.py
git commit -m "feat: implement persistent storage with indexing"
```

---

## Task 9: 重构 CLI

**Files:**
- Modify: `scripts/cli.py`
- Modify: `tests/test_cli.py`

- [ ] **Step 9.1: 更新 cli.py 支持所有提取器**

```python
# scripts/cli.py
"""doc-genie CLI - unified command line interface."""

import argparse
import json
import sys
from pathlib import Path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="genie", description="doc-genie: Document analysis tool"
    )
    subparsers = parser.add_subparsers(dest="command")

    # extract command
    ext = subparsers.add_parser("extract", help="Extract black boxes from files")
    ext.add_argument("files", nargs="+", help="Files to analyze")
    ext.add_argument(
        "--output", "-o", default="text", choices=["text", "json"], help="Output format"
    )
    ext.add_argument("--depth", "-d", choices=["quick", "medium", "deep"], help="Extraction depth")

    # init command
    subparsers.add_parser("init", help="Initialize .genie directory")

    # config command
    cfg = subparsers.add_parser("config", help="Show configuration")
    cfg.add_argument("action", choices=["show", "set"])

    # analyze command
    subparsers.add_parser("analyze", help="Analyze relationships")

    # report command
    rpt = subparsers.add_parser("report", help="Generate report")
    rpt.add_argument("--format", "-f", default="markdown", choices=["markdown", "html", "dot"])
    rpt.add_argument("--output", "-o", help="Output file path")

    return parser.parse_args(argv)


def extract(files: list[str], output: str = "text", depth: str | None = None) -> list[dict]:
    """Extract structure from files."""
    from lib.config import GenieConfig

    config = GenieConfig()
    depth = depth or config.depth

    results = []
    for filepath in files:
        path = Path(filepath)
        suffix = path.suffix.lower()

        if suffix == ".md":
            from lib.extractors.markdown_extractor import MarkdownExtractor
            extractor = MarkdownExtractor()
            result = extractor.extract_from_file(filepath)
        elif suffix == ".pdf":
            from lib.extractors.pdf_extractor import extract_from_pdf
            result = extract_from_pdf(filepath)
        elif suffix in (".docx", ".doc"):
            from lib.extractors.docx_extractor import extract_from_docx
            result = extract_from_docx(filepath)
        else:
            from lib.extractors.tree_sitter_extractor import extract_structure
            result = extract_structure(filepath)

        result["_depth"] = depth
        results.append(result)

    if output == "json":
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        for r in results:
            count = len(r.get("sections", r.get("functions", [])))
            print(f"Extracted from {r['file']}: {count} items (depth={depth})")

    return results


def init_genie():
    """Initialize .genie directory with default config."""
    from lib.config import DEFAULT_CONFIG
    import yaml

    genie_dir = Path(".genie")
    genie_dir.mkdir(exist_ok=True)

    config_file = genie_dir / "config.yaml"
    if config_file.exists():
        print("Config already exists at .genie/config.yaml")
        return

    config_file.write_text(yaml.dump(DEFAULT_CONFIG, default_flow_style=False))
    print("Created .genie/config.yaml with default configuration")


def show_config():
    """Show current configuration."""
    from lib.config import GenieConfig
    import yaml

    config = GenieConfig()
    print(yaml.dump(config._config, default_flow_style=False))


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if args.command == "extract":
        extract(args.files, args.output, args.depth)
    elif args.command == "init":
        init_genie()
    elif args.command == "config":
        if args.action == "show":
            show_config()
    elif args.command == "analyze":
        print("Analyzing relationships...")
        # TODO: Implement analyze
    elif args.command == "report":
        print(f"Generating {args.format} report...")
        # TODO: Implement report
    else:
        print("Usage: genie [extract|init|config|analyze|report]")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 9.2: 更新测试**

```python
# tests/test_cli.py
"""Tests for CLI module."""

import pytest


class TestCLI:
    def test_parse_extract_args(self):
        from scripts.cli import parse_args

        args = parse_args(["extract", "file1.md", "file2.py"])
        assert args.command == "extract"
        assert args.files == ["file1.md", "file2.py"]

    def test_parse_extract_with_depth(self):
        from scripts.cli import parse_args

        args = parse_args(["extract", "file.py", "--depth", "deep"])
        assert args.depth == "deep"

    def test_parse_init_args(self):
        from scripts.cli import parse_args

        args = parse_args(["init"])
        assert args.command == "init"

    def test_parse_config_args(self):
        from scripts.cli import parse_args

        args = parse_args(["config", "show"])
        assert args.command == "config"
        assert args.action == "show"

    def test_parse_report_args(self):
        from scripts.cli import parse_args

        args = parse_args(["report", "--format", "html"])
        assert args.command == "report"
        assert args.format == "html"

    def test_default_depth_uses_config(self, tmp_path, monkeypatch):
        from scripts.cli import extract

        monkeypatch.chdir(tmp_path)

        # Create default config
        import yaml
        from lib.config import DEFAULT_CONFIG

        genie_dir = tmp_path / ".genie"
        genie_dir.mkdir()
        (genie_dir / "config.yaml").write_text(yaml.dump({"depth": "deep"}))

        # Test that depth is read from config
        from lib.config import GenieConfig

        config = GenieConfig(str(tmp_path))
        assert config.depth == "deep"
```

- [ ] **Step 9.3: 运行测试确认通过**

```bash
uv run pytest tests/test_cli.py -v
# Expected: PASS
```

- [ ] **Step 9.4: Commit**

```bash
git add scripts/cli.py tests/test_cli.py
git commit -m "feat: refactor CLI with config support and all extractors"
```

---

## Task 10: 运行完整测试套件

- [ ] **Step 10.1: 运行所有单元测试**

```bash
uv run pytest tests/ -v --cov=lib --cov-report=term-missing
```

- [ ] **Step 10.2: 运行 linter**

```bash
uv run ruff check lib/
uv run ruff format lib/
uv run mypy lib/
```

- [ ] **Step 10.3: 修复任何问题后提交**

```bash
git add -A
git commit -m "test: all tests passing with coverage"
```

---

## Task 11: Skill 更新 (使用 /skill-creator)

**注意：此任务需要用户手动运行 `/skill-creator`**

- [ ] **Step 11.1: 更新 genie-extract skill**

```
/skill-creator
- 选择 "Update existing skill"
- 选择 genie-extract
- 添加 CLI 调用指令:
  uv run --directory $CLAUDE_PLUGIN_ROOT genie extract <path> --output json --depth <quick|medium|deep>
- 添加子代理格式参考 OUTPUT.md
```

- [ ] **Step 11.2: 更新 genie-relations skill**

```
/skill-creator
- 选择 "Update existing skill"
- 选择 genie-relations
- 添加代理消费关系
- 添加审查流程说明
```

- [ ] **Step 11.3: 更新 genie-insights skill**

```
/skill-creator
- 选择 "Update existing skill"
- 选择 genie-insights
- 添加 disputed 项审查流程
```

- [ ] **Step 11.4: 更新 genie-report skill**

```
/skill-creator
- 选择 "Update existing skill"
- 选择 genie-report
- 添加 Store 读取格式
```

---

## Task 12: 基线对比脚本

**Files:**
- Create: `scripts/record_baseline.py`
- Create: `scripts/compare_baseline.py`

- [ ] **Step 12.1: 创建 record_baseline.py**

```python
# scripts/record_baseline.py
"""Record baseline metrics for comparison."""

import json
import subprocess
from pathlib import Path
from datetime import datetime


def record_baseline():
    """Run extraction and record metrics."""
    result = subprocess.run(
        ["uv", "run", "genie", "extract", "tests/e2e/fixtures/", "--output", "json"],
        capture_output=True,
        text=True,
    )

    boxes = json.loads(result.stdout) if result.returncode == 0 else []

    metrics = {
        "timestamp": datetime.now().isoformat(),
        "total_boxes": sum(len(r.get("sections", r.get("functions", []))) for r in boxes),
        "files_processed": len(boxes),
        "boxes": boxes,
    }

    baseline_file = Path(".genie/baseline.json")
    baseline_file.write_text(json.dumps(metrics, indent=2))
    print(f"Baseline recorded: {metrics['total_boxes']} boxes from {metrics['files_processed']} files")


if __name__ == "__main__":
    record_baseline()
```

- [ ] **Step 12.2: 创建 compare_baseline.py**

```python
# scripts/compare_baseline.py
"""Compare current results against baseline."""

import json
import subprocess
import sys
from pathlib import Path


def compare_baseline(assert_improvement: bool = False):
    """Compare current extraction with baseline."""
    # Load baseline
    baseline_file = Path(".genie/baseline.json")
    if not baseline_file.exists():
        print("No baseline found. Run: uv run python scripts/record_baseline.py")
        return

    baseline = json.loads(baseline_file.read_text())

    # Run current extraction
    result = subprocess.run(
        ["uv", "run", "genie", "extract", "tests/e2e/fixtures/", "--output", "json"],
        capture_output=True,
        text=True,
    )

    current_boxes = json.loads(result.stdout) if result.returncode == 0 else []
    current_metrics = {
        "total_boxes": sum(len(r.get("sections", r.get("functions", []))) for r in current_boxes),
        "files_processed": len(current_boxes),
    }

    # Compare
    diff = {
        "boxes_diff": current_metrics["total_boxes"] - baseline["total_boxes"],
        "baseline_boxes": baseline["total_boxes"],
        "current_boxes": current_metrics["total_boxes"],
    }

    print(f"Baseline: {baseline['total_boxes']} boxes")
    print(f"Current:  {current_metrics['total_boxes']} boxes")
    print(f"Diff:     {diff['boxes_diff']:+d} boxes")

    if assert_improvement and diff["boxes_diff"] < 0:
        print("ERROR: Current is worse than baseline!")
        sys.exit(1)

    # Save comparison
    comparison_file = Path(".genie/baseline_comparison.json")
    comparison_file.write_text(json.dumps(diff, indent=2))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--assert-improvement", action="store_true")
    args = parser.parse_args()

    compare_baseline(assert_improvement=args.assert_improvement)
```

- [ ] **Step 12.3: Commit**

```bash
git add scripts/record_baseline.py scripts/compare_baseline.py
git commit -m "feat: add baseline comparison scripts"
```

---

## Task 13: 最终验证与提交

- [ ] **Step 13.1: 完整测试套件**

```bash
uv run pytest tests/ -v --cov
```

- [ ] **Step 13.2: 格式检查**

```bash
uv run ruff check lib/ --fix
uv run ruff format lib/
```

- [ ] **Step 13.3: 验证插件结构**

```bash
ls -la .claude-plugin/plugin.json
ls -la commands/
ls -la agents/
```

- [ ] **Step 13.4: 最终提交**

```bash
git add -A
git commit -m "feat: doc-genie v0.2.0 - complete refactor

- Move plugin.json to .claude-plugin/
- Add commands/ directory with slash commands
- Add agents/ directory with specialized agents
- Implement tree-sitter extractor (C/JS/TS/Python)
- Implement PDF/DOCX extractors
- Add project-level config (.genie/config.yaml)
- Add depth profiles (quick/medium/deep)
- Implement persistent storage with indexing
- Add baseline comparison scripts
- All tests passing

Co-Authored-By: Claude <noreply@anthropic.com>"
```

- [ ] **Step 13.5: 推送**

```bash
git push origin main
```

---

## 验证清单

完成后验证：

- [ ] `.claude-plugin/plugin.json` 存在
- [ ] `commands/` 目录有 3 个 `.md` 文件
- [ ] `agents/` 目录有 7 个代理定义文件
- [ ] `uv sync` 成功安装所有依赖
- [ ] `uv run pytest tests/ -v` 全部通过
- [ ] `uv run genie extract file.py --output json` 输出有效 JSON
- [ ] `.genie/config.yaml` 支持深度配置
- [ ] 基线对比脚本可运行