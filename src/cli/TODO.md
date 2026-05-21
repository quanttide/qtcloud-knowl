# TODO

## 已发布

v0.0.5 → v0.0.12 全部完成，见 [CHANGELOG.md](CHANGELOG.md)。

---

## [已发布] v0.0.13 — reviewers TUI 无法批量操作，也不支持 AI 草稿

- [x] 新增 `review` CLI 命令
  - [x] `review list` 列出所有待审项（支持 --domain 过滤）
  - [x] `review list --pending` 只显示待审项
  - [x] `review approve` 全部通过
  - [x] `review approve --id <key>` 单条通过
  - [x] `review reject --id <key> --reason x` 拒绝并注明原因
  - [x] `review reset` 重置评审记录
- [x] review CLI 同时支持已有知识库评审和 AI 草稿审核（接口预留）
- [x] 保留 reviewers TUI 代码（不做破坏性删除）
- [x] 测试（18 项，100% 覆盖 app/review.py）
- [x] 更新 docs/commands.md

停止条件：`review list` 列出待审项，`review approve --id <key>` 通过后再次 list 不再显示该项。

## v0.0.14 — 不知道 LLM 抽出来效果怎么样

- [ ] `app/prompts/` 目录，存放抽取 prompt 模板
  - [ ] ontology-discovery prompt（本体发现）
  - [ ] instance-mapping prompt（实例映射）
  - [ ] relation-discovery prompt（关系发现）
- [ ] `extract --llm <document>` 读取文档，调用 LLM，输出原始结果到 stdout
- [ ] LLM 连接复用 `quanttide-agent.LLM`
- [ ] 测试
- [ ] 更新 docs/commands.md

停止条件：指定一个源文档，`extract --llm` 能返回原始 LLM 输出。

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
