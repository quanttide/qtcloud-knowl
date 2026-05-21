# 教程：从源文档到知识库

以一个公司治理章程为例，走通从文档到可审计知识库的完整流程。

## 前提

```bash
pip install qtcloud-knowl-cli
```

后续命令默认数据存储在 `~/.local/share/quanttide/qtcloud-knowl/`，通过 `QTCLOUD_KNOWL_DATA_HOME` 可自定义。

## 第一步：下载源文档

知识库的原材料是 Markdown 文档。CLI 内置了三个公开章程仓库：

```bash
# 查看可下载的源文档
qtcloud-knowl source list

# 下载量潮科技工作章程
qtcloud-knowl source download --name qtcloud-bylaw
```

下载后的文档保存在 `source_home`（默认 `data_home/sources/`），后续 `extract` 命令从这里读取。

> 验证：[test_source.py](../integrated_tests/test_source.py) 验证了空目录下 `source list` 不崩溃。

## 第二步：抽取骨架

```bash
qtcloud-knowl extract
```

extract 扫描源文档目录中的所有 `.md` 文件，做两件事：

1. **创建领域目录** — 按内容匹配已有领域的 vocabulary，推荐文档归属
2. **生成骨架文件** — 每个领域下创建 `domain.json`、`ontologies.json`、`instances.json`、`relations.json`

输出示例：

```
抽取完成。新增 4 个领域，共收录 8 份文档。骨架文件已保存到 ~/.local/share/quanttide/qtcloud-knowl/。
```

第一次运行完可以加 `--verbose` 查看每个文档匹配到哪个领域。

> 验证：[test_extract.py](../integrated_tests/test_extract.py) 验证了从 fixtures/input/ 的 10 份 Markdown 创建骨架成功。

## 第三步：评审条目

骨架创建后，所有本体和实例处于"待评审"状态。你需要确认它们是否准确：

```bash
# 查看所有待评审条目
qtcloud-knowl review list --pending

# 通过指定条目
qtcloud-knowl review approve --id org-gov:ontology:role-responsibility

# 拒绝指定条目（可附原因）
qtcloud-knowl review reject --id org-gov:ontology:role-responsibility --reason "抽象层级不够，需拆分"

# 全部通过（确认骨架质量后使用）
qtcloud-knowl review approve
```

评审状态保存在知识库目录的 `review.json` 中，后续 audit 会参考评审结果。

> 验证：[test_main.py](../integrated_tests/test_main.py) 验证了 audit → review approve → 二次 audit 的三模块串联不崩溃。

## 第四步：审计质量

```bash
qtcloud-knowl audit
```

audit 对知识库执行 5 项检测，按三组输出报告：

| 分组 | 含义 | 常见问题 |
|------|------|---------|
| **需要你确认** | 平台无法自动判断 | 引用断裂、术语冲突 |
| **平台发现** | 结构性问题，可自动修复 | 骨架文件缺失、JSON 格式错误 |
| **建议关注** | 优化建议 | 本体抽象度不足、跨领域关系缺失 |

输出示例：

```
============================================================
  知识库质量审计报告（全面审计模式）
============================================================
审计目标: /home/user/.local/share/quanttide/qtcloud-knowl/
领域数量: 4

━━━ 需要你确认的问题 ━━━
  名称冲突或引用断裂
    • qtdata-index.md: 引用 "《量潮数据项目岗位权责章程》" 但无法匹配到已知文件
    → 确认该引用是否必要

━━━ 平台发现的问题 ━━━
  文件结构问题
    • 缺少文件 domain.json
    → 运行 qtcloud-knowl auto-fix 自动补全
```

**增量对比**：第二次运行 audit，会与上次审计结果做 diff，显示修复、新增、待处理各多少项：

```
相比上次审计（2026-05-21）：✅ 已修复 1 项 / ⏳ 待处理 4 项
```

> 验证：[test_main.py](../integrated_tests/test_main.py) 验证了两次 audit 的增量对比输出。

### 快速检查模式

```bash
qtcloud-knowl audit --mode simple
```

只验证结构完整性，跳过质量检测和意识检查。适合日常快速巡检。

> 验证：[test_main.py](../integrated_tests/test_main.py) 验证了无 LLM key 时 audit --mode simple 不崩溃。

## 第五步：修复问题

### 自动修复

```bash
qtcloud-knowl auto-fix
```

补全缺失的骨架文件，修复 `domain.json`、`ontologies.json`、`instances.json`、`relations.json` 的结构问题。

### 手动修复后验证

```bash
# 修复问题后再次审计，确认已修复
qtcloud-knowl audit
```

如果上一步评审了条目，这次审计会显示 ✅ 已修复 N 项。

## 完整流程

从零开始的全流程命令：

```bash
# 1. 下载源文档
qtcloud-knowl source download --name qtcloud-bylaw

# 2. 抽取骨架
qtcloud-knowl extract

# 3. 查看待评审条目
qtcloud-knowl review list --pending

# 4. 确认骨架无误后全部通过
qtcloud-knowl review approve

# 5. 首次审计
qtcloud-knowl audit

# 6. 修复问题
qtcloud-knowl auto-fix

# 7. 二次审计，确认修复
qtcloud-knowl audit
```

## 集成测试验证

每个核心步骤都有对应的集成测试验证模块协作：

| 步骤 | 集成测试 | 验证内容 |
|------|---------|---------|
| source list | `test_source.py`（单元测试） | 空目录不崩溃 |
| extract | `test_extract.py` | 从 10 份 Markdown 创建骨架 |
| audit | `test_audit.py` | 审计 4 个领域输出审计目标 |
| 全链路 | `test_main.py` | extract → audit、增量对比、approve → audit、无 key 全流程 |

完整测试列表见 [integrated_tests/README.md](../integrated_tests/README.md)。
