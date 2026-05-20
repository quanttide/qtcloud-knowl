# ROADMAP

### 修复检测精度

- find-undefined-terms 对模板术语（`第X条 定义`）的误报过滤
- fusion-check 中 "交接" 跨领域重叠需人确认
- fusion-check 中 qtdata-index.md 引用断裂需人确认

### 增强测试

- 现有测试仅验证返回值，未验证输出内容
- 为每个检测模块补充正例和反例断言

### 数据目录可配置化

- `config.py` 中 DATA_DIR 硬编码为 tests/fixtures/output，安装后无法使用
- 方案：读取 `KNOWL_DATA_DIR` 环境变量，fallback 到 `~/.local/share/qtcloud-knowl`
- 各命令已接受可选 `data_dir` 参数，只需改 `config.py` 一个文件
