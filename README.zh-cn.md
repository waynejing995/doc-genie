# doc-genie

从文档和代码中提取黑盒组件。映射关系。发现跨文档洞察。

> 纯本地运行，无外部服务，无 LLM API 调用。

## 功能

1. **提取** — 解析 PDF/DOCX/Markdown/代码为结构化黑盒（输入、输出、约束）
2. **关系** — 映射关系：数据流、依赖、调用、约束
3. **洞察** — 深度分析：隐式关系、冲突检测、模式识别（SKILL 指导 AI 执行）
4. **报告** — 生成报告：Markdown + Mermaid、表格、交互式网页

## 快速开始

```bash
# 安装
uv venv
uv pip install -e .

# 分析文档
genie-extract spec1.pdf spec2.md src/
genie-analyze
genie-report --format markdown
```

## 技能

| 技能 | 用途 | 触发词 |
|------|------|--------|
| `genie-extract` | 提取黑盒 | extract, parse, analyze |
| `genie-relations` | 映射关系 | relationship, dependency |
| `genie-insights` | 深度分析 | conflicts, implicit, patterns |
| `genie-report` | 生成报告 | report, visualize, diagram |

## 平台支持

| 平台 | 集成方式 |
|------|----------|
| Claude Code | `plugin.json` + `skills/` |
| OpenCode | `openclaw-plugin.json` + `skills/` |
| Cursor | `.cursor/rules/*.mdc` |
| Copilot | `.github/copilot-instructions.md` |
| CLI | `scripts/cli.py` |

## 架构

```
Layer 1: 结构提取 (ast-grep, pdfplumber, python-docx)
     │
     ▼
Layer 2: 模式检测 (正则, IO 匹配, 名称引用)
     │
     ▼
Layer 3: 语义分析 (SKILL 指导 AI, 无外部 LLM)
```

## 许可证

MIT
