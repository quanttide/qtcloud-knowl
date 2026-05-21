# 命令参考

## extract

```
qtcloud-knowl extract --source <目录> [--data-dir <目录>] [--verbose]
```

从本地 Markdown 文档提取知识，全程 LLM 驱动。逐文件调用大模型，自动识别并生成四类知识条目。

### 参数

| 选项 | 说明 |
|------|------|
| `--source` `-s` | 源文档目录路径（必填） |
| `--data-dir` | 知识库输出目录（默认 `QTCLOUD_KNOWL_DATA_HOME`） |
| `--verbose` `-v` | 显示抽取详情 |

### 输出

```
抽取完成。生成 1 个领域知识库，保存至 ~/.local/share/qtcloud-knowl。
  本体: 3 项
  实例: 5 项
  关系: 4 项
```

### 生成的文件结构

```
<data-dir>/
└── <domain-id>/
    ├── domain.json         # 领域定义
    ├── ontologies.json     # 本体列表
    ├── instances.json      # 实例列表
    └── relations.json      # 关系列表
```

每个条目统一四个字段：`id`、`name`、`label`、`description`。`description` 可包含结构化内容（如"职责：xxx；权限：xxx"）。

### 前置条件

- 需要配置 LLM API key（通过 `QTCLOUD_KNOWL_LLM_API_KEY` 环境变量或 Vault）
- 默认使用 DeepSeek，可通过 `QTCLOUD_KNOWL_LLM_MODEL` 和 `QTCLOUD_KNOWL_LLM_BASE_URL` 切换

## audit

```
qtcloud-knowl audit [<data-dir>] [--mode simple|full] [--sample-dir <目录>]
```

审计知识库完整性。先统计概览（领域/本体/实例/关系数量），再运行检测。

### 参数

| 选项 | 说明 |
|------|------|
| `data-dir` | 知识库目录（默认 `QTCLOUD_KNOWL_DATA_HOME`） |
| `--mode` | `simple`（快速）/ `full`（全面，默认） |
| `--sample-dir` | 源文件目录（部分检测需要） |

### 输出

```
============================================================
  知识库概览
============================================================

  数据目录: ~/.local/share/qtcloud-knowl
  领域数量: 1
  本体数量: 3
  实例数量: 5
  关系数量: 4

  领域清单:
    company_governance   公司治理       vocabulary=0 项

============================================================
  检测结果
============================================================
```
