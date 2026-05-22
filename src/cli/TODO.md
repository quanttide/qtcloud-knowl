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

## v0.2.1 — report.py 展示层重构 ✅

三个代码设计问题已修复。

| 问题 | 方案 | 效果 |
|------|------|------|
| `print_stats` 4 个散装参数 | 提取 `KnowledgeBaseStats` dataclass | 调用方传递一个对象 |
| `_print_section` 收 `list[Issue]` 却按 group 遍历 | 改收 `list[IssueGroup]`，移除 `[issue]` 包装 | 数据结构和遍历匹配 |
| `print_report` 用 `if mode == "simple"` 硬编码标题文案 | 提取 `ReportTemplate`，`print_report` 遍历 `template.sections_for(mode)` | 换模板可改文案不改渲染 |

### 遗留问题（非阻塞，可后续考虑）

- [x] **展示模型混在领域模型文件** — `ReportSectionDef`、`ReportTemplate`、`DEFAULT_REPORT_TEMPLATE` 移入 `presentation.py`。`IssueGroup` 因 `AuditReport.section_groups()` 强耦合留在 `models.py`
- [ ] **AuditState 仍贫血** — 无 `add_issue()` 自动更新时间戳、无 `filter_by_category()`。当前无消费方需求
- [ ] **tool→category 映射在服务层** — `_categorize_issues` 中的 mapping dict 是领域规则（validate = auto_fixable），目前只有一个消费者。若出现第二个消费者则应收进模型
