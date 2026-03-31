# lib/config.py 与 lib/storage/genie_store.py 函数关系分析

## 1. 模块概述

### lib/config.py - GenieConfig 类
配置管理模块，负责加载和管理项目配置。

**函数列表：**
| 函数名 | 类型 | 描述 |
|--------|------|------|
| `__init__(project_root)` | 构造函数 | 初始化，设置项目根目录和配置文件路径 |
| `_load_config()` | 私有方法 | 加载配置文件或返回默认值 |
| `_merge_config(default, user)` | 私有方法 | 深度合并用户配置到默认配置 |
| `depth` | 属性 | 获取当前提取深度 |
| `depth_profiles` | 属性 | 获取深度配置设置 |
| `box_size_thresholds` | 属性 | 获取按深度的盒子大小阈值 |
| `file_types` | 属性 | 获取支持的文件类型 |
| `exclude_patterns` | 属性 | 获取排除模式 |
| `should_process_file(filepath)` | 方法 | 检查文件是否应该被处理 |
| `get_depth_profile(depth)` | 方法 | 获取特定深度的设置 |
| `get_box_threshold(depth)` | 方法 | 获取特定深度的盒子大小阈值 |

### lib/storage/genie_store.py - GenieStore 类
持久化存储模块，负责保存和加载分析结果。

**函数列表：**
| 函数名 | 类型 | 描述 |
|--------|------|------|
| `__init__(project_root)` | 构造函数 | 初始化，设置项目根目录和存储文件路径 |
| `load_boxes()` | 方法 | 加载黑盒数据 |
| `save_boxes(boxes, metadata)` | 方法 | 保存黑盒数据 |
| `load_relationships()` | 方法 | 加载关系数据 |
| `save_relationships(relationships, metadata)` | 方法 | 保存关系数据 |
| `load_patterns()` | 方法 | 加载模式数据 |
| `save_patterns(patterns)` | 方法 | 保存模式数据 |
| `load_review()` | 方法 | 加载审查状态 |
| `save_review(review)` | 方法 | 保存审查状态 |
| `load_index()` | 方法 | 加载搜索索引 |
| `_update_index(boxes)` | 私有方法 | 更新搜索索引 |
| `_get_timestamp()` | 私有方法 | 获取当前时间戳 |

---

## 2. 直接依赖关系

**结论：两个模块之间没有直接依赖关系。**

- `lib/config.py` 没有导入 `lib/storage/genie_store.py`
- `lib/storage/genie_store.py` 没有导入 `lib/config.py`

---

## 3. 共享依赖

两个模块共享以下依赖：

| 依赖项 | config.py | genie_store.py |
|--------|-----------|----------------|
| `pathlib.Path` | 是 | 是 |
| `typing.Any` | 是 | 否 |
| `yaml` | 是 | 否 |
| `json` | 否 | 是 |
| `datetime` | 否 | 是（仅 `_get_timestamp` 内部导入） |

---

## 4. 概念关联

### 4.1 共享 .genie 目录

两个模块都操作 `.genie` 目录下的文件：

| 模块 | 文件路径 | 用途 |
|------|----------|------|
| GenieConfig | `.genie/config.yaml` | 存储项目配置 |
| GenieStore | `.genie/boxes.json` | 存储黑盒数据 |
| GenieStore | `.genie/relationships.json` | 存储关系数据 |
| GenieStore | `.genie/patterns.json` | 存储模式数据 |
| GenieStore | `.genie/review.json` | 存储审查状态 |
| GenieStore | `.genie/index.json` | 存储搜索索引 |

### 4.2 相似的设计模式

两个类具有相似的初始化签名：

```python
# GenieConfig
def __init__(self, project_root: str = "."):
    self.project_root = Path(project_root)
    self.config_file = self.project_root / ".genie" / "config.yaml"

# GenieStore
def __init__(self, project_root: str = "."):
    self.project_root = Path(project_root)
    self.genie_dir = self.project_root / ".genie"
```

---

## 5. 外部使用情况

### 5.1 使用 GenieConfig 的文件
- `scripts/cli.py` - 用于配置管理和初始化
- `scripts/record_baseline.py` - 用于获取配置信息
- `tests/test_config.py` - 单元测试

### 5.2 使用 GenieStore 的文件
- `tests/test_genie_store.py` - 单元测试

### 5.3 同时使用两者的文件
目前没有发现同时使用两个模块的文件。

---

## 6. 潜在的协作场景

虽然两个模块没有直接依赖，但在实际使用中可能存在以下协作模式：

```
[用户代码/CLI]
      |
      v
[GenieConfig] -----> 配置参数（depth, file_types, exclude_patterns）
      |
      v
[提取器] ---------> 黑盒数据
      |
      v
[GenieStore] ----> 持久化存储
```

**典型工作流：**
1. 使用 `GenieConfig` 加载项目配置
2. 根据配置（如 `file_types`, `exclude_patterns`）筛选要处理的文件
3. 根据配置（如 `depth`, `depth_profiles`）确定提取深度
4. 提取黑盒数据
5. 使用 `GenieStore` 保存提取结果

---

## 7. 函数调用关系图

```
lib/config.py 内部调用关系:
==========================

__init__()
    |
    +---> _load_config()
              |
              +---> _merge_config() [递归]


lib/storage/genie_store.py 内部调用关系:
========================================

__init__()  --->  设置文件路径

save_boxes()
    |
    +---> _get_timestamp()
    +---> _update_index()

save_relationships()
    |
    +---> _get_timestamp()

save_patterns()
    |
    +---> _get_timestamp()
```

---

## 8. 总结

| 维度 | 分析结果 |
|------|----------|
| 直接依赖 | 无 |
| 共享依赖 | pathlib.Path |
| 共享资源 | .genie 目录 |
| 设计相似性 | 高（相同的初始化模式） |
| 功能互补性 | 高（配置管理 + 数据存储） |
| 实际协作 | 目前没有，但设计上应该协作 |

**建议：** 两个模块设计上应该是互补的，建议在未来的代码中同时使用这两个模块来实现完整的工作流。