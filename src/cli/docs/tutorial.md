# 教程：从源文档到知识库

以一个公司治理章程为例，走通 `extract --source` 的完整流程。

## 前提

```bash
pip install qtcloud-knowl-cli
```

默认数据存储在 `~/.local/share/qtcloud-knowl/`，通过 `QTCLOUD_KNOWL_DATA_HOME` 可自定义。

LLM API key 可通过环境变量或 Vault 配置。未配置时 extract 会报错。

## 第一步：准备源文档

在本地创建或准备好一批 Markdown 文档。例如：

```bash
mkdir -p /tmp/my-docs

cat > /tmp/my-docs/company-rules.md << 'EOF'
# 公司管理制度

第一条 总经理负责公司全面工作，行使以下职权：
（一）组织实施董事会决议；
（二）制定公司管理制度。

第二条 董事会会议每季度召开一次，由董事长召集。
董事会决议须经三分之二以上董事通过。
EOF
```

## 第二步：抽取知识

```bash
qtcloud-knowl extract --source /tmp/my-docs --verbose
```

extract 逐文件调用 LLM，从文档中识别并生成四类知识条目：

| 条目类型 | 含义 | 示例 |
|---------|------|------|
| Domain | 领域 | 公司治理 |
| Ontology | 本体 | 岗位职责、议事规则 |
| Instance | 实例 | 总经理（岗位职责的实例） |
| Relation | 关系 | 总经理→董事会会议（参与关系） |

输出示例：

```
抽取完成。生成 1 个领域知识库，保存至 ~/.local/share/qtcloud-knowl。
  本体: 3 项
  实例: 5 项
  关系: 4 项
```

## 第三步：查看结果

生成的知识库目录结构：

```
~/.local/share/quanttide/qtcloud-knowl
└── <domain-id>/
    ├── domain.json         # 领域定义
    ├── ontologies.json     # 本体列表
    ├── instances.json      # 实例列表
    └── relations.json      # 关系列表
```

每个条目四个字段：`id`、`name`、`label`、`description`。

## 第四步：质量审计

```bash
qtcloud-knowl audit
```

先统计知识库概览（领域数、本体数、实例数、关系数），再运行检测检查问题。

```
============================================================
  知识库概览
============================================================
  领域数量: 1
  本体数量: 3
  实例数量: 5
  关系数量: 4
```

## 完整流程

```bash
# 1. 创建源文档
mkdir -p /tmp/my-docs
cat > /tmp/my-docs/rules.md << 'EOF'
...文档内容...
EOF

# 2. 抽取知识
qtcloud-knowl extract --source /tmp/my-docs

# 3. 审计检查
qtcloud-knowl audit
```
