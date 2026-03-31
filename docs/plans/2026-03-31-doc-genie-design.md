# doc-genie 设计文档

> 日期: 2026-03-31
> 状态: 已批准
> 作者: Sisyphus

## 1. 概述

doc-genie 是一个跨平台插件，用于从文档和代码中提取"黑盒"组件，分析组件间关系，发现跨文档洞察。

### 核心价值
- 一次读取文档 → 提取结构化黑盒定义
- 自动发现组件关系（显式 + 隐式）
- 跨文档分析：冲突检测、模式识别、架构洞察

### 设计原则
- 纯本地依赖，无外部服务
- 复用现有成熟工具（ast-grep、pdfplumber、pyan3）
- 语义分析由 SKILL 指导 AI 助手执行（非外部 LLM API）

---

## 2. 架构

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                      doc-genie                              │
├─────────────────────────────────────────────────────────────┤
│  Layer 1: 结构提取                                          │
│  ast-grep + pdfplumber + python-docx + markdown-it-py      │
│  (纯本地，快速)                                             │
├─────────────────────────────────────────────────────────────┤
│  Layer 2: 规则检测                                          │
│  正则模式 + IO 匹配 + 名称引用 + 代码调用图                 │
│  (纯本地，快速)                                             │
├─────────────────────────────────────────────────────────────┤
│  Layer 3: 语义分析（SKILL 驱动）                            │
│  AI 助手根据 SKILL.md 指令执行深度分析                      │
│  (无外部 LLM API，AI 已在运行)                              │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 技能划分

| 技能 | 职责 | 触发词 |
|------|------|--------|
| genie-extract | 提取黑盒：输入、输出、属性 | extract, parse, analyze |
| genie-relations | 映射关系：数据流、依赖、调用 | relationship, dependency |
| genie-insights | 深度分析：隐式关系、冲突、模式 | deep analysis, conflicts |
| genie-report | 生成报告：MD、表格、可视化 | report, visualize, diagram |

---

## 3. 黑盒模型

### 3.1 数据结构

```yaml
blackbox:
  id: "bb-001"
  name: "用户认证服务"
  source:
    type: "document" | "code" | "api_spec" | "config"
    file: "auth-spec.md"
    section: "## 3. Authentication"
    line_range: [45, 120]
  
  inputs:
    - name: "用户凭证"
      type: "data"
      required: true
      format: "string"
  
  outputs:
    - name: "JWT Token"
      type: "data"
      format: "string"
  
  attributes:
    constraints:
      - "密码最少8位"
      - "最多5次失败后锁定"
    dependencies:
      - "bb-005"
    properties:
      owner: "auth-team"
      status: "approved"
```

### 3.2 输入源支持

| 类型 | 格式 | 提取工具 |
|------|------|----------|
| 文档 | MD, PDF, DOC/DOCX | markdown-it-py, pdfplumber, python-docx |
| 代码 | Python, JS, TS, Go, Java | ast-grep-py |
| API 定义 | OpenAPI, GraphQL | 结构化解析 |
| 配置 | YAML, JSON, TOML | PyYAML |

---

## 4. 关系类型

### 4.1 完整关系分类

| 类别 | 关系类型 | 符号 | 示例 |
|------|----------|------|------|
| 数据 | data_flow | → | A 输出 Token → B 消耗 Token |
| 数据 | transform | ⟹ | XML → JSON |
| 数据 | aggregate | ⊕ | 汇总 A, B, C |
| 数据 | cache | ⊇ | Redis 缓存数据库 |
| 控制 | dependency | ⟵ | A 依赖 B |
| 控制 | sequence | → | 先认证后授权 |
| 控制 | preempt | ⇏ | 超时中断长任务 |
| 控制 | routing | ⇢ | 网关路由到服务 |
| 结构 | composition | ◆ | 电商包含支付 |
| 结构 | extension | + | 插件扩展核心 |
| 结构 | version | v | API v2 是 v1 升级 |
| 结构 | alternative | ∥ | 密码登录 vs OAuth |
| 交互 | interface | ⟶ | 前端调用后端 API |
| 交互 | notification | ! | 状态变更通知 |
| 交互 | delegation | ⇒ | 控制器委托服务 |
| 交互 | synchronization | ⇔ | 主从数据库同步 |
| 约束 | constraint | ⊢ | 速率限制约束 |
| 约束 | validation | ✓ | 数据校验验证 |
| 约束 | authorization | 🔑 | RBAC 权限控制 |
| 约束 | rate_limit | ⏱ | API 调用频率限制 |
| 问题 | conflict | ⚡ | 两个 spec 矛盾 |
| 问题 | replication | ≡ | 重复定义 |
| 问题 | override | ⬆ | 配置覆盖默认 |
| 问题 | fallback | ↺ | 主库宕机切备用 |
| 监控 | monitoring | 👁 | 健康检查 |

### 4.2 关系检测策略

| 层级 | 方法 | 检测的关系类型 |
|------|------|----------------|
| Layer 1 | ast-grep + pyan3 | import, call, inheritance |
| Layer 2 | 正则 + IO 匹配 | data_flow, dependency, interface |
| Layer 3 | SKILL 指导 AI | semantic_dependency, data_transform, temporal, constraint_propagation |

---

## 5. 关系管理

### 5.1 增量更新策略

