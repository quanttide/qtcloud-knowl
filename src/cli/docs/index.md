# qtcloud-knowl CLI 参考

## 这是什么

一个**知识工程助手**。从原始文档中自动抽取知识，构建结构化的知识库。

**知识抽取（extract）**：把本地 Markdown 文档发给 LLM，自动识别领域、本体、实例和关系，
生成可直接使用的知识库文件。

**质量审计（audit）**：检查知识库完整性，统计领域/本体/实例/关系数量，检测结构问题。

## 典型场景

| 你想做什么 | 怎么做 |
|-----------|--------|
| 从一批文档创建一个知识库 | `qtcloud-knowl extract --source ./docs` |
| 查看知识库的家底 | `qtcloud-knowl audit` |
| 判断知识库完整性 | `qtcloud-knowl audit --mode full` |

## 命令参考

详细命令说明见 [commands.md](commands.md)。

| 命令 | 说明 |
|------|------|
| `extract` | 从 Markdown 文档提取知识，生成知识库 |
| `audit` | 审计知识库，统计概览并检测问题 |

## 配置参考

详细配置说明见 [config.md](config.md)。

| 环境变量 | 说明 |
|----------|------|
| `QTCLOUD_KNOWL_DATA_HOME` | 知识库数据目录 |
| `QTCLOUD_KNOWL_SAMPLE_HOME` | 源文档目录 |
| `QTCLOUD_KNOWL_LLM_API_KEY` | LLM API key（extract 需要，也可通过 Vault 配置） |
