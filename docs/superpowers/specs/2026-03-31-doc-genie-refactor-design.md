# doc-genie 架构重构设计

> 日期: 2026-03-31
> 状态: 待批准
> 目标: 解决设计差距 + 标准 Claude Code 插件结构 + tree-sitter 统一解析

---

## 1. 问题总结

### 当前差距

| 缺失项 | 影响 | 优先级 |
|--------|------|--------|
| 插件 manifest 位置错误 | Claude Code 无法识别插件 | P0 |
| PDF/DOCX 提取器缺失 | Layer 1 不完整 | P1 |
| tree-sitter 统一解析 | 当前自定义 AST，不支持多语言 | P1 |
| Skill-lib 交互机制 | AI 不知道如何调用 Python 工具 | P1 |
| 持久化缺失 | 无法保存/复用分析结果 | P2 |
| 调用图分析缺失 | Layer 2 不完整 | P2 |

---

## 2. 插件结构重构

### 目标结构（Claude Code 标准）

```
doc-genie/
├── .claude-plugin/
│   └── plugin.json              # ✅ 标准位置
│
├── commands/                     # Slash 命令
│   ├── genie-extract.md          # /genie-extract
│   ├── genie-analyze.md          # /genie-analyze
│   └── genie-report.md           # /genie-report
│
├── agents/                       # 可选：自动化代理
│   └── doc-analyzer.md           # 全文档分析流程
│
├── skills/                       # 自动激活技能（保留现有）
│   ├── genie-extract/SKILL.md
│   ├── genie-relations/SKILL.md
│   ├── genie-insights/SKILL.md
│   └── genie-report/SKILL.md
│
├── lib/                          # Python 核心库
│   ├── __init__.py
│   ├── blackbox_model.py         # 数据模型
│   ├── relationship_types.py     # 关系类型
│   ├── extractors/
│   │   ├── tree_sitter_extractor.py  # 🆕 tree-sitter 统一解析
│   │   ├── markdown_extractor.py     # 保留
│   │   ├── pdf_extractor.py          # 🆕 PDF 提取
│   │   └── docx_extractor.py         # 🆕 DOCX 提取
│   ├── patterns/
│   │   └── relationship_patterns.py  # 保留
│   ├── storage/                  # 🆕 持久化
│   │   └── genie_store.py
│   └── call_graph/               # 🆕 调用图分析
│       └── pyan_analyzer.py
│
├── scripts/
│   └── cli.py                    # CLI 入口（重构）
│
├── .mcp.json                     # 可选：MCP server 定义
│
├── tests/
│
├── pyproject.toml                # Python 依赖管理
│
└── AGENTS.md                     # 跨平台兼容（保留）
```

### plugin.json 内容

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

---

## 3. tree-sitter 统一解析方案

### 安装策略（uv 全流程）

**pyproject.toml 依赖：**

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

# 用户可按需安装更多语言
[project.optional-dependencies]
languages = [
    "tree-sitter-go>=0.23.0",
    "tree-sitter-java>=0.23.0",
    "tree-sitter-rust>=0.23.0",
]
```

**uv 安装命令：**

```bash
# 项目初始化
uv init

# 添加核心依赖（默认支持 C/JS/TS/Python）
uv add tree-sitter tree-sitter-python tree-sitter-javascript tree-sitter-typescript tree-sitter-c
uv add pdfplumber python-docx markdown-it-py networkx pyyaml rich

# 扩展语言支持（可选：Go/Java/Rust）
uv add --optional languages tree-sitter-go tree-sitter-java tree-sitter-rust

# 同步安装
uv sync

# 运行 CLI
uv run genie extract file.py --output json
```

### tree_sitter_extractor.py 设计

```python
"""
tree-sitter 统一解析器
默认支持: C, JavaScript, TypeScript, Python
扩展支持: Go, Java, Rust (需额外安装)
"""

import tree_sitter_python as tspython
import tree_sitter_javascript as tsjs
import tree_sitter_typescript as tsts
import tree_sitter_c as tsc
from tree_sitter import Language, Parser
from pathlib import Path
from typing import Any

# 语言映射
LANGUAGE_MODULES = {
    ".py": (tspython, "python"),
    ".js": (tsjs, "javascript"),
    ".jsx": (tsjs, "javascript"),
    ".ts": (tsts, "typescript"),
    ".tsx": (tsts, "typescript"),
    ".c": (tsc, "c"),
    ".h": (tsc, "c"),
    # 扩展语言（可选）
    ".go": None,      # tree-sitter-go
    ".java": None,    # tree-sitter-java
    ".rs": None,      # tree-sitter-rust
}

def get_parser(suffix: str) -> Parser | None:
    """获取对应语言的 Parser"""
    lang_info = LANGUAGE_MODULES.get(suffix)
    if lang_info is None:
        # 尝试加载可选语言
        try:
            if suffix == ".go":
                import tree_sitter_go as tsgo
                return Parser(Language(tsgo.language()))
            # ... 其他可选语言
        except ImportError:
            return None
    if lang_info:
        module, _ = lang_info
        return Parser(Language(module.language()))
    return None

