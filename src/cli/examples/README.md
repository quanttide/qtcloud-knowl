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
# 下载所有示例
./examples/setup.sh

# 对示例运行抽取（当前 extract 只扫描目录下的 .md 文件，不递归子目录）
# 可指向具体子目录作为源文档目录
qtcloud-knowl extract ./examples/qtcloud-bylaw-of-business-entity/audit

# 或复制到平面目录：
# mkdir -p /tmp/samples && find ./examples -name '*.md' -exec cp {} /tmp/samples \;
# qtcloud-knowl extract /tmp/samples

# 运行审计
qtcloud-knowl audit --data-dir ./examples/qtcloud-bylaw-of-business-entity/kbase
```
