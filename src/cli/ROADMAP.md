# ROADMAP

每个版本解决一个用户痛点。

## v0.0.12 — 模型与加载逻辑在 CLI/SDK 间重复维护

**痛点**：`app/models.py`、`app/loader.py`、`app/reviewers/data.py` 三套重复的模型/加载逻辑需要分别维护，导致类型不一致（`Instance.data` 可变默认值 bug）和代码膨胀。

**解决**：CLI 改为使用 `qtcloud-knowl` SDK 包（`packages/python/`）的模型和加载器，删除 `app/models.py` 和 `app/loader.py`，`reviewers/data.py` 改为底层调用 SDK。统一数据模型类型约束。

## v0.0.11 — 审计结果不可靠，环境变量配置不灵活

**痛点**：data_home 设成无效路径直接崩溃；diff 在 simple/full 模式间切换产生假阳性；env var 置空后行为异常。

**解决**：不在 import 阶段崩溃，改为命令入口处校验路径。diff 按审计模式隔离存储。env var 空串回退到默认值。

## v0.1.0 — 业务专家还不能自助完成全流程

**痛点**：从文档到正式知识库的链路有断裂。extract 能创建骨架，但本体/实例/关系仍需人工编写。

**解决**：接入 LLM 完成本体发现 → 实例映射 → 关系发现的完整语义抽取，输出标注"AI 生成"供人审核。配合 audit 做质量门禁，实现"文档入库 → 质检 → 发布"闭环。

---

所有已发布版本记录见 [CHANGELOG.md](./CHANGELOG.md)。