def extract_structure(filepath: str) -> dict[str, Any]:
    """提取代码结构: functions, classes, imports"""
    path = Path(filepath)
    parser = get_parser(path.suffix)

    if parser is None:
        return {"error": f"Unsupported language: {path.suffix}"}

    source = path.read_bytes()
    tree = parser.parse(source)

    # Query 提取（根据语言不同）
    functions = []
    classes = []
    imports = []

    # ... tree-sitter query 逻辑

    return {
        "file": filepath,
        "language": LANGUAGE_MODULES.get(path.suffix, (None, "unknown"))[1],
        "functions": functions,
        "classes": classes,
        "imports": imports,
    }
```

### 删除旧文件

- `lib/extractors/code_analyzer.py` → 替换为 `tree_sitter_extractor.py`

---

## 4. Skill-lib 交互机制

### 方案：Bash 调用 + JSON 输出

**SKILL.md 指令模式：**

```markdown
## 使用方法

1. **快速解析**（CLI 工具）：
   ```bash
   uv run --directory $CLAUDE_PLUGIN_ROOT genie extract file.py --output json
   ```

2. **AI 语义分析**：
   - 读取 CLI 输出的 JSON
   - 根据 OUTPUT.md 模板提取黑盒
   - 补充隐式关系、冲突检测

## 输出格式

CLI 输出 JSON，Skill 解析：
```

**CLI JSON 输出格式：**

```json
{
  "file": "auth.py",
  "language": "python",
  "functions": [
    {"name": "login", "line": 10, "args": ["username", "password"]}
  ],
  "classes": [
    {"name": "AuthService", "line": 5, "bases": ["BaseService"]}
  ],
  "imports": [
    {"module": "flask", "line": 1}
  ]
}
```

### commands/genie-extract.md 设计

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

---

## 5. 持久化方案

### 5.1 项目级配置

**配置文件：`.genie/config.yaml`**

```yaml
# .genie/config.yaml - 项目级黑盒提取配置
# 此配置应用于项目中所有文档和代码

version: "1.0"

# 🎯 核心配置：提取深度（抽象级别）
# depth 控制黑盒的最小粒度 - 即"一个盒子有多小"
# quick   - 粗粒度：大盒子（模块/章节级）
# medium  - 中粒度：中等盒子（函数/段落级）
# deep    - 细粒度：小盒子（语句/表达式级）
depth: "medium"

# 深度 = 抽象级别的反向
# ┌─────────────────────────────────────────────────────────────────┐
# │ Depth │ 抽象级别   │ 黑盒最小粒度      │ 典型盒子大小        │
# ├─────────────────────────────────────────────────────────────────┤
# │ quick │ 高抽象     │ 模块/章节         │ ~500 行/字          │
# │       │            │ - 一个文件一个盒  │ - 一个章节一个盒    │
# │       │            │ - 一个类一个盒    │ - 概括性描述        │
# ├─────────────────────────────────────────────────────────────────┤
# │ medium│ 中抽象     │ 函数/段落         │ ~50-100 行/字       │
# │       │            │ - 每个函数一个盒  │ - 每个段落一个盒    │
# │       │            │ - 包含签名+IO     │ - 包含核心论点      │
# ├─────────────────────────────────────────────────────────────────┤
# │ deep  │ 低抽象     │ 语句/表达式       │ ~10-30 行/字        │
# │       │            │ - 关键语句独立    │ - 关键句子独立      │
# │       │            │ - 调用链追踪      │ - 具体细节提取      │
# └─────────────────────────────────────────────────────────────────┘

# 盒子最小尺寸阈值（小于此值不独立成盒，合并到父盒）
box_size_thresholds:
  quick:
    min_lines: 20       # 代码最小行数
    min_chars: 300      # 文档最小字符数
  medium:
    min_lines: 5
    min_chars: 100
  deep:
    min_lines: 1        # 单行也可独立
    min_chars: 30

# 各深度的默认行为
depth_profiles:
  quick:
    # 高抽象：只看结构骨架
    extract_comments: false
    extract_signatures: true   # 仅顶层签名
    detect_implicit: false
    confidence_threshold: 0.8

  medium:
    # 中抽象：结构 + 核心内容
    extract_comments: false
    extract_signatures: true
    detect_implicit: false
    confidence_threshold: 0.7

  deep:
    # 低抽象：完整细节
    extract_comments: true
    extract_signatures: true
    detect_implicit: true
    confidence_threshold: 0.6

# 文件类型覆盖
file_types:
  - ".md"
  - ".py"
  - ".js"
  - ".ts"
  - ".c"
  - ".h"

# 排除模式
exclude_patterns:
  - "node_modules/**"
  - ".venv/**"
  - "**/__pycache__/**"
  - "**/test_*.py"

# 输出配置
output:
  format: "yaml"  # yaml | json
  language: "auto"  # auto | en | zh
```

### 5.2 配置加载逻辑

**lib/config.py**:

```python
"""项目配置管理"""

import yaml
from pathlib import Path
from typing import Any

