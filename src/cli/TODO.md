# TODO

## 已发布

v0.0.5 → v0.0.14 全部完成，见 [CHANGELOG.md](CHANGELOG.md)。

## v0.0.15 — LLM 输出没法保存为结构化草稿

- [ ] 解析 LLM 输出为 Domain / Ontology / Instance / Relation 结构
- [ ] 保存到 `settings.data_home / drafts/ <domain>/` 目录
- [ ] 重复运行不覆盖，按时间戳生成版本
- [ ] `extract --list-drafts` 列出所有草稿
- [ ] `extract --show-draft <id>` 查看指定草稿
- [ ] 测试
- [ ] 更新 docs/commands.md

停止条件：多次运行 `extract --llm` 后，`--list-drafts` 能列出多个版本，`--show-draft` 能展示结构化内容。

## v0.0.16 — 草稿审核后不能落库

- [ ] review CLI 读取 `drafts/` 而非仅读取正式知识库
- [ ] 审核确认后写入正式知识库（domain.json / ontologies.json / instances.json / relations.json）
- [ ] 已落库的草稿标记为"已发布"
- [ ] 测试
- [ ] 更新 docs/commands.md

停止条件：从文档抽取 → 草稿保存 → 审核确认 → 落库的完整链路可走通。

## v0.1.0 — 业务专家还不能自助完成全流程

- [ ] prompt 管线编排：三个 prompt 串联执行
- [ ] 结构化输出解析器（LLM 原始输出 → 模型实例）
- [ ] 全链路单命令完成：文档抽取 → 草稿 → 审核 → 发布
- [ ] audit 做质量门禁
- [ ] 标记"AI 生成"供人溯源
- [ ] 文档
