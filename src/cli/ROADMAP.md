# ROADMAP

## v0.0.3: 使用 `platformdirs` 升级本地数据路径

### 动机

当前 `config.py` 中 DATA_DIR 的回退路径为 `Path.home() / ".local" / "share" / "qtcloud-knowl"`，这是 Linux 硬编码，macOS/Windows 上不符合各自操作系统规范。

### 执行步骤

1. **添加依赖** — `pyproject.toml` 新增 `platformdirs`
2. **修改 `config.py`** — `KNOWL_DATA_DIR` 环境变量优先级不变；fallback 改为 `platformdirs.user_data_dir("qtcloud-knowl", "quanttide")`；移除 `Path.home()` 硬编码
3. **更新 `docs/storage.md`** — 确认路径表与实际一致（改为引用 `platformdirs` 文档）
4. **验证测试** — 已有 `test_data_dir_fallback` 需要适配新行为（mock `platformdirs` 或验证调用）
