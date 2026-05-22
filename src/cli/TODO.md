# TODO

未来规划见 [ROADMAP.md](ROADMAP.md)。

## v0.2.0 — audit 领域模型提取

将 `app/audit.py` 从单个模块重构为 `app/audit/` 包，提取领域模型。

### 目录转换

- [x] `app/audit/__init__.py` — 公开 `run()` + 导出领域类型，保持 `from app.audit import run` 兼容
- [x] `app/audit/models.py` — `AuditMode`, `IssueCategory`, `AuditIssue`, `AuditDiff`, `AuditReport`, `AuditState`
- [x] `app/audit/repository.py` — `AuditStateRepository`（JSON 持久化，注入 state_home Path）
- [x] `app/audit/parser.py` — `ToolOutputParser` + 5 个 IssueParser 策略（MISS/FAIL/TERM/CONFIRM/ABSTRACTION）
- [x] `app/audit/report.py` — `print_stats`, `print_report`, `print_diff`（展示层，接收领域对象）
- [x] 删除 `app/audit.py`

### 测试迁移

- [x] `tests/test_audit/test_models.py` — AuditMode/AuditIssue/AuditDiff/AuditReport 纯逻辑
- [x] `tests/test_audit/test_repository.py` — AuditStateRepository 持久化
- [x] `tests/test_audit/test_parser.py` — ToolOutputParser 解析策略链
- [x] `tests/test_audit/test_integration.py` — run() 编排集成测试（原 TestAudit/TestAuditUnit 等）
- [x] 删除 `tests/test_audit.py`
- [x] 验证 100% 覆盖率不变

### 原则

- 不破坏 `from app.audit import run` 接口
- 不破坏测试覆盖率
- domain 逻辑纯度优先：models/parser/repository 不打印、不依赖 settings
- 展示层隔离：report.py 只做格式化输出

## v0.2.1 — report.py 展示层重构

`app/audit/report.py` 的三个设计问题及其修复方案。

### 问题1: `print_stats` 参数散装 — 提取 KnowledgeBaseStats

- . [x] `app/audit/models.py` — 新增 `KnowledgeBaseStats` dataclass（domains, ontology_count, instance_count）
- . [x] `app/audit/__init__.py` — `_collect_stats` 改为返回 `KnowledgeBaseStats` 而非散装 tuple
- . [x] `app/audit/report.py` — `print_stats` 改为接收 `KnowledgeBaseStats` 对象
- . [x] 更新 `test_models.py` — 测试 KnowledgeBaseStats
- . [x] 更新 `test_integration.py` — 适配 _collect_stats / print_stats 新签名

### 问题2: `_print_section` 数据结构不匹配 — 修复 group → issues 映射

- . [x] `app/audit/models.py` — 新增 `IssueGroup` dataclass（group_name: str, issues: list[AuditIssue]）
- . [x] `app/audit/__init__.py` — `_categorize_issues` 返回 `list[IssueGroup]` 而非散装三层列表
- . [x] `app/audit/report.py` — `_print_section` 接收 `list[IssueGroup]`，移除 `[issue]` 包装
- . [x] `app/audit/models.py` — `AuditReport.from_raw` 重构为持 `IssueGroup` 结构
- . [x] 更新测试

### 问题3: `print_report` 渲染与决策耦合 — 提取 ReportTemplate

- . [x] `app/audit/models.py` 或新建 `app/audit/template.py` — 定义 `ReportTemplate` dataclass（section_order, header_map per mode, summary_text）
- . [x] `app/audit/report.py` — `print_report` 改为读取 `ReportTemplate` 决定标题和顺序，自身只做渲染
- . [x] 更新测试验证：切换 template 可改变输出文案而不改渲染逻辑

### 收尾

- . [x] 验证 100% 覆盖率不受影响
- . [x] 确认 `from app.audit import run` 接口不变
