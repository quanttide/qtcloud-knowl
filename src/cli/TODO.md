# TODO

源于 `STATUS.md` 已知问题与 `ROADMAP.md` 规划。

## 需人确认

- [x] **#7** fusion-check "交接" 重叠 — ✅ 已确认（合法跨领域重叠）
- [ ] **#8** fusion-check 引用文件 `《量潮数据项目岗位权责章程》` 不存在 — `app/validators/fusion_check.py:183`

## 代码迁移

- [x] **#9** `config.py` 改用 `quanttide.LocalStorage` 实现跨平台路径解析
  - `pyproject.toml` 添加 `quanttide` 依赖
  - `config.py` fallback 改为 `LocalStorage("qtcloud-knowl", vendor="quanttide").data_dir`
  - 测试适配 mock 策略
- [x] **#10** 统一环境变量命名 — 标准化为 `QTCLOUD_KNOWL_DATA_DIR`（pydantic `BaseSettings`, `env_prefix="QTCLOUD_KNOWL_"`）