```
新增 N 个黑盒
     │
     ▼
┌─────────────────┐
│ 更新索引        │ by_name, by_keyword, by_file
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 找候选黑盒      │ 同文件 + 名称引用 + 关键词重叠 + IO 匹配
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 检测关系        │ 只检查候选集，不全量扫描
└─────────────────┘
```

### 5.2 数据持久化

```
.genie/
├── boxes.json              # 黑盒定义
├── relationships.json      # 关系列表
└── index.json              # 快速查找索引
```

---

## 6. 分析能力

### 6.1 连接洞察（Insights）

- 依赖地图：谁依赖谁、谁调用谁
- 关键路径：最长链路、瓶颈
- 影响范围：改 X 影响哪些
- 数据血缘：数据从哪来到哪去
- 覆盖情况：哪些需求有对应实现
- 层级结构：谁包含谁

### 6.2 问题检测（Issues）

- 接口不匹配：A 输出 ≠ B 输入
- 缺失依赖：A 依赖 B，但 B 不存在
- 矛盾约束：两个文档定义冲突
- 孤儿节点：没有输入或没有输出
- 循环依赖：A→B→C→A
- 重复定义：多个文档定义同一东西

### 6.3 风险提示（Risks）

- 单点故障：关键节点无备份
- 信任边界穿越：安全边界组件交互
- 复杂度警告：过度耦合
- 所有权缺口：没人负责的组件

---

## 7. 输出格式

### 7.1 Markdown 报告（含 Mermaid）

```markdown
# 系统架构分析报告

## 架构图
\`\`\`mermaid
graph TD
    A[认证] -->|Token| B[网关]
    B -->|路由| C[订单]
\`\`\`

## 问题清单
| 严重度 | 类型 | 描述 |
|--------|------|------|
| ❌ | 接口不匹配 | Token 格式不一致 |
```

### 7.2 表格汇总

```markdown
| 黑盒 | 输入 | 输出 | 依赖 | 状态 |
|------|------|------|------|------|
| 认证 | 2 | 1 | 1 | ✅ |
```

### 7.3 交互式网页（vis.js CDN）

单文件 HTML，使用 vis.js CDN，无需构建。

### 7.4 DOT 文件

可导出为 Graphviz DOT 格式，用任何工具渲染。

---

## 8. 跨平台适配

### 8.1 插件结构

```
doc-genie/
├── plugin.json                    # Claude Code
├── openclaw-plugin.json           # OpenCode
├── AGENTS.md                      # 跨平台标准
├── .cursor/rules/doc-genie.mdc    # Cursor
├── .github/copilot-instructions.md # Copilot
├── skills/
│   ├── genie-extract/
│   ├── genie-relations/
│   ├── genie-insights/
│   └── genie-report/
├── lib/
│   ├── blackbox_model.py
│   ├── relationship_types.py
│   ├── visualizer.py
│   ├── extractors/
│   │   ├── pdf_layout.py
│   │   ├── docx_structure.py
│   │   └── code_analyzer.py
│   └── patterns/
│       └── relationship_patterns.py
├── templates/
│   ├── report.md
│   └── web-report.html
└── scripts/
    └── cli.py
```

### 8.2 平台支持

| 平台 | 适配方式 |
|------|----------|
| Claude Code | plugin.json + skills/ |
| OpenCode | openclaw-plugin.json + skills/ |
| Cursor | .cursor/rules/*.mdc |
| Copilot | .github/copilot-instructions.md |
| Codex | AGENTS.md + .agents/skills/ |
| CLI | scripts/cli.py |

---

## 9. 依赖

```toml
[project]
name = "doc-genie"
version = "1.0.0"
requires-python = ">=3.10"

dependencies = [
    # 文档解析
    "pdfplumber>=0.10.0",
    "PyMuPDF>=1.24.0",
    "python-docx>=1.1.0",
    "markdown-it-py>=3.0.0",
    
    # 代码解析
    "ast-grep-py>=0.20.0",
    "pyan3>=1.2.0",
    
    # 图与可视化
    "networkx>=3.0",
    
    # 工具
    "pyyaml>=6.0",
    "rich>=13.0",
]
```

**无 LLM 依赖**。语义分析由 SKILL 指导 AI 助手执行。

---

## 10. 风险与缓解

| 风险 | 影响 | 缓解 |
|------|------|------|
| ast-grep 不支持某语言 | 部分语言无法解析 | 支持 40+ 语言，覆盖主流 |
| PDF 布局复杂 | 提取不准确 | PyMuPDF4LLM + pdfplumber 双引擎 |
| 规则模式遗漏 | 显式关系漏检 | SKILL Layer 3 补充隐式分析 |
| 大文档性能 | 处理慢 | 分块处理 + 增量更新 |

---

## 11. 语言策略

- **Skills**: 英文（SKILL.md, references/）
- **代码注释**: 英文
- **README**: 英文默认 + 中文版可选（README.zh-cn.md）
- **输出报告**: 跟随用户文档语言

---

## 12. 下一步

进入实现阶段，按以下顺序：

1. 搭建项目骨架（pyproject.toml + 目录结构）
2. 实现 blackbox_model.py（数据模型）
3. 实现 genie-extract（结构提取）
4. 实现 genie-relations（关系映射）
5. 实现 genie-insights（SKILL 编写）
6. 实现 genie-report（报告生成）
7. 集成测试
8. 打包发布
