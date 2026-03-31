# doc-genie 插件重构计划

> 日期: 2026-03-31
> 状态: 待批准
> 目标: 将 doc-genie 从非规范结构转换为标准 Claude Code 插件结构

## 1. 当前问题分析

### 结构问题

| 问题 | 当前状态 | 正确规范 |
|------|----------|----------|
| manifest 位置 | `plugin.json` 在根目录 | 必须在 `.claude-plugin/plugin.json` |
| manifest 内容 | 缺少必要字段 | 需要 name + 元数据 |
| 多平台配置 | `openclaw-plugin.json` 混用 | Claude Code 专用 |
| 命令定义 | 在 manifest 中用 script | 应使用 `commands/` 目录 |
| 无 commands 目录 | 缺失 | 应有 `commands/*.md` |
| 无 agents 目录 | 缺失 | 可选，但有助于复杂任务 |

### 当前文件结构

```
doc-genie/
├── plugin.json              # ❌ 位置错误，应在 .claude-plugin/
├── openclaw-plugin.json     # ❌ 混合平台配置，应删除或分离
├── skills/                  # ✅ 正确
│   ├── genie-extract/SKILL.md
│   ├── genie-relations/SKILL.md
│   ├── genie-insights/SKILL.md
│   └── genie-report/SKILL.md
├── lib/                     # ⚠️ 可保留作为支持代码
├── scripts/                 # ⚠️ 未使用，可整合
├── docs/                    # ✅ 设计文档
├── AGENTS.md                # ⚠️ 跨平台指令，可保留
├── .cursor/rules/           # ⚠️ Cursor 适配，可保留
└── .github/copilot-instructions.md  # ⚠️ Copilot 适配，可保留
```

---

## 2. 目标结构

### 标准 Claude Code 插件结构

```
doc-genie/
├── .claude-plugin/
│   └── plugin.json          # 标准 manifest
├── commands/                 # 用户可调用的命令
│   ├── genie-extract.md     # /genie-extract
│   ├── genie-analyze.md     # /genie-analyze
│   └── genie-report.md      # /genie-report
├── agents/                   # 可选：自动化子代理
│   └── doc-analyzer.md      # 自动文档分析代理
├── skills/                   # 自动激活的技能（保留现有）
│   ├── genie-extract/
│   │   ├── SKILL.md
│   │   └── OUTPUT.md
│   ├── genie-relations/
│   │   ├── SKILL.md
│   │   └── OUTPUT.md
│   ├── genie-insights/
│   │   ├── SKILL.md
│   │   └able OUTPUT.md
│   └── genie-report/
│       ├── SKILL.md
│       └able OUTPUT.md
├── lib/                      # Python 支持代码（保留）
│   ├── blackbox_model.py
│   ├── relationship_types.py
│   └── extractors/
├── tests/                    # 测试文件（保留）
├── scripts/                  # CLI 工具（可选保留）
├── .mcp.json                 # 可选：MCP 服务器定义
├── AGENTS.md                 # 跨平台兼容（保留）
├── .cursor/rules/            # Cursor 兼容（保留）
└── .github/copilot-instructions.md  # Copilot 兼容（保留）
```

---

## 3. 实施步骤

### Step 1: 创建标准 manifest

**文件**: `.claude-plugin/plugin.json`

```json
{
  "name": "doc-genie",
  "version": "0.1.0",
  "description": "Extract black boxes from docs/code, map relationships, discover cross-doc insights",
  "author": {
    "name": "waynejing995"
  },
  "license": "MIT",
  "keywords": ["documentation", "analysis", "architecture", "black-box"]
}
```

### Step 2: 创建命令文件

**commands/genie-extract.md**:
```markdown
---
name: genie-extract
description: Extract black boxes from documents and code files
---

# Extract Black Boxes

Invoke the genie-extract skill to extract structured black boxes from the specified files.

## Usage

Run on a file or directory:
- Single file: `/genie-extract path/to/file.pdf`
- Directory: `/genie-extract path/to/docs/`

The skill will parse and output YAML-formatted black boxes.
```

**commands/genie-analyze.md**:
```markdown
---
name: genie-analyze
description: Analyze relationships between extracted black boxes
---

# Analyze Relationships

Invoke genie-relations and genie-insights skills to map relationships and find insights.

## Usage

After extraction, run:
`/genie-analyze`

This will detect data flows, dependencies, conflicts, and patterns.
```

