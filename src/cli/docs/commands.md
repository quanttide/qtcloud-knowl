# 命令参考

## audit

```
audit [DATA_DIR] [--mode simple|full] [--sample-dir PATH]
```

全面检查知识库，按「需要你确认」「平台发现」「建议关注」三组输出报告。支持增量对比——二次运行会显示相比上次的变化。

关键行为：
- `--mode simple`：只检查结构完整性，跳过质量检测，问题降一级严重度
- `--mode full`（默认）：执行全部 5 项检测
- 首次运行无历史对比；二次起输出 `相比上次审计：✅ 已修复 N 项 / 🆕 新增 N 项 / ⏳ 待处理 N 项`

实际输出：

```text
============================================================
  知识库质量审计报告（全面审计模式）
============================================================
审计目标: ~/.local/share/quanttide/qtcloud-knowl/
领域数量: 4
相比上次审计（2026-05-21）：⏳ 待处理 1 项

━━━ 需要你确认的问题 ━━━
  名称冲突或引用断裂
    • qtdata-index.md: 引用 "《量潮数据项目岗位权责章程》" 但无法匹配到已知文件
    → 确认该引用是否必要，如必要则补充源文件或删除引用
```

## extract

```
extract [SAMPLE_DIR] [--data-dir PATH] [--verbose]
```

从 Markdown 文档创建知识库骨架，按内容推荐所属领域。

关键行为：
- 无 LLM 也能用：只做骨架创建 + 词汇匹配
- 默认输出一句话摘要；加 `--verbose` 显示领域匹配详情
- 配置 `QTCLOUD_KNOWL_LLM_API_KEY` 后可启用语义抽取

实际输出：

```text
抽取完成。共收录 10 份文档。骨架文件已保存到 ~/.local/share/quanttide/qtcloud-knowl/。
```

## review

```
review list [--pending] [--domain NAME]
review approve [--id KEY]
review reject --id KEY [--reason TEXT]
review reset
```

评审知识条目，支持批量操作。替代旧的 TUI 评审工具。

关键行为：
- `list`：列出所有条目及评审状态，`--pending` 只显示待审项
- `approve`：不传 `--id` 时全部通过；传 `--id` 时通过指定项
- `reject`：需传 `--id` 和可选的 `--reason` 说明原因
- `reset`：清空所有评审记录
- 条目 ID 格式：`{领域}:{类型}:{ID}`（如 `biz-ops:ontology:role-responsibility`）

## 内部命令（不公开）

以下 9 个命令标记为 `hidden=True`，不出现在 `--help` 中，可通过 CliRunner 或直接 import 调用，供 `audit` 和 `extract` 内部编排：

`validate` `find-undefined-terms` `fusion-check` `check-abstraction` `auto-fix` `cross-domain-report` `summary` `detect-domain` `init-domain`
