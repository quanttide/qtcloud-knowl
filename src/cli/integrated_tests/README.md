# 集成测试

状态：**6 tests, all passing**

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

## 下沉到单元测试的

以下场景由单元测试覆盖，不进入集成测试：

| 场景 | 原因 |
|------|------|
| extract 空目录不崩溃 | `tests/test_extract.py::test_extract_empty_dir` |
| audit 空知识库不崩溃 | `tests/test_audit.py::test_audit_empty_dir` |
| extract --llm mock | mock 外部依赖不属于集成测试 |
| review list 列领域 | 单模块读文件 + 格式化输出 |
| source list 空目录 | 单模块读目录 + 格式化输出 |
| audit --mode 分支 | typer 参数路由 |
| review 条件分支（缺 id、拒绝无原因） | 单模块行为 |
| extract 异常路径（缺 key、文件不存在） | 单模块行为 |
| 隐藏命令 9 个 | audit 内部编排的单模块调用 |

检验问题：每个测试崩溃的原因只能是"模块间协作出问题了"还是"环境变了"？

## 测试设计

### extract（真实数据链路）

| # | 用例 | 输入 | 断言 | 文件 |
|---|------|------|------|------|
| 1 | 从 fixtures/input/ 创建骨架 | 10 份 Markdown + 4 个已有领域 | 输出含"抽取完成" | `test_extract.py` |

### audit（真实数据链路）

| # | 用例 | 输入 | 断言 | 文件 |
|---|------|------|------|------|
| 2 | 审计 4 个领域 | fixtures/output/（biz-ops, doc-std, hr, org-gov） | 输出含"审计目标" | `test_audit.py` |

### main（跨模块数据流）

| # | 用例 | 输入 | 断言 | 文件 |
|---|------|------|------|------|
| 3 | extract → audit 链路 | fixtures/input/ + fixtures/output/ | 两命令相继执行成功 | `test_main.py` |
| 4 | audit 两次 → 增量对比 | 与 #2 相同，运行两次 | 第二次输出"相比上次审计" | `test_main.py` |
| 5 | audit → approve → audit | audit 发现 issue → review 全部通过 → 二次 audit | approve 成功 + 二次 audit 输出 diff | `test_main.py` |
| 6 | 无 LLM key 全流程 | fixtures/input/ + fixtures/output/，无 key | extract + audit --mode simple 不崩 | `test_main.py` |

## 实现说明

### conftest.setup_env 的 settings 隔离

15 个 app 模块通过 `from app.config import settings` 在模块级缓存了 settings 引用。`setup_env` 不重载模块，而是直接替换每个已加载模块的 `.settings` 属性：

```python
new_settings = config.Settings()
for mod_name in sys.modules:
    if mod_name.startswith("app."):
        sys.modules[mod_name].settings = new_settings
```

无需 `importlib.reload`，纯属性注入。

### state_dir 不能放在 data_home 内

validate 会遍历 data_home 下的所有子目录。若 state_dir 放入 data_home，validate 会将其识别为领域目录并报 MISS，污染审计结果。

**解决**：增量对比和评审测试使用 `tmp_path / "audit-state"`（与 data_home 同级）。

### review approve 不影响 audit 结果

当前 `fusion_check` 不读取 review 状态。测试验证的是 audit → review → audit 的三模块串联不崩溃，而非"review 减少了 issue"。

## 文件组织

```
integrated_tests/
├── README.md               # 本文件
├── conftest.py             # 共享夹具（real_sample_dir, real_knowledge_base, setup_env）
├── fixtures/
│   ├── input/              # 10 份 Markdown 样本文档
│   └── output/             # 4 个领域（biz-ops, doc-std, hr, org-gov）
├── test_extract.py         # 命令级：extract
├── test_audit.py           # 命令级：audit
└── test_main.py            # 全链路：跨模块协作
```

## 设计原则

1. **测业务价值，不测代码行**。每个测试对应一个用户可感知的场景。

2. **集成测试不重复单元测试**。单模块行为、条件分支、参数路由下沉到单元测试。

3. **fixture 保护**。`real_knowledge_base` 夹具通过 `shutil.copytree` 复制到 tmp_path，禁止直接写原 fixture。

4. **env var 隔离**。所有测试通过 `setup_env()` 独立设置环境变量 + `importlib.reload` 刷新模块级 settings。
