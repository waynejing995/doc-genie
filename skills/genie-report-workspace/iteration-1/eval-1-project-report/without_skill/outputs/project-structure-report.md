# doc-genie 项目结构报告

> 生成日期: 2026-03-31

## 1. 项目概述

doc-genie 是一个跨平台插件，用于从文档和代码中提取"黑盒"组件，分析组件间关系，发现跨文档洞察。

**核心价值**:
- 一次读取文档 → 提取结构化黑盒定义
- 自动发现组件关系（显式 + 隐式）
- 跨文档分析：冲突检测、模式识别、架构洞察

**设计原则**:
- 纯本地依赖，无外部服务
- 复用现有成熟工具（ast-grep、pdfplumber、python-docx）
- 语义分析由 SKILL 指导 AI 助手执行（非外部 LLM API）

---

## 2. 架构图

```
┌─────────────────────────────────────────────────────────────────────┐
│                         doc-genie 架构                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                │
│  │   PDF 文件   │  │  DOCX 文件  │  │  Markdown   │                │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘                │
│         │                │                │                        │
│         ▼                ▼                ▼                        │
│  ┌─────────────────────────────────────────────────────────┐      │
│  │            extractors/ (提取器模块)                      │      │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐   │      │
│  │  │pdf_extractor│ │docx_extractor│ │markdown_extractor│  │      │
│  │  └─────────────┘ └─────────────┘ └─────────────────┘   │      │
│  └─────────────────────────────────────────────────────────┘      │
│                                                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                │
│  │ Python 代码  │  │ JS/TS 代码  │  │  C 代码     │                │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘                │
│         │                │                │                        │
│         ▼                ▼                ▼                        │
│  ┌─────────────────────────────────────────────────────────┐      │
│  │            extractors/ (代码提取器)                       │      │
│  │  ┌──────────────────┐  ┌──────────────────────────┐     │      │
│  │  │  code_analyzer    │  │  tree_sitter_extractor   │     │      │
│  │  │  (AST 解析)        │  │  (多语言树解析)            │     │      │
│  │  └──────────────────┘  └──────────────────────────┘     │      │
│  └─────────────────────────────────────────────────────────┘      │
│                              │                                     │
│                              ▼                                     │
│  ┌─────────────────────────────────────────────────────────┐      │
│  │                核心数据模型 (lib/)                         │      │
│  │  ┌────────────────┐  ┌────────────────────────────┐     │      │
│  │  │ blackbox_model │  │   relationship_types        │     │      │
│  │  │ (黑盒定义)      │  │   (关系类型枚举)            │     │      │
│  │  └────────────────┘  └────────────────────────────┘     │      │
│  └─────────────────────────────────────────────────────────┘      │
│                              │                                     │
│                              ▼                                     │
│  ┌─────────────────────────────────────────────────────────┐      │
│  │           patterns/ (模式检测模块)                         │      │
│  │  ┌──────────────────────────────────────────────────┐   │      │
│  │  │         relationship_patterns (PatternDetector)    │   │      │
│  │  │         - IO 匹配检测                               │   │      │
│  │  │         - 文本引用检测                               │   │      │
│  │  │         - 依赖模式检测                               │   │      │
│  │  └──────────────────────────────────────────────────┘   │      │
│  └─────────────────────────────────────────────────────────┘      │
│                              │                                     │
│                              ▼                                     │
│  ┌─────────────────────────────────────────────────────────┐      │
│  │              storage/ (存储模块)                          │      │
│  │  ┌──────────────────────────────────────────────────┐   │      │
│  │  │              genie_store (GenieStore)              │   │      │
│  │  │              - boxes.json (黑盒存储)                │   │      │
│  │  │              - relationships.json (关系存储)        │   │      │
│  │  │              - patterns.json (模式存储)             │   │      │
│  │  │              - index.json (快速索引)                 │   │      │
│  │  └──────────────────────────────────────────────────┘   │      │
│  └─────────────────────────────────────────────────────────┘      │
│                              │                                     │
│                              ▼                                     │
│  ┌─────────────────────────────────────────────────────────┐      │
│  │              config.py (配置管理)                         │      │
│  │  - 深度级别 (quick/medium/deep)                          │      │
│  │  - 文件类型过滤                                          │      │
│  │  - 排除模式                                              │      │
│  └─────────────────────────────────────────────────────────┘      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. 目录结构

```
lib/
├── __init__.py                 # 模块初始化
├── blackbox_model.py           # 黑盒数据模型
├── config.py                   # 配置管理
├── relationship_types.py       # 关系类型定义
├── extractors/                 # 提取器模块
│   ├── code_analyzer.py        # Python AST 代码分析
│   ├── markdown_extractor.py   # Markdown 提取器
│   ├── tree_sitter_extractor.py # Tree-sitter 多语言提取
│   ├── pdf_extractor.py        # PDF 提取器
│   └── docx_extractor.py       # DOCX 提取器
├── patterns/                   # 模式检测模块
│   └── relationship_patterns.py # 关系模式检测器
└── storage/                    # 存储模块
    ├── __init__.py
    └── genie_store.py          # 持久化存储
