# qtcloud-knowl-cli

知识工程 CLI 工具：对原始知识库进行结构校验、术语检测、跨领域融合分析。

## 命令

```
summary              领域概况统计
validate             领域目录结构完整性验证
find-undefined-terms 扫描源文档中出现的术语是否已定义
fusion-check         跨领域融合检测（名称冲突、引用断裂、效力声明）
check-abstraction    本体抽象度检测
auto-fix             骨架文件自动补全
cross-domain-report  跨领域关系覆盖率报告
detect-domain        推荐所属领域
init-domain          初始化新领域目录和骨架文件
```

## 快速开始

1. 设置环境变量：
   ```bash
   export QTCLOUD_KNOWL_DATA_HOME=~/my-knowledge/models
   export QTCLOUD_KNOWL_SAMPLE_HOME=~/my-knowledge/raw
   ```
2. 创建领域：`qtcloud-knowl init-domain 组织治理`
3. 填充 JSON 模型文件
4. 校验：`qtcloud-knowl validate`

详细说明见 `docs/storage.md`。

## 目录结构

```
AGENTS.md              # 智能体自描述
CHANGELOG.md           # 变更记录
CONTRIBUTING.md        # 贡献指南
README.md              # 本文件
ROADMAP.md             # 路线图
STATUS.md              # 状态报告
TODO.md                # 待办
docs/                  # 设计文档
  storage.md           # 数据存储方案
  contract.md          # 人机权责分工
  criteria.md          # 本体评审标准
  workflow.md          # 执行流程
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
