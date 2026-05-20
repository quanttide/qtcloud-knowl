# ROADMAP

每个版本解决一个用户痛点。

## v0.0.12 — 模型与加载逻辑在 CLI/SDK 间重复维护

**痛点**：`app/models.py`、`app/loader.py`、`app/reviewers/data.py` 三套重复的模型/加载逻辑需要分别维护，导致类型不一致（`Instance.data` 可变默认值 bug）和代码膨胀。

**解决**：CLI 改为使用 `qtcloud-knowl` SDK 包（`packages/python/`）的模型和加载器，删除 `app/models.py` 和 `app/loader.py`，`reviewers/data.py` 改为底层调用 SDK。统一数据模型类型约束。

## v0.0.13 — AI 抽取结果缺少审核入口

**痛点**：v0.1.0 承诺 AI 生成的抽取结果"供人审核"，但 reviewers 当前只支持人工评审已有知识库，没有审核 AI 草稿的工作流。

**解决**：reviewers 新增"AI 草稿审核"模式，展示 AI 提取的候选本体/实例/关系，逐条接受/拒绝/修改后写入知识库。

## v0.0.14 — 不知道 LLM 抽出来效果怎么样

**痛点**：prompt 质量决定抽取质量，但不跑一次看不到效果。

**解决**：`app/prompts/` 放 prompt 模板，`extract --llm` 读取文档调用 LLM，输出原始结果到 stdout。

**用户能力**：能验证 prompt 效果，迭代 prompt。

## v0.0.15 — LLM 输出没法保存为结构化草稿

**痛点**：每次跑完只看到 stdout，不能保存结果反复对比。

**解决**：解析 LLM 输出为 Domain/Ontology/Instance/Relation 结构，保存到 `data_home / drafts/` 目录。

**用户能力**：能保存和对比多次抽取结果。

## v0.0.16 — 草稿审核后不能落库

**痛点**：草稿在 `drafts/` 里，审核入口（v0.0.13）能看到但不能写入正式知识库。

**解决**：审核工作流接入 drafts/，确认后写入 `data_home` 的 domain.json、ontologies.json、instances.json、relations.json。

**用户能力**：LLM 结果经审核转为正式知识库。

## v0.0.11 — 审计结果不可靠，环境变量配置不灵活

**痛点**：data_home 设成无效路径直接崩溃；diff 在 simple/full 模式间切换产生假阳性；env var 置空后行为异常。

**解决**：不在 import 阶段崩溃，改为命令入口处校验路径。diff 按审计模式隔离存储。env var 空串回退到默认值。

## v0.1.0 — 业务专家还不能自助完成全流程

**痛点**：从文档到正式知识库的链路有断裂。extract 能创建骨架，但本体/实例/关系仍需人工编写。

**解决**：设计 prompt 管线 + 结构化输出解析器 + 编排调用，完成本体发现 → 实例映射 → 关系发现的全自动语义抽取。经 v0.0.13 审核工作流确认后落库。配合 audit 做质量门禁，实现"文档入库 → 质检 → 发布"闭环。LLM 连接层由 `quanttide-agent` 提供；不强制复用现有 ReActAgent，可按需覆盖或重写。

---

所有已发布版本记录见 [CHANGELOG.md](./CHANGELOG.md)。
