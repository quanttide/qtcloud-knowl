# qtcloud-knowl-cli

知识工程 CLI 工具：对原始知识库进行结构校验、术语检测、跨领域融合分析。

## 命令

```
audit    全量质量审计 — 串行执行全部检测并聚合报告
extract  知识抽取 — 从源文件自动抽取知识到知识库
```

## 快速开始

1. 设置环境变量：
   ```bash
   export QTCLOUD_KNOWL_DATA_HOME=~/my-knowledge/models
   export QTCLOUD_KNOWL_SAMPLE_HOME=~/my-knowledge/raw
   ```
2. 审计已有知识库：`qtcloud-knowl audit`
3. 从源文档抽取知识：`qtcloud-knowl extract`

详细说明见 `docs/index.md`（CLI 参考）和 `../../docs/`（通用设计文档）。

## 目录结构

```
AGENTS.md              # 智能体自描述
CHANGELOG.md           # 变更记录
CONTRIBUTING.md        # 贡献指南
README.md              # 本文件
ROADMAP.md             # 路线图
STATUS.md              # 状态报告
TODO.md                # 待办
docs/                  # CLI 文档
  index.md             # CLI 参考（命令、配置、内部 API）
app/                   # CLI 工具链
  cli.py               # typer 入口
  config.py            # 配置（pydantic Settings）
  models.py            # 数据模型
  loader.py            # 数据加载
  reporters/           # 报告生成
  validators/          # 验证检测
  detectors/           # 领域操作
  reviewers/           # 交互式评审
tests/                 # 测试
  conftest.py          # 测试夹具路径
  fixtures/            # 测试数据
    input/             # 源文档样本
    output/            # 建模结果
  test_*.py            # 单元测试 + 文档测试
```
