# TODO

## 需人确认

- [ ] **#8** fusion-check 引用文件 `《量潮数据项目岗位权责章程》` 不存在

## 已完成

### v0.0.4
- [x] CLI 改用 `typer`，自动 `--help` / `--show-completion`
- [x] 模型升级：`dataclasses` → `pydantic.BaseModel`
- [x] `Settings` 新增 `sample_home`（`QTCLOUD_KNOWL_SAMPLE_HOME`）
- [x] 清理 CLI 参数：移除 `data_dir`、`sample_dir` 位置参数
- [x] 移除 `config.SAMPLE_DIR`，`config.py` 只保留 `Settings`
- [x] 新增文档测试（CLI help、storage.md env var 校验、doctest）

### 基础设施
- [x] `config.py` 改用 `quanttide.LocalStorage`
- [x] 环境变量统一为 `QTCLOUD_KNOWL_DATA_HOME`（XDG `_HOME` 风格）
- [x] 修复帮助信息 `python -m src.cli` → `qtcloud-knowl`
