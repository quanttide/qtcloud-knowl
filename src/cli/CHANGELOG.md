# 变更记录

## [0.1.6] - 2026-05-22

### Changed

- 移除 relations 输出，仅保留 domain/ontologies/instances

## [0.1.5] - 2026-05-22

### Changed

- prompt 注入源目录名，提示 LLM 同一目录下的文件属于同一作品

## [0.1.4] - 2026-05-22

### Added

- extract 逐文件进度提示，不再静默等待

## [0.1.3] - 2026-05-22

### Changed

- 移除 `sample_home`/`source_home` 配置项
- 移除 audit `--sample-dir` 参数
- audit 输出去重，概览 + 检测结果两段式

## [0.1.2] - 2026-05-22

### Fixed

- 移除 `Relation` 引用，对齐 PyPI `quanttide-knowl` 模型结构
- `audit` 命令恢复正常

## [0.1.1] - 2026-05-22

### Changed

- 移除本地 `qtcloud-knowl` SDK 依赖，loader 内置到 CLI 中
- 依赖仅剩 `quanttide-knowl`（PyPI）+ `quanttide-agent`

## [0.1.0] - 2026-05-22

### Breaking changes

- extract 完全重写：全程 LLM 驱动，移除规则匹配模式
- 数据模型简化：Domain/Ontology/Instance/Relation 统一为 id/name/label/description
- 依赖切换：使用 `quanttide-knowl`（PyPI）替代本地 `qtcloud-knowl` SDK

### Removed

- `source`、`review` 命令
- 所有隐藏命令（summary/validate/find-undefined-terms 等）
- `--llm` 参数

### Added

- CI：`.github/workflows/publish-python.yml`
- `extract --source`：从本地目录直接抽取知识库

## [0.0.20] - 2026-05-21

### Fixed

- 补全 `pyproject.toml` 缺失的 `typer`、`pydantic-settings`、`quanttide` 依赖

## [0.0.19] - 2026-05-21

### 重构

- 使用 `quanttide_agent.Tool` 对象替代 tuple 工具定义
- audit 使用 `Tool.execute(inp)` 替代 `capture_run`
- agent 复用 tools.py 的 Tool 定义，消除重复

### 工程

- 依赖 `quanttide-agent>=0.3.0`

## [0.0.18] - 2026-05-21

### 文档

- 新增 `docs/tutorial.md` — 从源文档到知识库的完整流程教程
- 教程对应 6 个集成测试，每步可验证

### 重构

- 集成测试从 11 个精简至 6 个，下沉 5 个单模块测试到单元测试
- 集成测试文件统一命名：`test_extract.py`、`test_audit.py`、`test_main.py`
- `setup_env` 用 settings 属性注入替代 `importlib.reload`，移除模块重载 hack

### 工程

- 新增 `[build-system]` 配置，支持 `pip install` 安装 CLI 为系统命令
- 使用 `uv sync` 管理开发依赖

## [0.0.17] - 2026-05-21

### 功能

- 新增 `source` CLI 命令：`source download`、`source list`、`source remove`
- `source download --name <name>` 从 GitHub 下载源文档到 `source_home`
- `source list` 查看已下载的源文档，如无则显示可用列表
- `source remove` 删除已下载的源文档
- 新增配置 `QTCLOUD_KNOWL_SOURCE_HOME`，默认 `data_home / sources/`

### 测试

- 新增 6 项 source 命令测试
- 更新 config 和 docs 测试适配 `sample_home` 默认值

## [0.0.14] - 2026-05-21

### 功能

- `extract --llm <file>` 对指定文档运行 LLM 语义抽取，输出原始结果到 stdout
- 新增 `app/prompts/` 目录，存放 ontology-discovery / instance-mapping / relation-discovery prompt 模板
- 新增配置：`QTCLOUD_KNOWL_LLM_MODEL`（默认 deepseek-chat）、`QTCLOUD_KNOWL_LLM_BASE_URL`

### 测试

- 新增 5 项 extract --llm 测试（mock LLM 调用、异常路径覆盖）

## [0.0.13] - 2026-05-21

### 功能

- 新增 `review` CLI 命令：`review list`、`review approve`、`review reject`、`review reset`
- `review list --pending` 只显示待审项，`review list --domain NAME` 按领域过滤
- `review approve` 不传参数时全部通过，传 `--id` 时单条通过
- `review reject --id KEY --reason TEXT` 拒绝并注明原因
- review CLI 同时支持已有知识库评审和 AI 草稿审核（接口预留）
- `app/review.py` 100% 测试覆盖

