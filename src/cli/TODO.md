# TODO

未来规划见 [ROADMAP.md](ROADMAP.md)。

## v0.2.0 — audit 领域模型提取（进行中）

### ✅ 已完成

**基础架构**（6 个模块，307 测试，100% 覆盖率）：

- [x] `app/audit/__init__.py` — 公共 API 门面
- [x] `app/audit/models.py` — `AuditMode`, `AuditIssue`, `AuditDiff`, `AuditReport`, `KnowledgeBaseStats`, `Report`
- [x] `app/audit/service.py` — `run()` 编排
- [x] `app/audit/parser.py` — `ToolOutputParser`
- [x] `app/audit/report.py` — `Report` 实体 + 渲染 + `ReportRepository`
- [x] 删除 `app/audit.py`、`app/audit/repository.py`、`app/audit/renderer.py`
- [x] `tests/test_audit/` — 5 个测试文件

**设计改进**：

- [x] `KnowledgeBaseStats` — `print_stats` 从 4 个散装参数改为一个对象
- [x] `IssueGroup` — `_print_section` 修复数据结构不匹配
- [x] `ReportTemplate` — `print_report` 渲染/决策解耦
- [x] `Report` 领域模型 — 替代 `AuditState`，合并渲染 + 仓储
- [x] `service.py` — 编排从 `__init__.py` 分离
- [x] 展示模型与领域模型分离（`ReportSectionDef`/`ReportTemplate` 留在 `report.py`）

### 🔲 待完成

#### 1. parser 重构 — 分离格式解析、分类规则、展示构造

`parser.py` 同时做了三件事：格式解析（识别 `[MISS]`）、分类决策（MISS → auto_fixable）、展示构造（中文 label/action）。与 `_categorize_issues` 的分类逻辑重复。

- [ ] `app/audit/parser.py` — `_parse_*` 改为只返回结构化数据 `{tag, detail, domain}`，不分配 category/group/label/action
- [ ] `app/audit/models.py` — 新增 `RawMatch` dataclass 作为 parser 输出类型
- [ ] `app/audit/service.py` — `_categorize_issues` 接管分类决策，消除与 parser 的规则重复
- [ ] `app/audit/report.py` — label/action 字符串构造移入 report 模块
- [ ] 更新测试

#### 2. 审计证据 — AuditIssue 携带原始证据

- [ ] `app/audit/models.py` — `AuditIssue` 新增 `evidence: str = ""` 字段
- [ ] `app/audit/parser.py` — 各 `_parse_*` 传入匹配到的原始行
- [ ] `app/audit/report.py` — `_print_group` 支持 `--verbose` 输出 evidence
- [ ] 更新测试

#### 3. 审计报告完整持久化 — ReportRepository 保存完整 Report

- [ ] `app/audit/report.py` — `save_report()` 保存完整 Report（含 stats、issues、diff）
- [ ] `app/audit/report.py` — `load_previous_state()` 升级为 `load_report()`，返回完整 Report
- [ ] `app/audit/report.py` — `to_dict()` / `from_dict()` 序列化方法
- [ ] 移除 `_PreviousAudit` helper
- [ ] 更新测试

#### 4. 审计规则 — AuditRule 模型

- [ ] `app/audit/rules.py` — `AuditRule` 实体（id, name, tool, category, condition, action, severity）
- [ ] `app/audit/rules.py` — `AuditRuleSet` 聚合（version, rules list）
- [ ] `app/audit/service.py` — `_categorize_issues` 改为读取 `AuditRuleSet`
- [ ] `app/audit/report.py` — `DEFAULT_REPORT_TEMPLATE` 可被规则集驱动
- [ ] 更新测试
