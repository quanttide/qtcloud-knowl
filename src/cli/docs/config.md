# 配置参考

## 环境变量

| 环境变量 | 说明 | 默认值 |
|----------|------|--------|
| `QTCLOUD_KNOWL_DATA_HOME` | 知识库数据目录 | `~/.local/share/quanttide/qtcloud-knowl/` |
| `QTCLOUD_KNOWL_STATE_HOME` | 审计状态文件目录（增量对比用） | `~/.local/state/quanttide/qtcloud-knowl/` |
| `QTCLOUD_KNOWL_SAMPLE_HOME` | 源文档目录 | 无 |
| `QTCLOUD_KNOWL_LLM_API_KEY` | LLM API key（extract 需要） | 空 |

## 审计模式

| 模式 | 说明 |
|------|------|
| `--mode full`（默认） | 全面审计：执行全部 5 项检测，含质量检查 |
| `--mode simple` | 快速检查：只验证结构完整性，跳过质量检测 |