DEFAULT_CONFIG = {
    "version": "1.0",
    "extraction": {
        "depth": "standard",
        "min_section_length": 100,
        "include_comments": True,
        "include_signatures": True,
        "file_types": [".md", ".py", ".js", ".ts", ".go", ".java"],
        "exclude_patterns": ["node_modules/**", ".venv/**"],
    },
    "relationships": {
        "confidence_threshold": 0.7,
        "enabled_types": ["data_flow", "dependency", "interface"],
        "detect_implicit": True,
    },
    "output": {
        "format": "yaml",
        "include_source_snippets": False,
        "language": "auto",
    },
}

class GenieConfig:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.config_file = self.project_root / ".genie" / "config.yaml"
        self._config = self._load_config()

    def _load_config(self) -> dict[str, Any]:
        if self.config_file.exists():
            user_config = yaml.safe_load(self.config_file.read_text())
            return self._merge_config(DEFAULT_CONFIG, user_config)
        return DEFAULT_CONFIG.copy()

    def _merge_config(self, default: dict, user: dict) -> dict:
        """深度合并配置"""
        result = default.copy()
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        return result

    @property
    def extraction(self) -> dict:
        return self._config["extraction"]

    @property
    def relationships(self) -> dict:
        return self._config["relationships"]

    def should_process_file(self, filepath: str) -> bool:
        """检查文件是否应该被处理"""
        path = Path(filepath)
        # 检查文件类型
        if path.suffix not in self.extraction["file_types"]:
            return False
        # 检查排除模式
        for pattern in self.extraction["exclude_patterns"]:
            if path.match(pattern):
                return False
        return True
```

### 5.3 CLI 支持配置

```bash
# 初始化项目配置
genie init

# 使用配置提取
genie extract ./src

# 覆盖配置
genie extract ./src --depth deep --format json

# 显示当前配置
genie config show
```

### 5.4 .genie/ 目录结构（更新）

```
.genie/
├── config.yaml              # 🆕 项目级配置
├── boxes.json               # 黑盒定义
├── relationships.json       # 关系列表
├── patterns.json            # 🆕 模式检测结果
├── review.json              # 🆕 审查状态
└── index.json               # 快速查找索引
```

### 5.5 genie_store.py 设计（更新）

```python
"""持久化存储"""

import json
from pathlib import Path
from typing import Any

class GenieStore:
    def __init__(self, project_root: str = "."):
        self.genie_dir = Path(project_root) / ".genie"
        self.genie_dir.mkdir(exist_ok=True)

        self.boxes_file = self.genie_dir / "boxes.json"
        self.rels_file = self.genie_dir / "relationships.json"
        self.index_file = self.genie_dir / "index.json"

    def load_boxes(self) -> list[dict]:
        if self.boxes_file.exists():
            return json.loads(self.boxes_file.read_text())
        return []

    def save_boxes(self, boxes: list[dict]):
        self.boxes_file.write_text(json.dumps(boxes, indent=2))
        self._update_index(boxes)

    def _update_index(self, boxes: list[dict]):
        """更新索引: by_name, by_file"""
        index = {
            "by_name": {b["name"]: b["id"] for b in boxes},
            "by_file": {},
        }
        for b in boxes:
            file = b["source"]["file"]
            if file not in index["by_file"]:
                index["by_file"][file] = []
            index["by_file"][file].append(b["id"])

        self.index_file.write_text(json.dumps(index, indent=2))
```

---

## 6. PDF/DOCX 提取器

### pdf_extractor.py

```python
"""PDF 提取器"""

import pdfplumber

def extract_from_pdf(filepath: str) -> dict:
    """提取 PDF 结构化内容"""
    sections = []

    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            # 按标题/段落分块
            # ...

    return {"file": filepath, "sections": sections}
```

### docx_extractor.py

```python
"""DOCX 提取器"""

from docx import Document

def extract_from_docx(filepath: str) -> dict:
    """提取 DOCX 结构化内容"""
    doc = Document(filepath)
    sections = []

    for para in doc.paragraphs:
        if para.style.name.startswith('Heading'):
            # 标题段落
            sections.append({
                "level": int(para.style.name.replace('Heading ', '')),
                "title": para.text,
            })

    return {"file": filepath, "sections": sections}
```

---

## 7. CLI 重构

### scripts/cli.py

```python
"""doc-genie CLI"""

import argparse
import json
import sys
from pathlib import Path

def extract(files: list[str], output: str = "text"):
    """提取文件结构"""
    results = []

    for filepath in files:
        path = Path(filepath)
        suffix = path.suffix

        if suffix == ".md":
            from lib.extractors.markdown_extractor import MarkdownExtractor
            extractor = MarkdownExtractor()
        elif suffix == ".pdf":
            from lib.extractors.pdf_extractor import extract_from_pdf
            result = extract_from_pdf(filepath)
            results.append(result)
            continue
        elif suffix in [".docx", ".doc"]:
            from lib.extractors.docx_extractor import extract_from_docx
            result = extract_from_docx(filepath)
            results.append(result)
            continue
        else:
            from lib.extractors.tree_sitter_extractor import extract_structure
            result = extract_structure(filepath)
            results.append(result)
            continue

        result = extractor.extract_from_file(filepath)
        results.append(result)

    if output == "json":
        print(json.dumps(results, indent=2))
    else:
        for r in results:
            print(f"Extracted from {r['file']}: {len(r.get('sections', r.get('functions', [])))} items")

    return results