**commands/genie-report.md**:
```markdown
---
name: genie-report
description: Generate analysis report with diagrams
---

# Generate Report

Invoke genie-report skill to create a structured report.

## Usage

`/genie-report [output.md]`

Generates Markdown with Mermaid diagrams, tables, and insights.
```

### Step 3: 创建自动化代理（可选）

**agents/doc-analyzer.md**:
```markdown
---
description: Automatically analyze documents for black boxes and relationships
capabilities:
  - Extract black boxes from documents and code
  - Map relationships between components
  - Detect conflicts and patterns
---

# Document Analyzer Agent

This agent performs comprehensive document analysis:

1. Extract black boxes using genie-extract skill
2. Map relationships using genie-relations skill
3. Find insights using genie-insights skill
4. Generate report using genie-report skill

Use when: user provides multiple documents needing full analysis.
```

### Step 4: 清理旧文件

- 移动 `plugin.json` → `.claude-plugin/plugin.json`
- 删除或重命名 `openclaw-plugin.json`（如需多平台支持，保留但分离）
- 删除根目录旧的 `plugin.json`

### Step 5: 更新文档

更新 README.md 说明正确安装方式：
```markdown
## Installation

1. Clone or download this plugin
2. In Claude Code: Settings → Plugins → Add local plugin
3. Select the doc-genie directory
4. Plugin auto-loads commands, agents, and skills
```

---

## 4. skills 保留内容

现有 skills 结构正确，无需修改：

| Skill | 文件 | 状态 |
|-------|------|------|
| genie-extract | skills/genie-extract/SKILL.md | ✅ 保留 |
| genie-relations | skills/genie-relations/SKILL.md | ✅ 保留 |
| genie-insights | skills/genie-insights/SKILL.md | ✅ 保留 |
| genie-report | skills/genie-report/SKILL.md | ✅ 保留 |

每个 skill 的 OUTPUT.md 也保留，用于子代理模板。

---

## 5. lib/ 代码处理

Python 库代码保留，作为 skill 执行的支持工具：

```
lib/
├── __init__.py
├── blackbox_model.py      # 数据模型
├── relationship_types.py  # 关系类型定义
├── extractors/
│   ├── code_analyzer.py   # 代码提取器
│   └ markdown_extractor.py # Markdown 提取器
```

Skill 文档中可引用 `$CLAUDE_PLUGIN_ROOT/lib/` 路径。

---

## 6. 多平台兼容策略

| 平台 | 配置文件 | 处理方式 |
|------|----------|----------|
| Claude Code | `.claude-plugin/plugin.json` | 主要配置 |
| OpenCode | `openclaw-plugin.json` | 可保留独立文件 |
| Cursor | `.cursor/rules/doc-genie.mdc` | 保留 |
| Copilot | `.github/copilot-instructions.md` | 保留 |
| Codex | `AGENTS.md` | 保留 |

Claude Code 配置独立，不影响其他平台适配。

---

## 7. 验证清单

完成后验证：

- [ ] `.claude-plugin/plugin.json` 存在且格式正确
- [ ] `commands/` 目录存在，包含 `.md` 文件
- [ ] 每个 command 有 YAML frontmatter
- [ ] `skills/*/SKILL.md` 文件存在
- [ ] 无重复的根目录 `plugin.json`
- [ ] README 更新安装说明

---

## 8. 执行顺序

1. 创建 `.claude-plugin/` 目录
2. 创建新的 `plugin.json`
3. 创建 `commands/` 目录和命令文件
4. 创建 `agents/` 目录和代理文件（可选）
5. 删除根目录旧 `plugin.json`
6. 更新 README.md
7. 验证插件加载

---

## 9. 依赖关系

- Step 1-3 可并行执行
- Step 4-6 依赖 Step 1-3 完成
- Step 7 依赖全部完成

---

## 10. 风险评估

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 现有技能不加载 | 功能丢失 | skills 结构正确，风险低 |
| 命令不生效 | 用户无法调用 | 验证 frontmatter 格式 |
| 跨平台兼容破坏 | 其他平台失效 | 保留独立配置文件 |