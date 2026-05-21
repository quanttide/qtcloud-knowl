# 配置参考

## 环境变量

| 环境变量 | 说明 | 默认值 |
|----------|------|--------|
| `QTCLOUD_KNOWL_DATA_HOME` | 知识库数据目录 | `~/.local/share/qtcloud-knowl/` |
| `QTCLOUD_KNOWL_STATE_HOME` | 审计状态文件目录（增量对比用） | `~/.local/state/qtcloud-knowl/` |
| `QTCLOUD_KNOWL_LLM_API_KEY` | LLM API key（extract 需要） | 空，可通过 Vault 配置 |
| `QTCLOUD_KNOWL_LLM_MODEL` | LLM 模型名 | `deepseek-chat` |
| `QTCLOUD_KNOWL_LLM_BASE_URL` | LLM API 地址 | 空（使用模型默认） |

## LLM 配置优先级

1. 环境变量 `QTCLOUD_KNOWL_LLM_API_KEY`
2. Vault 路径 `quanttide/deepseek`，密钥 `api_key`
3. 两者都未配置时 extract 报错

## 审计模式

| 模式 | 说明 |
|------|------|
| `--mode full`（默认） | 全面审计：概览统计 + 全部检测项 |
| `--mode simple` | 快速检查：只统计概览，跳过部分检测 |