def main():
    parser = argparse.ArgumentParser(prog="genie")
    subparsers = parser.add_subparsers(dest="command")

    # extract
    ext = subparsers.add_parser("extract")
    ext.add_argument("files", nargs="+")
    ext.add_argument("--output", default="text", choices=["text", "json"])

    # analyze
    subparsers.add_parser("analyze")

    # report
    rpt = subparsers.add_parser("report")
    rpt.add_argument("--format", default="markdown")

    args = parser.parse_args()

    if args.command == "extract":
        extract(args.files, args.output)
    elif args.command == "analyze":
        print("Analyzing...")
    elif args.command == "report":
        print(f"Generating {args.format} report...")

if __name__ == "__main__":
    main()
```

---

## 8. 子代理架构

### 8.1 设计目标

- **并行处理**: 大规模文档时，多个子代理并行处理不同文件/黑盒
- **专业分工**: 不同关系类型由专门子代理处理
- **多 Skill 消费**: 结果标准化，多个 Skill 可复用

### 8.2 架构图

```
用户请求: 分析 50 个文件
           │
           ▼
    ┌──────────────┐
    │ Orchestrator │  主 Skill 协调器
    └──────┬───────┘
           │
    ┌──────┴──────┐
    │             │
    ▼             ▼
┌─────────┐   ┌─────────┐
│ Chunker │   │ Router  │  分块 + 路由
└────┬────┘   └────┬────┘
     │             │
     │    ┌────────┼────────┬────────┐
     │    ▼        ▼        ▼        ▼
     │ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐
     │ │Data  │ │Dep   │ │Confl │ │Pattern│
     │ │Flow  │ │Expert│ │Detect│ │Finder │
     │ │Agent │ │Agent │ │Agent │ │Agent  │
     │ └──────┘ └──────┘ └──────┘ └──────┘
     │    │        │        │        │
     └────┴────────┴────────┴────────┘
                    │
                    ▼
              ┌──────────┐
              │ Reviewer │  结果审查
              └────┬─────┘
                   │
                   ▼
              ┌──────────┐
              │  Store   │  持久化（多 Skill 共享）
              └──────────┘
                   │
         ┌─────────┼─────────┐
         ▼         ▼         ▼
    ┌─────────┐ ┌─────────┐ ┌─────────┐
    │genie-   │ │genie-   │ │genie-   │
    │relations│ │insights │ │report   │
    └─────────┘ └─────────┘ └─────────┘
```

### 8.3 代理定义

#### agents/ 目录结构

```
agents/
├── chunk-coordinator.md      # 分块协调器
├── extract-worker.md         # 提取工作器
├── data-flow-agent.md        # 数据流分析专家
├── dependency-agent.md       # 依赖分析专家
├── conflict-agent.md         # 冲突检测专家
├── pattern-agent.md          # 模式识别专家
└── result-reviewer.md        # 结果审查器
```

#### 分块代理

**agents/chunk-coordinator.md**:
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

**agents/extract-worker.md**:
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

#### 专业代理

**agents/data-flow-agent.md**:
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

**agents/dependency-agent.md**:
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

**agents/conflict-agent.md**:
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

**agents/pattern-agent.md**:
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

### 8.4 结果审查机制

**agents/result-reviewer.md**:
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

```
Agent Results → Format Check → Dedupe → Confidence Filter → Cross-Validate → AI Review → Store
```

## Review Checks

| Check | Method | Action |
|-------|--------|--------|
| Format | JSON Schema | Reject invalid |
| Duplicate | ID matching | Merge duplicates |
| Confidence | Threshold < 0.7 | Mark `needs_review` |
| Cross-validate | Multi-agent vote | Confirm if 2+ agree |
| Semantic | AI review | Flag suspicious |

## Output Format

```yaml
relationships:
  - source: "bb-001"
    target: "bb-002"
    type: "dependency"
    confidence: 0.95
    evidence: "Auth queries user database"
    detected_by: ["dependency-agent", "data-flow-agent"]
    review_status: "confirmed"  # confirmed | needs_review | disputed
```
```

---

## 9. 多 Skill 消费机制

### 9.1 标准化输出格式

所有代理结果存储到 `.genie/` 后，多个 Skill 可共享：

```json
// .genie/boxes.json
{
  "version": "1.0",
  "generated_at": "2026-03-31T10:00:00Z",
  "boxes": [...]
}

// .genie/relationships.json
{
  "version": "1.0",
  "generated_at": "2026-03-31T10:05:00Z",
  "relationships": [
    {
      "source": "bb-001",
      "target": "bb-002",
      "type": "dependency",
      "confidence": 0.95,
      "evidence": "...",
      "detected_by": ["dependency-agent"],
      "review_status": "confirmed"
    }
  ]
}

// .genie/review.json
{
  "version": "1.0",
  "pending_review": [
    {"id": "rel-005", "reason": "low_confidence", "confidence": 0.65}
  ],
  "disputed": [
    {"id": "rel-008", "conflict": "agent_disagreement"}
  ]
}
```

