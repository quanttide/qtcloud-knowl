---
name: product-refactor
description: Refactoring patterns for cross-consumer reuse — extract shared models/loaders so CLI and provider share one source of truth
---

# Product Refactor Skill

重构经验总结，来自 `qtcloud-knowl` SDK 包的实践。

核心原则：**模型和加载逻辑不是 CLI 的私有财产，是 CLI 和 provider 的共享地基。** 所有消费者（CLI、provider、测试工具）应依赖同一套 `packages/<lang>/` SDK 包，而不是各自维护副本。

## 何时抽取共享包

当出现以下信号时，应将代码抽取为独立包：

- 同一套模型定义在 2+ 个消费者中重复（如 CLI 的 `app/models.py` vs provider 的 `models.py`）
- 同一套加载逻辑在 3+ 个地方重复（CLI loader + provider loader + 第三套绕过逻辑）
- 重复副本之间存在细微差异（如 `Instance.data` 一个用 `{}` 一个用 `Field(default_factory=dict)`）
- 重复副本之一已修复 bug，另一份未修复
- 新消费者（provider、测试工具等）需要同一套数据结构

## 设计包的原则

1. **框架无关**：模型只依赖 `pydantic`，不依赖 typer/click/settings/django/flask 等框架
2. **字段类型一致性**：同一个语义的字段（pattern、detail、id）在所有模型中使用同一种类型，不因消费者不同而放宽/收紧
3. **Mutable default 不可接受**：`data: dict = {}` 必须改为 `data: dict = Field(default_factory=dict)`
4. **包不设默认路径**：数据目录由调用者传入，包不硬编码 XDG、环境变量或配置文件
5. **消费者自带适配层**：如果消费者需要 dict 格式而非 Pydantic 模型，在消费者侧做适配转换，不在 SDK 中加

## 重构操作流程

```
1. 审计所有导入者（grep -r "from app.loader" / "from app.models"）
2. 检查数据格式兼容性
   ├── 调用者期望 dict 还是 Pydantic 模型？
   ├── 是否有 flat dict 包装了嵌套 data 字段的需求？
   └── 在适配层（如 data.py）用 _flatten() 做格式转换
3. 先安装再测试
   ├── pip install -e packages/python/
   ├── 跑全部测试确保没有 import 错误
   └── 修正测试中的 import 路径
4. 删除冗余文件
5. 更新版本号和依赖声明
```

## 常见陷阱

| 陷阱 | 案例 | 解决 |
|------|------|------|
| 实例 JSON 中领域特有字段（authority、rule）在顶层而非 data dict | reviewers 期望 `inst["authority"]`，SDK 放入 `inst.data["authority"]` | 在适配层用 `_flatten()` 把 `data` 合并回顶层 |
| 测试 import 路径未更新 | `test_loader.py` 仍用 `from app.loader import ...` | 全局 grep import 路径，逐个修改 |
| 三方包的版本号未对齐 | SDK `0.1.0` 而主项目 `v0.0.11` | 统一版本号风格 |

## 经验法则

- **接口不变原则**：重构时尽量不改变调用者代码。如果调用者用 `inst["key"]`，保持返回 dict；如果用 `inst.key`，保持返回模型
- **边界转换**：在适配层（如 `data.py`）做格式转换，而不是在 SDK 或调用者中做
- **一个边界不跨两层**：`data.py` 做了一层 dict 转换，reviewers 就无需改动
- **先删冗余再改逻辑**：删除重复文件迫使 import 错误暴露，避免遗漏
