# TODO

源于 `STATUS.md` 已知问题与 `ROADMAP.md` 规划。

## 需人确认

- [ ] **#7** fusion-check "交接" 重叠 — `app/validators/fusion_check.py:182`
- [ ] **#8** fusion-check 引用文件 `《量潮数据项目岗位权责章程》` 不存在 — `app/validators/fusion_check.py:183`

## 代码迁移

- [ ] **#9** `config.py` 改用 `quanttide` / `platformdirs` 实现路径解析，而非手动 `Path.home()` 计算（参见 ROADMAP v0.0.3）
  - `pyproject.toml` 添加 `platformdirs` 依赖
  - `config.py` fallback 改为 `platformdirs.user_data_dir("qtcloud-knowl", "quanttide")`
  - 测试适配 mock 策略
- [ ] **#10** 统一环境变量命名：`KNOWL_DATA_DIR` / `{APP_NAME}_DATA_DIR` / `{APP}_DATA_HOME` 三套命名选其一