### 9.2 Skill 消费流程

```
┌─────────────────────────────────────────────────────────────┐
│                    Skill 消费流程                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  genie-relations Skill                                      │
│       │                                                     │
│       ▼                                                     │
│  ┌─────────────┐                                            │
│  │ Read Store  │  Load boxes.json + relationships.json     │
│  └──────┬──────┘                                            │
│         │                                                   │
│         ▼                                                   │
│  ┌─────────────┐                                            │
│  │ Filter      │  Only high-confidence, confirmed relations │
│  └──────┬──────┘                                            │
│         │                                                   │
│         ▼                                                   │
│  ┌─────────────┐                                            │
│  │ Analyze     │  Build relationship graph, find patterns   │
│  └──────┬──────┘                                            │
│         │                                                   │
│         ▼                                                   │
│  Output: Relationship report                                │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  genie-insights Skill                                       │
│       │                                                     │
│       ▼                                                     │
│  ┌─────────────┐                                            │
│  │ Read Store  │  Load all .genie/*.json                    │
│  └──────┬──────┘                                            │
│         │                                                   │
│         ▼                                                   │
│  ┌─────────────┐                                            │
│  │ Focus       │  Include needs_review + disputed items     │
│  └──────┬──────┘                                            │
│         │                                                   │
│         ▼                                                   │
│  ┌─────────────┐                                            │
│  │ Deep Analyze│  AI semantic analysis on uncertain items   │
│  └──────┬──────┘                                            │
│         │                                                   │
│         ▼                                                   │
│  Output: Insights + resolved disputes                       │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  genie-report Skill                                         │
│       │                                                     │
│       ▼                                                     │
│  ┌─────────────┐                                            │
│  │ Read Store  │  Load finalized data                       │
│  └──────┬──────┘                                            │
│         │                                                   │
│         ▼                                                   │
│  ┌─────────────┐                                            │
│  │ Aggregate   │  Statistics, counts, summaries             │
│  └──────┬──────┘                                            │
│         │                                                   │
│         ▼                                                   │
│  Output: Markdown report with Mermaid diagrams              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 9.3 代理与 Skill 消费关系

```
┌─────────────────────────────────────────────────────────────────────┐
│                    代理 → Skill 消费映射                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  genie-extract Skill                                                │
│       │                                                             │
│       ├──► chunk-coordinator    (分发任务)                          │
│       ├──► extract-worker       (提取黑盒)                          │
│       └──► result-reviewer      (审查提取结果)                      │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  genie-relations Skill                                              │
│       │                                                             │
│       ├──► data-flow-agent      (数据流分析)                        │
│       ├──► dependency-agent     (依赖分析)                          │
│       └──► result-reviewer      (审查关系结果)                      │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  genie-insights Skill                                               │
│       │                                                             │
│       ├──► conflict-agent        (冲突检测)                         │
│       ├──► pattern-agent         (模式识别)                         │
│       ├──► result-reviewer       (深度审查 disputed 项)             │
│       └──► 读取 needs_review 项进行 AI 语义分析                     │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  genie-report Skill                                                 │
│       │                                                             │
│       └──► 读取 Store 中所有 finalized 数据生成报告                 │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 9.4 代理注册表

| 代理 | 消费 Skill | 输出类型 | 存储位置 |
|------|------------|----------|----------|
| chunk-coordinator | genie-extract | Task assignments | 内存 |
| extract-worker | genie-extract | Black boxes | .genie/boxes.json |
| data-flow-agent | genie-relations | Relationships | .genie/relationships.json |
| dependency-agent | genie-relations | Relationships | .genie/relationships.json |
| conflict-agent | genie-insights | Conflicts | .genie/review.json |
| pattern-agent | genie-insights | Patterns | .genie/patterns.json |
| result-reviewer | 所有 Skill | Review status | .genie/review.json |

### 9.5 审查状态流转

---

## 10. 可借鉴的工具与模式

### 10.1 Tree-sitter 生态工具

