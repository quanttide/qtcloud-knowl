# ROADMAP

## ✅ 已完成 (2026-05-20)

### 修复检测精度

- [x] find-undefined-terms 对模板术语（`第X条 定义`）的误报过滤
  - 扩展 `IGNORED_CHAPTER_RE` 覆盖中文数字、阿拉伯数字、`第X` 占位符
  - 新增 `术语名称` 到忽略列表
- [x] fusion-check 中 "交接" 跨领域重叠需人确认
  - 新增 `HUMAN_CONFIRM_TERMS`，输出标记 `【需人确认】`
- [x] fusion-check 中 qtdata-index.md 引用断裂需人确认
  - 新增 `HUMAN_CONFIRM_REFS`，输出标记 `【需人确认】`

### 增强测试

- [x] 现有测试仅验证返回值，未验证输出内容
  - 用 `capsys` 捕获 stdout，校验输出内容
- [x] 为每个检测模块补充正例和反例断言
  - 30 个测试（从 5 扩至 30），含异常路径和边缘用例

### 数据目录可配置化

- [x] `config.py` 中 DATA_DIR 硬编码为 tests/fixtures/output，安装后无法使用
- [x] 方案：读取 `KNOWL_DATA_DIR` 环境变量，fallback 到 `~/.local/share/qtcloud-knowl`
- [x] 附带修复 4 个模块中 `data_dir` 字符串→`Path` 转换缺失的 bug

## ✅ 已修复 (2026-05-20)

### 🔴 严重

- [x] `reviewers/__init__.py` `run_detection` 引用 `src.validators.*` → 改为 `app.validators.*`

### 🟡 中

- [x] `cli.py` 帮助信息 `python -m src.cli` → `kcli`
- [x] `detect_domain.py` `main()` 新增 `--data-dir` 参数并传给 `run()`
- [x] 缺少 `KNOWL_DATA_DIR` 环境变量的测试覆盖 → 已有 `test_config.py`

### 🟢 低

- [x] `auto_fix.py` 移除未使用的 `sample_dir` 参数

## 🧑 需人确认（未变更）

- fusion-check "交接" 跨领域重叠
- fusion-check qtdata-index.md 引用 `《量潮数据项目岗位权责章程》` 文件不存在