### 文档

- 新增 `product-release` skill
- `docs/commands.md` 新增 `review` 命令参考

## [0.0.12] - 2026-05-21

### 重构

- CLI 改用 `qtcloud-knowl` SDK 包（`packages/python/`）的模型和加载器
- 删除 `app/models.py` 和 `app/loader.py`（三套重复逻辑合一）
- `reviewers/data.py` 底层调用 SDK，向上保持 dict 接口兼容
- 修复 `Instance.data` 可变默认值 bug（SDK 已用 `Field(default_factory=dict)`）

### 功能

- 新增 `product-refactor` skill

## [0.0.11] - 2026-05-20

### 修复

- 修复传入非法路径时的崩溃
- 修复 `diff` 模式下审计结果污染
- 修复空环境变量导致的异常
- 减少噪声输出
- 清理无用 import

### 文档

- 新增 P0-P4 任务分级机制
- 拆分 CLI 文档为 index/commands/config 三层
- 向 product-review skill 补充文档编写反模式示例

## [0.0.10] - 2026-05-20

### 功能

- `audit` diff 比较：支持对比两次审计结果
- 审计状态文件存储至 XDG `state_home`
- 新增 `product-review` skill（7 项盲区检查点）
- 强化 `product-iteration` skill 文档同步

### 修复

- 审计无变更时输出改进

## [0.0.9] - 2026-05-20

### 改进

- `extract` 命令输出单行摘要
- 统一错误消息格式

## [0.0.8] - 2026-05-20

### 功能

- `audit` 支持 simple/full 两种模式
- 新增 `product-iteration` skill
- ROADMAP 对齐 v0.0.9 规划

## [0.0.7] - 2026-05-20

### 修复

- `audit` 命令实现 action 路径输出
- 清理 ROADMAP/TODO 过期条目
- STATUS 同步至 v0.0.6 实际状态

## [0.0.6] - 2026-05-20

### CLI 重构

- 面向场景的 CLI：`audit`（业务语言审计）、`extract`（领域知识提取）
- 低级别命令（`summary`、`validate`、`check-abstraction` 等）隐藏为 `dev` 子命令
- 设计文档从 `src/cli/docs/` 移至顶层 `docs/`
- 新增业务 + 技术双层 CLI 文档
- 测试 143 个，全部通过

## [0.0.5] - 2026-05-20

### 重构

- 集成 `quanttide-agent` 替换本地 Agent 实现（ReActAgent、Action、Tool）
- 消息模型从自定义格式迁移至 `quanttide-agent` 标准消息类型
- 配置层接入 Vault 密钥管理
- 测试从 40 个扩至 135 个，覆盖率从 37% 提升至 74%
- 修复 `detect_domain` 中 `Path` 类型转换 bug

## [0.0.4] - 2026-05-20

### CLI 重设计

- `sys.argv` 手动分发 → `typer`，自动 `--help` / `--show-completion`
- 所有 CLI 命令不再接受 `data_dir`、`sample_dir` 位置参数，统一从 `Settings` 读取
- `find-undefined-terms`、`fusion-check` 默认路径改读 `settings.sample_home`（环境变量 `QTCLOUD_KNOWL_SAMPLE_HOME`）

### 配置层统一

- `config.py` 新增 `Settings.sample_home`（`QTCLOUD_KNOWL_SAMPLE_HOME`），无默认值
- 移除模块级 `SAMPLE_DIR` 常量，`config.py` 只保留 `Settings`

### 文档与测试

- 新增 `tests/test_docs.py` —— CLI help 输出验证、storage.md env var 一致性、Settings 字段校验
- `app/cli.py`、`app/config.py` 模块 docstring 含 doctest 示例
- `README.md` 重写、STATUS.md 同步、storage.md 路径修正

### 模型升级

- `app/models.py`：`dataclasses` → `pydantic.BaseModel`，字段使用 `quanttide` v0.1.1 类型注释
- `Domain.name`、`Ontology.name` → `NameField`（str, max_length=100）
- `Ontology.label` → `LabelField`
- `Domain.perspective`、`Ontology.perspective`、`Ontology.description`、`Relation.description` → `DescriptionField`

## [0.0.3] - 2026-05-20

### 重构