```

---

## 4. 组件摘要

### 4.1 核心模块

| 模块 | 文件 | 职责 |
|------|------|------|
| **blackbox_model.py** | `/Volumes/data/User/wayne/Code/doc-genie/lib/blackbox_model.py` | 定义黑盒数据结构：`BlackBox`, `BlackBoxInput`, `BlackBoxOutput`, `BlackBoxSource`, `BlackBoxAttributes` |
| **relationship_types.py** | `/Volumes/data/User/wayne/Code/doc-genie/lib/relationship_types.py` | 定义关系类型枚举：`RelationshipType` (22种), `RelationshipCategory` (7类), `Relationship` 数据类 |
| **config.py** | `/Volumes/data/User/wayne/Code/doc-genie/lib/config.py` | 配置管理：深度级别、文件类型过滤、排除模式、项目配置加载 |

### 4.2 提取器模块 (lib/extractors/)

| 提取器 | 文件 | 支持格式 | 主要功能 |
|--------|------|----------|----------|
| **CodeAnalyzer** | `code_analyzer.py` | Python | 使用 AST 解析 Python 代码，提取函数、类、导入 |
| **TreeSitterExtractor** | `tree_sitter_extractor.py` | Python, JS, TS, C, Go, Java, Rust | 使用 tree-sitter 多语言解析，提取函数、类、导入 |
| **MarkdownExtractor** | `markdown_extractor.py` | .md | 提取章节、输入输出定义 |
| **PDF Extractor** | `pdf_extractor.py` | .pdf | 使用 pdfplumber 提取文本和章节结构 |
| **DOCX Extractor** | `docx_extractor.py` | .docx | 使用 python-docx 提取标题、段落、表格 |

### 4.3 模式检测模块 (lib/patterns/)

| 检测器 | 文件 | 功能 |
|--------|------|------|
| **PatternDetector** | `relationship_patterns.py` | 检测黑盒间关系：IO 匹配检测、文本引用检测、依赖模式检测 |

### 4.4 存储模块 (lib/storage/)

| 存储类 | 文件 | 功能 |
|--------|------|------|
| **GenieStore** | `genie_store.py` | 持久化存储黑盒、关系、模式数据，维护快速索引 |

---

## 5. 数据模型详情

### 5.1 BlackBox 黑盒模型

```python
@dataclass
class BlackBox:
    id: str                           # 唯一标识
    name: str                         # 名称
    source: BlackBoxSource            # 来源信息
    inputs: list[BlackBoxInput]       # 输入列表
    outputs: list[BlackBoxOutput]     # 输出列表
    attributes: BlackBoxAttributes    # 属性（约束、依赖、属性）
