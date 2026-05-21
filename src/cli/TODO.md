# TODO

## 已发布

v0.0.5 → v0.0.14 全部完成，见 [CHANGELOG.md](CHANGELOG.md)。

## v0.0.15 — LLM 抽取结果不能落库

- [ ] 解析 LLM 输出为 Domain / Ontology / Instance / Relation 结构
- [ ] 保存到 `settings.data_home / drafts/ <domain>/` 目录，按时间戳版本化
- [ ] `extract --list-drafts` 列出所有草稿
- [ ] `extract --show-draft <id>` 查看指定草稿及 AI 推理依据
- [ ] review CLI 读取 `drafts/`，确认后写入正式知识库
- [ ] `review explain <id>` 展示 AI 的定义依据和推理路径
- [ ] 测试
- [ ] 更新 docs/commands.md

停止条件：从文档抽取 → 草稿保存 → 查看 AI 依据 → 审核确认 → 落库的完整链路可走通。

## v0.0.16 — 实例归类靠手动，审计看不出下一步

- [ ] AI 抽取的实例自动匹配到已确认的本体下
- [ ] audit 报告末尾附带"写作待办"清单
- [ ] 测试
- [ ] 更新 docs/commands.md

停止条件：抽取实例时自动带出对应本体 ID；audit 显示"缺少 X 文档，建议编写 Y"。

## v0.1.0 — 业务专家还不能自助完成全流程

- [ ] prompt 管线编排：三个 prompt 串联执行
- [ ] 结构化输出解析器（LLM 原始输出 → 模型实例）
- [ ] 全链路单命令完成：文档抽取 → 草稿 → 审核 → 发布
- [ ] audit 做质量门禁
- [ ] 标记"AI 生成"供人溯源
- [ ] 文档
