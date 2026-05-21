# 示例项目

本目录存放 qtcloud-knowl CLI 的示例知识库项目。每个示例包含源文档和知识库输出，供测试和演示使用。

## 可用示例

| 项目 | 说明 | 源文档仓库 |
|------|------|-----------|
| `qtcloud-bylaw-of-business-entity` | 量潮科技工作章程，8 个领域，14 个 OCL 本体 | [GitHub](https://github.com/quanttide/quanttide-bylaw-of-business-entity) |
| `qtcloud-handbook-of-business-entity` | 量潮科技工作手册，公司经营操作指南 | [GitHub](https://github.com/quanttide/quanttide-handbook-of-business-entity) |
| `qtcloud-tutorial-of-business-entity` | 量潮科技工作教程，叙事风格教学文档 | [GitHub](https://github.com/quanttide/quanttide-tutorial-of-business-entity) |

## 使用方法

```bash
# 下载示例源文档
./examples/setup.sh

# 对示例运行抽取
qtcloud-knowl extract ./examples/qtcloud-bylaw-of-business-entity/samples

# 运行审计
qtcloud-knowl audit --data-dir ./examples/qtcloud-bylaw-of-business-entity/kbase
```