| 工具 | 特点 | 可借鉴 |
|------|------|--------|
| [tree-sitter-analyzer](https://pypi.org/project/tree-sitter-analyzer/) | MCP server + 统一元素管理 | MCP 协议集成、filter 语法 |
| [ast-grep](https://ast-grep.github.io/) | 结构化搜索/替换、YAML 规则 | Pattern matching 语法 |
| [CodeGraph CLI](https://www.reddit.com/r/LocalLLaMA/comments/1r645hx/) | tree-sitter + RAG + 多代理 | 语义图构建 |

**tree-sitter-analyzer 关键模式：**
```python
# 统一元素类型
elements = [
    {"type": "class", "name": "AuthService", "element_type": "class"},
    {"type": "method", "name": "login", "element_type": "method"},
]

# 声明式过滤
--filter "name=login" --filter "modifiers=public"
```

### 10.2 多代理编排模式

| 来源 | 模式 | 应用 |
|------|------|------|
| [Anthropic Multi-Agent](https://www.anthropic.com/engineering/multi-agent-research-system) | Orchestrator-Worker | 领导代理分解任务，工作代理并行执行 |
| [Azure AI Patterns](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns) | Chaining/Routing/Parallelization | 任务链、路由分发、并行处理 |
| [Production Patterns](https://levelup.gitconnected.com/your-multi-agent-system-works-in-a-demo-production-is-a-different-story-2f8ff6350664) | Evaluator-Optimizer | 评估器-优化器循环 |

**Anthropic 编排关键模式：**
```
Orchestrator (Lead Agent)
    │
    ├── 分解任务
    ├── 生成子任务指令 (objective + output_format + tools + boundaries)
    │
    └── 并行启动 3-5 个 Subagent
            │
            ├── Subagent 1: 独立搜索评估
            ├── Subagent 2: 独立搜索评估
            └── Subagent 3: 独立搜索评估
                    │
                    ▼
            返回结构化结果 → Orchestrator 合成
```

### 10.3 代理评估与审查模式

| 来源 | 模式 | 应用 |
|------|------|------|
| [Anthropic Evals](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) | Grader 组合 | 代码检测 + 模型评分 + 人工审查 |
| [AWS Agent Eval](https://aws.amazon.com/blogs/machine-learning/evaluating-ai-agents-real-world-lessons-from-building-agentic-systems-at-amazon/) | Intent Correctness | 意图正确性 + 任务完成度 |
| [LangSmith/Langfuse](https://medium.com/@avigoldfinger/multi-agent-system-evaluation-for-dummies-langsmith-langfuse-and-friends-3a78e3c18128) | QA Pipeline | 专家答案 + 次级专家审查 |

**关键评估模式：**
```python
# pass@k vs pass^k
pass@k  # 一次成功即可（工具调用）
pass^k  # 每次都需成功（代理行为）

# 评估器组合
graders = [
    CodeGrader(),      # 字符串匹配、静态分析
    ModelGrader(),     # 模型评分
    HumanGrader(),     # 人工抽查
]
```

### 10.4 依赖与关系分析工具

| 工具 | 特点 | 可借鉴 |
|------|------|--------|
| [Depends](https://github.com/multilang-depends/depends) | 多语言依赖提取 | 语法关系推断 |
| [pyan3](https://github.com/Technologicat/pyan) | Python 静态调用图 | 函数/类关系图 |
| [Sourcegraph](https://sourcegraph.com/) | 跨仓库代码导航 | Cross-reference 引用 |

### 10.5 文档-代码追溯工具

| 工具 | 特点 | 可借鉴 |
|------|------|--------|
| [SpecMap](https://arxiv.org/abs/2601.11688) | 层次化 LLM 追溯 | 仓库级→文件级→符号级 |
| [FTLR](https://github.com/tobhey/finegrained-traceability) | 细粒度追溯 | 制品到元素映射 |

**SpecMap 层次化追溯：**
```
Datasheet → Repository Structure → File Relevance → Symbol Alignment
```

### 10.6 知识图谱构建模式

| 来源 | 模式 | 应用 |
|------|------|------|
| [Claude KG Guide](https://platform.claude.com/cookbook/capabilities-knowledge-graph-guide) | Pydantic 结构化提取 | 实体/关系 Schema |
| [Neo4j KG](https://neo4j.com/blog/developer/knowledge-graph-extraction-challenges/) | 文档分块+关系提取 | Chunk→Entity→Relation |

**知识图谱提取模式：**
```python
class Entity(BaseModel):
    name: str
    type: EntityType  # 组件、服务、数据流
    description: str

class Relation(BaseModel):
    source: str
    predicate: str  # "depends_on", "produces", "consumes"
    target: str

class ExtractedGraph(BaseModel):
    entities: list[Entity]
    relations: list[Relation]
```

---

## 11. 实施步骤

### 11.0 先决条件检查

**必需环境：Python 3.10+ 和 uv**

```bash
# Step 0.1: 检查 Python 版本
python3 --version
# 期望输出: Python 3.10.x 或更高

# 如果未安装，根据系统安装：
# macOS:
brew install python@3.10

# Ubuntu/Debian:
sudo apt install python3.10 python3.10-venv

# Windows:
winget install Python.Python.3.10
```

```bash
# Step 0.2: 检查 uv 是否安装
uv --version
# 期望输出: uv 0.x.x

# 如果未安装：
# macOS/Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows:
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# 或使用 pip:
pip install uv
```

```bash
# Step 0.3: 验证环境
uv python list  # 列出可用 Python 版本
uv venv --python 3.10  # 创建虚拟环境
```

### 11.1 开发阶段

| 步骤 | 任务 | 命令/工具 | 依赖 |
|------|------|----------|------|
| 1 | 创建 `.claude-plugin/plugin.json` | 手动 | 先决条件 ✅ |
| 2 | 创建 `commands/*.md` | 手动 | 步骤 1 |
| 3 | 创建 `agents/*.md` | 手动 | 步骤 1 |
| 4 | 删除旧 `plugin.json` | `rm plugin.json` | 步骤 1 |
| 5 | 更新 `pyproject.toml` | `uv add ...` | 先决条件 ✅ |
| 6 | 同步依赖 | `uv sync` | 步骤 5 |
| 7 | 实现 `tree_sitter_extractor.py` | TDD: 先写测试 | 步骤 6 |
| 8 | 删除 `code_analyzer.py` | `rm lib/extractors/code_analyzer.py` | 步骤 7 |
| 9 | 实现 `pdf_extractor.py` | TDD | 步骤 6 |
| 10 | 实现 `docx_extractor.py` | TDD | 步骤 6 |
| 11 | 实现 `genie_store.py` + `config.py` | TDD | 步骤 6 |
| 12 | 重构 `cli.py` | 手动 | 步骤 7-11 |
| 13 | 运行单元测试 | `uv run pytest tests/ -v` | 步骤 7-12 |
| 14 | 更新现有 SKILL.md | `/skill-creator` | 步骤 1-13 |

### 11.2 Skill 创建与更新

**使用 `/skill-creator` 更新 Skills：**

```
步骤 14.1: /skill-creator
  - 选择 "Update existing skill"
  - 选择 genie-extract
  - 添加 CLI 调用指令
  - 添加子代理格式

步骤 14.2: /skill-creator
  - 选择 "Update existing skill"
  - 选择 genie-relations
  - 添加代理消费关系
  - 添加审查流程

步骤 14.3: /skill-creator
  - 选择 "Update existing skill"
  - 选择 genie-insights
  - 添加 disputed 项审查流程

步骤 14.4: /skill-creator
  - 选择 "Update existing skill"
  - 选择 genie-report
  - 添加 Store 读取格式
```

### 11.3 评估阶段

**步骤 15: 运行所有评估**

```bash
# 15.1 单元测试
uv run pytest tests/ -v --cov=lib --cov-report=html

# 15.2 集成测试
uv run pytest tests/integration/ -v

# 15.3 CLI 测试
uv run genie extract tests/fixtures/sample.md --output json
uv run genie analyze
uv run genie report --format html
```

**步骤 16: Skill 评估**

```
/skill-creator
  - 选择 "Run skill evaluation"
  - 选择所有 skills
  - 等待评估完成
  - 查看报告
```

**步骤 17: E2E 测试（真实文档）**

```bash
# 17.1 下载测试文档
mkdir -p tests/e2e/fixtures
curl -L "https://arxiv.org/pdf/2401.00123.pdf" -o tests/e2e/fixtures/paper.pdf
curl -L "https://raw.githubusercontent.com/OAI/OpenAPI-Specification/main/examples/v3.0/petstore.yaml" -o tests/e2e/fixtures/api.yaml

# 17.2 运行 E2E 测试
uv run genie extract tests/e2e/fixtures/ --depth deep --output .genie/e2e_boxes.json
uv run genie analyze
uv run genie report --format html --output tests/e2e/report.html

# 17.3 打开报告验证
open tests/e2e/report.html  # macOS
# 或 xdg-open tests/e2e/report.html  # Linux
```

### 11.4 基线对比

**步骤 18: 创建无 Skill 基线**

```bash
# 18.1 创建基线分支
git checkout -b baseline-no-skill

# 18.2 禁用 Skills（重命名）
mv skills/ skills_disabled/

# 18.3 运行基线测试
uv run genie extract tests/e2e/fixtures/ --output .genie/baseline_boxes.json

# 18.4 记录基线指标
uv run python scripts/record_baseline.py

# 18.5 切回主分支对比
git checkout main
uv run python scripts/compare_baseline.py
```

### 11.5 自动修复与提交

**步骤 19: 自动修复问题**

```bash
# 19.1 运行 linter 并自动修复
uv run ruff check lib/ --fix
uv run ruff format lib/
uv run mypy lib/

# 19.2 重新运行失败的测试
uv run pytest tests/ --lf -v

# 19.3 如果仍有失败，手动修复后重复 19.1-19.2
```

**步骤 20: 最终验证**

```bash
# 20.1 完整测试套件
uv run pytest tests/ -v --cov

# 20.2 所有评估通过确认
uv run genie eval --all

# 20.3 基线对比通过
uv run python scripts/compare_baseline.py --assert-improvement
```

**步骤 21: 提交并推送**

```bash
# 21.1 查看变更
git status
git diff

# 21.2 暂存所有变更
git add -A

# 21.3 提交
git commit -m "feat: doc-genie v0.2.0 - complete refactor

- Move plugin.json to .claude-plugin/
- Add commands/ directory with slash commands
- Add agents/ directory with specialized agents
- Implement tree-sitter extractor (C/JS/TS/Python)
- Implement PDF/DOCX extractors
- Add project-level config (.genie/config.yaml)
- Add depth profiles (quick/medium/deep)
- Update all SKILL.md with CLI instructions
- All tests passing: 40+ unit, 5+ integration, E2E
- Baseline comparison: +30% relationship recall

Co-Authored-By: Claude <noreply@anthropic.com>"

# 21.4 推送
git push origin main
```

### 11.6 评估矩阵总结

| 评估类型 | 命令 | 步骤 | 自动修复 |
|----------|------|------|----------|
| 单元测试 | `uv run pytest tests/ -v` | 13, 15 | ruff --fix |
| 集成测试 | `uv run pytest tests/integration/` | 15 | 手动 |
| Skill 评估 | `/skill-creator` | 16 | 手动 |
| E2E 测试 | `uv run genie eval --e2e` | 17 | 手动 |
| 基线对比 | `scripts/compare_baseline.py` | 18 | N/A |
| 最终验证 | `uv run genie eval --all` | 20 | N/A |

---

```
                    ┌──────────────┐
                    │ Agent Result │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ Auto Review  │  Format + Confidence
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │confirmed │ │needs_    │ │rejected  │
        │          │ │review    │ │          │
        └────┬─────┘ └────┬─────┘ └──────────┘
             │            │
             │            ▼
             │     ┌──────────────┐
             │     │ AI Review    │  genie-insights
             │     │ (Skill)      │
             │     └──────┬───────┘
             │            │
             │    ┌───────┼───────┐
             │    │       │       │
             │    ▼       ▼       ▼
             │ ┌──────┐ ┌──────┐ ┌────────┐
             │ │confirm│ │dispute│ │escalate│
             │ └──┬───┘ └──┬───┘ └────────┘
             │    │        │
             └────┴────────┘
                  │
                  ▼
           ┌──────────────┐
           │ Final Store  │  Used by all Skills
           └──────────────┘
```

---

## 10. 实施顺序

| 步骤 | 任务 | 依赖 |
|------|------|------|
| 1 | 创建 `.claude-plugin/plugin.json` | 无 |
| 2 | 创建 `commands/*.md` | 步骤 1 |
| 3 | 创建 `agents/doc-analyzer.md` | 步骤 1 |
| 4 | 删除旧 `plugin.json` | 步骤 1 |
| 5 | 实现 `tree_sitter_extractor.py` | 无 |
| 6 | 删除 `code_analyzer.py` | 步骤 5 |
| 7 | 实现 `pdf_extractor.py` | 无 |
| 8 | 实现 `docx_extractor.py` | 无 |
| 9 | 实现 `genie_store.py` | 无 |
| 10 | 重构 `cli.py` | 步骤 5-8 |
| 11 | 更新 `pyproject.toml` | 无 |
| 12 | 更新 SKILL.md 添加 CLI 指令 | 步骤 1-10 |
| 13 | 测试验证 | 全部完成 |

---

## 12. 验证清单

完成后验证：

- [ ] `.claude-plugin/plugin.json` 存在
- [ ] `commands/` 目录有 3 个 `.md` 文件
- [ ] `agents/` 目录有 7 个代理定义文件
- [ ] `uv sync` 成功安装所有依赖（默认 C/JS/TS/Python）
- [ ] CLI `uv run genie extract file.py --output json` 输出有效 JSON
- [ ] CLI 可解析 .md/.pdf/.docx/.py/.js/.ts/.c 文件
- [ ] `.genie/config.yaml` 支持深度配置
- [ ] SKILL.md 有明确的 CLI 调用指令
- [ ] `/skill-creator` 评估通过
- [ ] E2E 测试：真实文档生成可视化报告

---

## 13. 风险评估

| 风险 | 影响 | 缓解 |
|------|------|------|
| tree-sitter 语言包版本冲突 | 安装失败 | 使用 >=0.23.0 宽版本约束 |
| PDF 布局复杂提取不准 | 信息丢失 | pdfplumber + PyMuPDF 双引擎 |
| 用户无 Python 环境 | CLI 不可用 | Skill 可降级到纯 AI 分析 |
| 代理结果冲突 | 合并困难 | 置信度投票 + 人工确认 |
| 深度分析耗时 | 用户体验差 | 默认 medium，deep 可选 |

---

## 14. 参考资料

### 工具与框架

- [tree-sitter-analyzer](https://pypi.org/project/tree-sitter-analyzer/) - MCP 集成、统一元素管理
- [ast-grep](https://ast-grep.github.io/) - 结构化搜索/替换
- [Depends](https://github.com/multilang-depends/depends) - 多语言依赖分析
- [pyan3](https://github.com/Technologicat/pyan) - Python 静态调用图

### 多代理模式

- [Anthropic Multi-Agent Research](https://www.anthropic.com/engineering/multi-agent-research-system) - Orchestrator-Worker 模式
- [Azure AI Agent Patterns](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns) - 编排模式
- [Agent Evaluation Guide](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) - 评估框架

### 知识图谱与追溯

- [Claude Knowledge Graph Guide](https://platform.claude.com/cookbook/capabilities-knowledge-graph-guide) - 实体关系提取
- [SpecMap](https://arxiv.org/abs/2601.11688) - 层次化追溯
- [FTLR](https://github.com/tobhey/finegrained-traceability) - 细粒度追溯