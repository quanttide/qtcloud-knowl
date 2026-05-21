# 示例项目

本目录存放 qtcloud-knowl CLI 的示例知识库项目。每个示例包含源文档，供测试和演示使用。

## 安装 CLI

```bash
pip install qtcloud-knowl-cli
```

或从源码安装：

```bash
pip install -e /path/to/qtcloud-knowl/src/cli
```

安装后可用 `qtcloud-knowl --help` 查看所有命令。

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

# 抽取：从源文档创建知识库骨架（数据存到系统默认目录）
qtcloud-knowl extract ./examples/qtcloud-bylaw-of-business-entity

# 审计：对知识库运行质量检测
qtcloud-knowl audit
```

数据默认存储在 `~/.local/share/quanttide/qtcloud-knowl/`，对环境变量 `QTCLOUD_KNOWL_DATA_HOME` 可自定义。

```bash
# 删除下载的示例源文档
rm -rf ./examples/qtcloud-*
```
