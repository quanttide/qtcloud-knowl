# 集成测试设计

## 分层规则

| 层 | 目录 | 职责 |
|----|------|------|
| 单元测试 | `tests/` | 验证单模块函数、条件分支、typer 参数路由 |
| 集成测试 | `integrated_tests/` | 验证模块在真实环境中的协作 |

集成测试只保留三类：

| 类别 | 测什么 |
|------|--------|
| **环境变量启动** | 命令从真实 env 启动，加载 settings，模块不崩溃 |
| **真实数据链路** | 数据从 fixture 流向各模块，中间结果可断言 |
| **跨模块数据流** | 模块 A 输出是模块 B 输入，状态在文件间传递 |

## 下沉清单

以下内容必须由单元测试覆盖，不进入集成测试：

| 排除项 | 理由 | 对应检验问题 |
|--------|------|------------|
| `review` 各 action 的条件分支（缺 id、拒绝无原因等） | 单模块行为 | #1: 崩了是因为分支没走到 |
| `audit --mode` 分支 | typer 参数路由 | #1: 崩了是因为参数没透传 |
| `extract` 异常路径（缺 key、空目录、文件不存在） | 单模块行为 | #2: tmp_path + 三行 setup 就能测 |
| `source` 全部 | 依赖 git subprocess | #3: source 的返回值是函数结果，不是用户工作流 |
| 隐藏命令 9 个 | `audit` 内部编排的单模块调用 | #3: 测的是函数返回值 |

检验问题（每个集成测试候选都过这三问）：

1. 崩溃原因只能是"模块间协作出问题了"还是"环境变了"？
2. 需要真实 fixture 吗？tmp_path + 三行 setup 就能测？
3. 验证的是"用户的工作流"还是"函数的返回值"？

## 模块分析

```
extract  │ 依赖文件系统（sample_home 读取 + data_home 写入）
         │ 可选依赖 LLM（quanttide_agent）
         │
audit    │ 依赖 data_home（读取领域目录）
         │ 依赖 state_home（读写审计状态，增量对比用）
         │ 内部编排 9 个隐藏命令
         │
review   │ 依赖 data_home（读取 domain.json + 写 review.json）
         │ 纯文件 I/O + JSON 操作
         │
source   │ 依赖 git subprocess
         │ → 下沉
```

## 测试设计

### extract（OCL 阶段一）

| # | 类别 | 用例 | 输入 | 断言 | 文件 |
|---|------|------|------|------|------|
| 1 | 环境变量启动 | 空目录不崩溃 | 空 tmp_path 作为 sample + data | exit_code == 0 | `test_phase1_extract.py` |
| 2 | 真实数据链路 | 从 fixtures/input/ 创建骨架 | fixtures/input/ 的 10 份 Markdown | 输出含"抽取完成"，领域目录已创建 | `test_phase1_extract.py` |

> #1 不检验输出内容——只证明命令路径能走完。输出内容由 #2 检验。

### audit（OCL 阶段三/五）

| # | 类别 | 用例 | 输入 | 断言 | 文件 |
|---|------|------|------|------|------|
| 3 | 环境变量启动 | 空知识库不崩溃 | 空 tmp_path 作为 data_home | exit_code == 0，输出含"审计" | `test_phase3_audit.py` |
| 4 | 真实数据链路 | 审计真实领域数据 | fixtures/output/ 的 4 个领域 | 输出含"审计目标"和领域路径 | `test_phase3_audit.py` |
| 5 | 跨模块数据流 | 增量对比 | #4 运行两次 | 第二次输出含"与上次审计一致" | `test_pipeline.py` |
| 6 | 跨模块数据流 | 评审后审计变化 | audit → approve → audit | 第二次 audit 状态随评审变更 | `test_pipeline.py` |

### cross-module pipeline

| # | 类别 | 用例 | 输入 | 断言 | 文件 |
|---|------|------|------|------|------|
| 7 | 跨模块数据流 | extract → audit | fixtures/input/ + fixtures/output/ | 两命令相继执行成功 | `test_pipeline.py` |
| 8 | 跨模块数据流 | extract --llm → review | fixtures/input/ + mock LLM | LLM 抽取 → review 可操作 | `test_pipeline.py` |
| 9 | 环境变量启动 | 无 LLM key 全流程 | fixtures/input/ + fixtures/output/，无 LLM key | extract + audit --mode simple 不崩 | `test_pipeline.py` |

### review

review 不设独立集成测试。`review list` 仅读取文件 + 格式化输出，属于单模块行为。跨模块场景（#6, #8）由 pipeline 文件覆盖。

### source

不设集成测试。`source download` 依赖 `git clone` 子进程，集成测试无法可控运行。单元测试已 100% 覆盖 source 模块。

## 文件组织

```
integrated_tests/
├── README.md               # 本文件
├── conftest.py             # 共享夹具（real_sample_dir, real_knowledge_base, setup_env）
├── fixtures/
│   ├── input/              # 10 份 Markdown 样本文档
│   └── output/             # 4 个领域（biz-ops, doc-std, hr, org-gov）
├── test_phase1_extract.py  # #1, #2
├── test_phase3_audit.py    # #3, #4
└── test_pipeline.py        # #5 ~ #9
```

## 设计原则

1. **测业务价值，不测代码行**。每个测试对应一个用户可感知的场景。`test_audit_empty_kb` 测的是"用户刚安装、空知识库运行 audit 会不会崩溃"，不是"audit 函数的返回值结构对不对"。

2. **不复制单元测试的断言**。单元测试已覆盖条件分支和边界值，集成测试不再重复。集成测试的断言只问两件事：命令是否成功结束、输出是否包含关键业务标识。

3. **fixture 保护**。`real_knowledge_base` 夹具通过 `shutil.copytree` 将 fixtures/output/ 复制到 tmp_path，禁止直接写原 fixture。

4. **env var 隔离**。所有测试通过 `setup_env()` 独立设置环境变量 + `importlib.reload` 刷新模块级 settings。
