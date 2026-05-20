# ROADMAP

## [0.0.5] — ReAct 知识抽取循环

建立程序化 ReAct 智能体循环，将"智能体"角色从外部 AI 辅助编码助手内化为代码自身能力。

### Agent 基础设施

- ReAct 循环引擎：`Thought → Action → Observation → Thought` 主循环
- Tool 注册系统：LLM 可调用的工具接口层
- LLM 调用抽象层：支持多 Provider 的消息/补全接口
- Conversation 上下文管理：消息历史窗口维护

### 知识抽取工具集

将现有 CLI 命令和知识发现流程封装为 ReAct 可调用工具：

- `validate_domain(dir)` → 结构完整性检查
- `detect_undefined_terms(sample_dir)` → 未定义术语扫描
- `check_abstraction(dir)` → 本体抽象度检测
- `fusion_check(dir)` → 跨领域融合检测
- `suggest_ontology(domain_id, texts)` → 从源文推荐候选本体
- `suggest_instances(ontology_id, texts)` → 从源文推荐候选实例
- `suggest_relations(domains)` → 跨领域关系推荐
- `write_domain_json(domain_id, data)` → 写入领域 JSON 文件

### 集成点

- 新增 `app/agents/` 子包存放 agent 循环、工具注册、LLM 抽象
- `app/agents/engine.py` — ReAct 主循环
- `app/agents/tools.py` — 工具定义与注册
- `app/agents/llm.py` — LLM 调用抽象
- `app/cli.py` 新增 `extract` 命令触发抽取流程

### 依赖

- `openai` / `anthropic` SDK（择一，可配置）
- `jinja2`（Prompt 模板）

## [0.0.6] — 面向任务的 CLI 重构

当前 9 个命令（validate、fusion-check、find-undefined-terms 等）是工具级 API，需要人编排，不符合"规则引擎 vs 智能体 vs 人类"分工。v0.0.6 将其收敛为 2–3 个面向任务的高层入口。

### CLI 收敛

- `qtcloud-knowl audit` — 全量质量审计
  - Agent 自动串行执行全部检测（validate + fusion-check + find-undefined-terms + check-abstraction + cross-domain-report）
  - 聚合结果，解释根因，标记 **【需人确认】**
  - 输出一份可读审计报告
- `qtcloud-knowl extract` — 从源文件自动抽取知识到知识库
  - 输入：源文档目录
  - Agent 自动执行完整知识发现流程（领域→本体→实例→关系→跨域融合）
  - 输出：填充完成的 domain/ontologies/instances/relations JSON

### 保留底层 API

底层命令（validate、fusion-check 等）不删除，降级为不公开/仅 `--help` 隐藏的接口，供 agent 内部调用。用户面向的是 `audit` 和 `extract`。

---

- 所有已发布版本记录见 [CHANGELOG.md](./CHANGELOG.md)
- v0.0.5 的 agent 基础设施是 v0.0.6 的前置依赖
