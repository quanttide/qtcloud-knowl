# ROADMAP

## v0.0.3: 使用 `platformdirs` 正确实现跨平台路径

### 背景

`docs/storage.md` 已正确文档化三平台路径（含 `quanttide/` 命名空间），但 `config.py` 实际实现仅为 Linux 硬编码且缺少 `quanttide/` 前缀：

| 平台 | 文档承诺 | 当前实现 |
|------|---------|---------|
| Linux | `~/.local/share/quanttide/qtcloud-knowl/` | `~/.local/share/qtcloud-knowl`（缺 quanttide/） |
| macOS | `~/Library/Application Support/quanttide/qtcloud-knowl/` | ❌ Linux 硬编码 |
| Windows | `%APPDATA%/quanttide/qtcloud-knowl/` | ❌ Linux 硬编码 |

### 执行步骤

1. **添加依赖** — `pyproject.toml` 新增 `platformdirs`
2. **修改 `config.py`** — `KNOWL_DATA_DIR` 环境变量优先级不变；fallback 改为 `platformdirs.user_data_dir("qtcloud-knowl", "quanttide")`；移除 `Path.home()` 硬编码
3. **确认 `docs/storage.md`** — 路径表已正确，无需改动
4. **适配测试** — `test_data_dir_fallback` 改为 mock `platformdirs.user_data_dir` 或断言调用参数
