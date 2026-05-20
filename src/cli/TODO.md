# TODO

源于 `ROADMAP.md` v0.0.4。

## 需人确认

- [ ] **#8** fusion-check 引用文件 `《量潮数据项目岗位权责章程》` 不存在

## v0.0.4

- [ ] **CLI 改用 `typer`** — 替换手动 `sys.argv`，获得 `--help` / `--version`
- [ ] **Settings 新增 `sample_home`** — `QTCLOUD_KNOWL_SAMPLE_HOME`，无默认 fallback
- [ ] **合并校验命令** — `find-undefined-terms`、`fusion-check`、`check-abstraction` 归入 `validate --{undefined,fusion,abstraction}`
- [ ] **清理 CLI 参数** — 移除所有 `data_dir`、`sample_dir` 位置参数，统读 `settings`
- [ ] **移除 `config.SAMPLE_DIR`** — `config.py` 只保留 `Settings`

## 已完成

- [x] **#7** fusion-check "交接" 重叠 — 确认合法跨领域重叠
- [x] **#9** `config.py` 改用 `quanttide.LocalStorage`
- [x] **#10** 环境变量统一为 `QTCLOUD_KNOWL_DATA_HOME`
