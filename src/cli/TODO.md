# TODO

## 需人确认

- [ ] **#8** fusion-check 引用文件 `《量潮数据项目岗位权责章程》` 不存在

## 已完成

### v0.0.5
- [x] 模型升级：`dataclasses` → `pydantic.BaseModel`，字段使用 `quanttide` v0.1.1 类型注释

### v0.0.4
- [x] CLI 改用 `typer`，自动 `--help` / `--show-completion`
- [x] `Settings` 新增 `sample_home`（`QTCLOUD_KNOWL_SAMPLE_HOME`）
- [x] 清理 CLI 参数：移除 `data_dir`、`sample_dir` 位置参数
- [x] 移除 `config.SAMPLE_DIR`，`config.py` 只保留 `Settings`
- [x] 新增文档测试（CLI help、storage.md env var 校验、doctest）

### v0.0.3 / 基础设施
- [x] **#7** fusion-check "交接" 重叠 — 确认合法跨领域重叠
- [x] **#9** `config.py` 改用 `quanttide.LocalStorage`
- [x] **#10** 环境变量统一为 `QTCLOUD_KNOWL_DATA_HOME`
