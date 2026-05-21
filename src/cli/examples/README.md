# 示例项目

本目录存放 qtcloud-knowl CLI 的示例知识库项目。每个示例包含源文档和知识库输出，供测试和演示使用。

## 可用示例

| 项目 | 说明 | 源文档仓库 |
|------|------|-----------|
| `qtcloud-bylaw-of-business-entity` | 量潮科技工作章程，8 个领域，14 个 OCL 本体 | [GitHub](https://github.com/quanttide/quanttide-bylaw-of-business-entity) |
| `qtcloud-handbook-of-business-entity` | 量潮科技工作手册，公司经营操作指南 | [GitHub](https://github.com/quanttide/quanttide-handbook-of-business-entity) |
| `qtcloud-tutorial-of-business-entity` | 量潮科技工作教程，叙事风格教学文档 | [GitHub](https://github.com/quanttide/quanttide-tutorial-of-business-entity) |

## 使用方法

源文档和知识库数据应放在不同的目录，避免混淆。

```bash
# 下载所有示例
./examples/setup.sh

# 抽取：从源文档创建知识库骨架，输出到独立的存储目录
qtcloud-knowl extract ./examples/qtcloud-bylaw-of-business-entity \
    --data-dir ./examples/qtcloud-bylaw-of-business-entity/.knowl

# 审计：对知识库运行质量检测
qtcloud-knowl audit --data-dir ./examples/qtcloud-bylaw-of-business-entity/.knowl

# 评审：查看并批量确认知识条目
qtcloud-knowl review list --data-dir ./examples/qtcloud-bylaw-of-business-entity/.knowl
```

存储目录（`.knowl/`）会自动创建，包含 `domain.json`、`ontologies.json` 等知识库文件。
每次对同一存储目录运行命令会增量更新，不会覆盖已有数据。
