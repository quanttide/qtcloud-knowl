# TODO

## 需人确认

- [ ] **#8** fusion-check 引用文件 `《量潮数据项目岗位权责章程》` 不存在 — `app/validators/fusion_check.py:183`

## 代码重构

- [ ] **CLI** 顶层从手动 `sys.argv` 分发改用 `typer`，支持 `--help` / `--version`
- [ ] **环境变量** 统一为 `_DIR` 后缀：`quanttide` SDK 的 `_HOME` → `_DIR`，确保与 `Settings` 一致
- [ ] **帮助信息** `app/cli.py:6` 的 `python -m src.cli` → `qtcloud-knowl`

## 已完成

- [x] **#7** fusion-check "交接" 重叠 — 确认合法跨领域重叠
- [x] **#9** `config.py` 改用 `quanttide.LocalStorage`
- [x] **#10** 环境变量统一为 `QTCLOUD_KNOWL_DATA_DIR`
