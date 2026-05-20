# qtcloud-knowl CLI 参考

## 业务视角：这是什么

这是一个**知识库质检员**。它不帮你写知识，而是检查已有知识库的结构问题。

### 它能做什么

**全面体检（audit）**：检查整个知识库，出一份报告，涵盖文件结构、未定义术语、领域冲突、本体抽象度、跨领域关系。标记 **【需人确认】** 的项目由你拍板。

**自动抽取（extract）**：从 Markdown 文档中提炼知识结构草稿。需要配置大模型 API key。所有输出标注"AI 生成"，需审核后入库。

### 人机分工

| 你来做 | 工具来做 |
|--------|----------|
| 决定用哪个视角看知识 | 按你选的视角自动检查 |
| 确认术语冲突怎么处理 | 列出所有冲突术语 |
| 审核 AI 抽取的内容 | 从文档提取候选知识 |
| 判断本体抽象是否到位 | 按标准自检，标记存疑项 |
| 决定跨领域关系是否存在 | 推荐候选关系 |

## 技术参考

### 命令

| 命令 | 说明 |
|------|------|
| `audit` | 全量质量审计 — 串行执行全部 5 项检测，聚合输出可读报告 |
| `extract` | 知识抽取 — 从源文档自动发现本体、实例、关系，填充知识库 |

### 审计流程（audit）

串行执行并按顺序聚合结果：

1. **validate** — 目录结构完整性 + JSON 合法性
2. **find-undefined-terms** — 源文档加粗术语是否已定义
3. **fusion-check** — 跨领域名称冲突、引用断裂、效力声明
4. **check-abstraction** — 本体 pattern 抽象度检测
5. **cross-domain-report** — 跨领域关系覆盖率

输出标记 **【需人确认】** 表示智能体无法决断，需人介入。

### 抽取流程（extract）

需配置 `QTCLOUD_KNOWL_LLM_API_KEY`：

1. 读取源文档目录下所有 `.md` 文件
2. 对每份文件推荐所属领域（词汇匹配）
3. （LLM）分析文档内容，推荐候选本体和实例
4. 写入领域 JSON 骨架
5. 标记 AI 抽取的内容，供人审核修正

### 配置

| 环境变量 | 说明 | 默认值 |
|----------|------|--------|
| `QTCLOUD_KNOWL_DATA_HOME` | 知识库数据目录 | `~/.local/share/quanttide/qtcloud-knowl/` |
| `QTCLOUD_KNOWL_SAMPLE_HOME` | 源文档目录 | 无 |
| `QTCLOUD_KNOWL_LLM_API_KEY` | LLM API key（extract 需要） | 空 |

### 内部命令（不公开）

9 个命令标记 `hidden=True`，不出现在 `--help` 中，可通过 CliRunner 或直接 import 调用，供 `audit` 和 `extract` 内部编排：

`validate` `find-undefined-terms` `fusion-check` `check-abstraction` `auto-fix` `cross-domain-report` `summary` `detect-domain` `init-domain`

### 与顶层设计文档的关系

知识工程的整体流程、本体质量标准、人机分工等通用文档见 `../../docs/`：

- `contract.md` — 三元分工（规则引擎 / 智能体 / 人类）
- `criteria.md` — 本体质量标准（可复用性自检）
- `workflow.md` — 五步知识发现流程
- `storage.md` — 数据存储方案
- `index.md` — AI 能力与局限
