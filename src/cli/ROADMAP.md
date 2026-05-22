# ROADMAP

每个版本交付的不是功能，是用户能力。

## 下一阶段：v0.2.0 审计模块收尾

完成 TODO.md 中 v0.2.0 的四项剩余工作：
- parser 分离格式解析/分类规则/展示构造
- `AuditIssue` 携带原始证据
- `ReportRepository` 完整持久化
- `AuditRule` / `AuditRuleSet` 统一建模

## v0.3.0 — World 层级 + 多文件合并抽取

**层级扩展**：domain 上级增加 world（世界观），用于区分现实与虚构世界：

```
World（世界观）
  └── Domain（领域）
       ├── Ontology（本体）
       └── Instance（实例）
```

例如：
- world: `reality` → domain: `公司治理`、`岗位职责`
- world: `fiction-romance` → domain: `职场言情`、`校园言情`

**核心矛盾**：`qtcloud-knowl extract` 是按文件抽取的，每文件一 domain。但知识库是按故事系列组织的（夜市约会、深夜失眠、书房陪伴等），不是按文件。工具没有"合并多文件到同一个 domain"、也没有"按 world 组织 domain"的能力。

domain 不再直接归属知识库根目录，而是归属到对应的 world 目录下。
extract 需要支持 `--world` 参数指定世界观归属。

**方案 A：工具侧合并**

改进 extract 的抽取逻辑，让它能识别同一故事的多文件并合并到同一个 domain。例如：
- 利用源目录名作为 domain 分组 hint（已实现，效果有限）
- 后处理合并：文件级 LLM 调用完成后，按 domain 相似度合并
- 批处理：多文件合并后一次性发给 LLM（受限于上下文长度）

**方案 B：工作流侧分工（推荐）**

用户手动写好 domain 定义，extract 只做实例抽取。更符合 OCL 方法论的"人定义概念，AI 填充实例"：
- 用户在知识库目录下预置 `domain.json`、`ontologies.json`
- `extract` 读取已有 domain/ontology 结构，LLM 只填充 instances
- 结果更可控，不产生冗余 domain

## 已完成

### v0.2.0 — 审计不可定制、不可追溯、不可复用（进行中）

> 对应审计模块的领域模型提取与架构重构

**痛点**：`audit.py` 是 300 行的单文件脚本，检测逻辑、分类规则、输出格式全部耦合在一起。加一种新检测工具要改四五个 if/else，换一种输出格式要复制整个函数，看不懂审计报告是怎么产生的。

**用户能力（已完成）**：
- 审计系统可扩展——加新检测工具只需新增一个 `run()` 函数加入 tools 列表，不改编排逻辑
- 审计可理解——`AuditMode`、`AuditIssue`、`KnowledgeBaseStats`、`ReportTemplate` 各自独立，改文案不改逻辑，改规则不改渲染
- 测试可覆盖——307 个测试，100% 行覆盖率

**架构产出**（6 个模块）：

```
app/audit/
├── models.py       # 领域类型
├── report.py       # Report 实体 + 渲染 + 持久化
├── service.py      # 编排
├── parser.py       # 工具输出 → 结构化数据
└── __init__.py     # 公共 API

tests/test_audit/   # 5 个测试文件
```

**剩余工作**（见 `TODO.md`）：
- parser 分离格式解析/分类规则/展示构造（消除与 service 的规则重复）
- `AuditIssue` 携带原始证据
- `ReportRepository` 完整持久化
- `AuditRule` / `AuditRuleSet` 统一建模

### v0.1.0 — 文档入库到发布不能一步走完

> 对应 OCL 阶段二至五全串联

**痛点**：抽取→草稿→审核→落库的每个环节都能单步执行，但缺少一条命令跑完全流程的工作流。

**用户能力**：一条命令完成从源文档到正式知识库的全流程，中途经 audit 自动质检。

发布版本见 [CHANGELOG.md](./CHANGELOG.md)。
