# 变更记录

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
