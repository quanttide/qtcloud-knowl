# 知识工程智能体 — 状态报告

最近一次检查：2026-05-21

## 验收结果

### 数据质量

| 检查项 | 结果 | 数据 |
|:------|:----|:----|
| 结构完整性 | ✅ 通过 | 4 领域 × 4 JSON，全部合法 |
| 本体抽象度 | ✅ 14/14 通过 | 无未抽象信号 |
| 实例覆盖率 | ✅ 全部达标 | 每本体 ≥3 实例 |
| 跨域关系 | ✅ 8 条，每领域 ≥2 | 全部达标 |

### 工具链

| 检查项 | 结果 |
|:------|:----|
| CLI 入口 | ✅ `audit`（增量对比 + 业务语言报告）、`extract`（一句话摘要 + --verbose） |
| 审计模式 | ✅ `--mode simple`（快速）/ `--mode full`（全面） |
| 底层 API | ✅ 9 命令隐藏，内部可调用 |
| 测试 | ✅ 151 通过，覆盖率 77% |

### 文档一致性

| 文档 | 状态 |
|:----|:----|
| `AGENTS.md` | ✅ |
| `CHANGELOG.md` | ✅ |
| `CONTRIBUTING.md` | ✅ |
| `README.md` | ✅ |
| `ROADMAP.md` | ✅（PM 视角重写） |
| `STATUS.md` | ✅ 本文件 |
| `docs/index.md` | ✅（合并业务+技术） |
| `../../docs/contract.md` | ✅（顶层文档） |
| `../../docs/criteria.md` | ✅（顶层文档） |
| `../../docs/storage.md` | ✅（顶层文档） |
| `../../docs/workflow.md` | ✅（顶层文档） |

## 用户视角体验记录

2026-05-21 以首次使用者身份走了一遍完整流程。

### 顺利的

- `--help` 只显示 2 个命令，清晰
- `audit --help` 展开显示 `--mode` 和 `--sample-dir`
- audit 报告分组清晰，diff 增量对比正常工作
- extract 一句话摘要干净
- `--mode simple` 对新手友好

### 不顺利的

1. **data_home 设成无效路径时崩溃** — `QTCLOUD_KNOWL_DATA_HOME=/nonexistent` 在 import 阶段报 `PermissionError` traceback。应该拦截并提示"请确认 QTCLOUD_KNOWL_DATA_HOME 环境变量"。
2. **env var 置空串不 fallback 到默认值** — `QTCLOUD_KNOWL_DATA_HOME=""` 会被 pydantic 解析为 Path("") 即当前目录 `.`，导致 audit 在任意目录下都能跑但无意义。应加校验。
3. **diff 跨模式不一致** — 先跑 `--mode full` 存了状态，再跑 `--mode simple` 后 diff 显示"已修复 1 项"，但实际问题只是被 simple 模式过滤了，没有真修。diff 应按 mode 隔离。
4. **enc extract 输出的 init_domain 噪音** — `--verbose` 模式下显示了"领域 xxx 初始化完成"等日志，这些是 init_domain 的内部消息，用户不需要看到。
5. **detect-domain 暴露技术细节** — 虽然命令已隐藏，但被发现了还是输出"命中 43 次（词汇表 21 词）"，业务用户看不懂。
6. **`audit --help` 中 `--mode` 说明用词不一致** — `simple（仅结构检查）/ full（含质量检测）`，括号一边中文一边英文。

### 改进建议

| 优先级 | 问题 | 建议 |
|--------|------|------|
| P0 | #1 无效路径崩溃 | 在 audit/extract 入口处校验路径，不在 import 阶段崩溃 |
| P1 | #3 diff 跨模式污染 | 状态按 mode 隔离存储 |
| P2 | #2 env var 空串不 fallback | Path 字段加校验：空串视为未设置 |
| P3 | #4 init_domain 噪音 | verbose 模式也过滤内部日志 |
| P4 | #6 帮助文字格式不一致 | 统一括号风格 |

## 文件结构

```
CHANGELOG.md           # 变更记录（事实源）
STATUS.md              # 本文件
TODO.md                # 待办
ROADMAP.md             # 路线图（PM 视角）
  docs/
    index.md             # CLI 参考（业务 + 技术）
app/
  agents/              # 新增：审计 + 抽取编排
  cli.py               # Typer 入口（2 公开 + 9 隐藏）
  detectors/           # 领域操作
  reporters/           # 报告生成
  validators/          # 验证检测
  reviewers/           # 交互式评审
```