- `config.py` 集成 `quanttide.LocalStorage` + `pydantic_settings.BaseSettings`
- 环境变量统一为 `QTCLOUD_KNOWL_DATA_HOME`（XDG 风格）
- 新增 `conftest.py` 统一测试 mock
- 移除 `DATA_DIR` 模块级别名，全部通过 `Settings` 获取

## [0.0.2] - 2026-05-20

### 修复检测精度

- find-undefined-terms 扩展 `IGNORED_CHAPTER_RE` 覆盖中文数字、阿拉伯数字、`第X` 占位符
- fusion-check 新增 `HUMAN_CONFIRM_TERMS` 和 `HUMAN_CONFIRM_REFS`，输出标记 `【需人确认】`

### 测试增强

- 测试从 5 个扩至 30 个，用 `capsys` 捕获 stdout 校验输出内容
- 新增 `test_config.py` 覆盖 `KNOWL_DATA_DIR` 环境变量

### 数据目录可配置化

- `config.py` 支持 `KNOWL_DATA_DIR` 环境变量，fallback 到 `~/.local/share/quanttide/qtcloud-knowl/`
- 新增 `docs/storage.md` 阐述存储方案
- 修复 4 个模块中 `data_dir` 字符串→`Path` 转换缺失的 bug

### 重构与修复

- `reviewers/__init__.py` 引用路径 `src.validators.*` → `app.validators.*`
- `cli.py` 帮助信息更新为 `qtcloud-knowl`
- `detect_domain.py` 新增 `--data-dir` 参数
- `auto_fix.py` 移除未使用的 `sample_dir` 参数

## [0.0.1] - 2026-05-20

### 初始版本

- 从 `knowl-agent` 实验项目移植到 `qtcloud-knowl` 作为 `src/cli`
- 核心模块：detectors、reporters、reviewers、validators
- CLI 入口 `cli.py`
- 测试套件：加载、校验、抽象、汇总
- 项目名称：`qtcloud-knowl-cli`

## [1.0.0] - 2026-05-19

### 第一阶段：本体重构

14 个 ontology pattern 完成抽象重构，去除具体值改为可复用抽象模式。

| 领域 | 本体 | 抽象方向 |
|------|------|---------|
| biz-ops | role-responsibility | 角色以职责+权限成对定义 |
| biz-ops | service-process | 流程由阶段序列组成 |
| biz-ops | risk-control | 风险领域→控制措施集→措施分类 |
| biz-ops | cognitive-sovereignty | 原则约束行为边界 |
| doc-std | document-structure | 文档由元信息+引言+主体+结尾构成 |
| doc-std | format-rule | 格式要素有允许使用和禁止使用两种边界 |
| doc-std | content-standard | 内容受通用性/稳定性/域分离约束 |
| hr | development-track | 职业发展经历预备阶段后进入并行通道 |
| hr | rank-level | 等级递增表示资深程度 |
| hr | resignation-process | 流程由阶段序列组成 |
| org-gov | authority-responsibility | 清理 pattern 中的具体引用 |
| org-gov | hierarchy-system | 层级中上层效力高于下层 |
| org-gov | deliberation-procedure | 审议流程：召集→出席→辩论→表决→记录 |
| org-gov | qualification-condition | 清理末尾的具体例子 |

### 第二阶段：实例归位

- 从 ontology pattern 中提取具体值迁移到 instances.json
- 移除 ontology 中的 `source_files` 字段，移至实例层
- 补充 7 个新实例，全部本体达到 ≥3 实例的覆盖率标准

### 第三阶段：跨领域关系网

建立 8 条跨领域关系，每领域 ≥2 条：

| 源领域 | 源概念 | 目标领域 | 目标概念 | 关系类型 |
|--------|--------|---------|---------|---------|
| org-gov | 资格-条件 | hr | 职级等级 | references |
| biz-ops | 角色-职责 | org-gov | 权责结构 | instance-of |
| doc-std | 文档结构 | org-gov | 层级体系 | governs |
| hr | 离职流程 | biz-ops | 服务流程 | intersects |

### 第四阶段：工具链升级

- 新增 `scripts/check-abstraction.sh` — 本体抽象度检测脚本
- 新增 `scripts/cross-domain-report.sh` — 跨领域关系覆盖率报告
- 修复四个脚本问题：auto-fix、find-undefined-terms、fusion-check、detect-domain
- `.review.json` 新增 79 条评审记录，覆盖全部 83 项