```

### 5.2 Relationship 关系模型

```python
@dataclass
class Relationship:
    source_id: str                    # 源黑盒 ID
    target_id: str                    # 目标黑盒 ID
    type: RelationshipType            # 关系类型 (22种)
    category: RelationshipCategory    # 关系类别 (7类)
    confidence: float                 # 置信度
    evidence: str                     # 证据描述
```

### 5.3 关系类别

| 类别 | 说明 | 包含关系类型 |
|------|------|------------|
| DATA | 数据关系 | data_flow, transform, aggregate, cache |
| CONTROL | 控制关系 | dependency, sequence, preempt, routing |
| STRUCTURE | 结构关系 | composition, extension, version, alternative |
| INTERACTION | 交互关系 | interface, notification, delegation, synchronization |
| CONSTRAINT | 约束关系 | constraint, validation, authorization, rate_limit |
| ISSUE | 问题关系 | conflict, replication, override, fallback |
| MONITORING | 监控关系 | monitoring |

---

## 6. 配置选项

### 6.1 深度级别

| 级别 | 最小行数 | 最小字符 | 特点 |
|------|----------|----------|------|
| quick | 20 | 300 | 快速扫描，提取签名 |
| medium | 5 | 100 | 平衡模式（默认） |
| deep | 1 | 30 | 深度分析，提取注释、隐式关系 |

### 6.2 支持文件类型

- 文档: `.md`, `.pdf`, `.docx`
- 代码: `.py`, `.js`, `.ts`, `.jsx`, `.tsx`, `.c`, `.h`, `.go`, `.java`, `.rb`, `.rs`

---

## 7. 技能系统

项目通过 SKILL 系统支持 AI 助手执行语义分析：

| 技能 | 目的 | 触发词 |
|------|------|--------|
| genie-extract | 提取黑盒 | extract, parse, analyze |
| genie-relations | 映射关系 | relationship, dependency |
| genie-insights | 深度分析 | conflicts, implicit, patterns |
| genie-report | 生成报告 | report, visualize, diagram |

---

## 8. 测试覆盖

测试文件位于 `/Volumes/data/User/wayne/Code/doc-genie/tests/`:

| 测试文件 | 测试目标 |
|----------|----------|
| test_blackbox_model.py | 黑盒模型 |
| test_relationship_types.py | 关系类型 |
| test_config.py | 配置管理 |
| test_code_analyzer.py | 代码分析器 |
| test_tree_sitter_extractor.py | Tree-sitter 提取器 |
| test_markdown_extractor.py | Markdown 提取器 |
| test_pdf_extractor.py | PDF 提取器 |
| test_docx_extractor.py | DOCX 提取器 |
| test_relationship_patterns.py | 关系模式检测 |
| test_genie_store.py | 存储模块 |
| test_cli.py | 命令行接口 |

---

## 9. 依赖项

项目依赖以下主要包：

| 包名 | 用途 |
|------|------|
| pdfplumber | PDF 文本提取 |
| python-docx | DOCX 文档解析 |
| tree-sitter-python | Python 语法解析 |
| tree-sitter-javascript | JavaScript 语法解析 |
| tree-sitter-typescript | TypeScript 语法解析 |
| tree-sitter-c | C 语言语法解析 |
| PyYAML | 配置文件解析 |
| networkx | 图计算（计划中） |

---

## 10. 总结

doc-genie 是一个模块化的文档分析工具，采用三层架构：

1. **Layer 1 (结构提取)**: 使用 AST 解析器和文档解析器提取结构化数据
2. **Layer 2 (规则检测)**: 使用正则匹配和 IO 分析检测显式关系
3. **Layer 3 (语义分析)**: 通过 SKILL 系统指导 AI 助手执行深度分析

核心设计特点：
- 纯本地依赖，无外部 API 调用
- 支持多种文档和代码格式
- 可配置的深度级别
- 完整的关系类型体系
- 持久化存储与快速索引