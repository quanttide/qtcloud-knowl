# ROADMAP

每个版本解决一个用户痛点。

## v0.1.0 — 文档入库到发布不能一步走完

**痛点**：经过 v0.0.13~v0.0.16，抽取→草稿→审核→落库的每个环节都能单步执行，但缺少一条命令跑完全流程的工作流。

**解决**：
- `extract --pipeline` 一条命令完成：读取源文档 → LLM 抽取 → 生成草稿 → 提交审核 → 落库
- prompt 管线编排：本体发现 → 实例映射 → 关系发现串联执行
- audit 自动触发作为质量门禁，失败时阻断发布
- AI 生成内容标注"AI 生成"供人溯源
- 统一错误处理：任一步骤失败给出明确原因和修复建议


## v0.0.16 — 草稿审核后不能落库

**痛点**：草稿在 `drafts/` 里，review CLI 能看到但不能写入正式知识库。

**解决**：review CLI 接入 drafts/，确认后写入 `data_home` 的 domain.json、ontologies.json、instances.json、relations.json。

**用户能力**：LLM 结果经审核转为正式知识库。

## v0.0.15 — LLM 输出没法保存为结构化草稿

**痛点**：每次跑完只看到 stdout，不能保存结果反复对比。

**解决**：解析 LLM 输出为 Domain/Ontology/Instance/Relation 结构，保存到 `data_home / drafts/` 目录。

**用户能力**：能保存和对比多次抽取结果。

## v0.0.14 — 不知道 LLM 抽出来效果怎么样

**痛点**：prompt 质量决定抽取质量，但不跑一次看不到效果。

**解决**：`app/prompts/` 放 prompt 模板，`extract --llm` 读取文档调用 LLM，输出原始结果到 stdout。

**用户能力**：能验证 prompt 效果，迭代 prompt。

## v0.0.13 — reviewers TUI 无法批量操作，也不支持 AI 草稿

**痛点**：reviewers TUI 只能逐条交互评审，无法脚本化，也无法处理 AI 生成的候选知识。

**解决**：TUI 改为 CLI 命令体系：
- `review --list` 列出待审项（支持 --domain 过滤）
- `review --approve` 全部通过或 `--approve <id>` 单条通过
- `review --reject <id> --reason x` 拒绝并注明原因
- 同一 CLI 同时支持人工知识库评审和 AI 草稿审核

已发布版本见 [CHANGELOG.md](./CHANGELOG.md)。
