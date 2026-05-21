---
name: product-tests
description: Test design patterns — distinguish unit tests from integrated tests, cover business value not just function branches
---

# Product Tests Skill

## 测试分层

```
tests/                  → 单元测试：快、隔离、mock 外部依赖
integrated_tests/       → 集成测试：慢、真实环境、验证模块协作
```

## 单元测试（tests/）

**职责**：验证单个模块/函数的逻辑正确性。

### 覆盖哪些

- 条件分支：空输入、缺参数、文件不存在、权限错误
- CLI 参数路由：`typer` option 透传、默认值、非法值
- 纯函数逻辑：列表过滤、状态变更、格式转换
- 异常路径：每个 `if err:` 分支至少一个测试
- 边界值：空列表、单元素列表、超长字符串

### 不覆盖哪些

- 模块间协作：mock 掉所有跨模块调用
- 外部依赖：mock 掉 LLM、文件系统（除 tmp_path）、网络
- 环境变量：用 monkeypatch 隔离每个测试
- 真实数据：用 `tmp_path` 创建最小测试数据，不用 fixture 目录

### 模式

```python
# 条件分支：每个 if/else 一个测试
def test_reject_without_id_errors(self, review_env):
    runner = CliRunner()
    result = runner.invoke(app, ["review", "reject"])
    assert result.exit_code == 1

# 纯函数：构造输入 → 断言输出
def test_list_pending_only(self, review_env):
    items = list_items(pending_only=True)
    assert len(items) == 3

# 文件状态：写文件 → 调用函数 → 断言文件变更
def test_approve_single(self, review_env):
    approve_item("test-domain:ontology:o1")
    reviews = load_reviews()
    assert reviews["test-domain:ontology:o1"]["status"] == "通过"
```

## 集成测试（integrated_tests/）

**职责**：验证模块在真实环境中的协作。

### 只保留三类

| 类别 | 测什么 | 示例 |
|------|--------|------|
| **环境变量启动** | 命令从真实 env 启动，加载 settings，模块不崩溃 | audit 空目录 + 真实数据 |
| **真实数据链路** | 数据从 fixture 流向各模块，中间结果可断言 | extract 对样本文档创建骨架 |
| **跨模块数据流** | 模块 A 输出是模块 B 输入，状态在文件间传递 | audit → review approve → 二次 audit 显示增量 |

### 必须下沉到单元测试的

- 条件分支（空输入、缺 key、文件不存在）
- typer 参数透传（--pending、--mode）
- 单模块函数（list_items、approve_item）

### 检验清单

```
[ ] 这个测试崩溃的原因只能是"模块间协作出问题了"还是"环境变了"？
    → 如果是"某个分支没走到"，它不该是集成测试
[ ] 这个测试需要真实 fixture 吗？
    → 如果 tmp_path + 三行 setup 就能测，它不该是集成测试
[ ] 这个测试验证的是"用户的工作流"还是"函数的返回值"？
    → 验证 workflow 的留着，验证 return value 的下沉
```

## 测试设计原则

### 测业务价值，不是测代码行

每个测试应该对应一个用户可感知的场景。不好的测试："assert function returns True"；好的测试："用户 approve 后该条目不再出现在 pending 列表中"。

### 测试密度：每条停止条件至少一个测试

每个 TODO 版本有停止条件，每个停止条件对应至少一个测试。停止条件是"什么算做完"，测试是"怎么证明做完了"。

### tests 和 docs 必须是独立 task

不嵌入功能 task。每个版本 TODO 至少有一条 `[ ] 测试` 和一条 `[ ] 更新 docs/commands.md`。

### fixture 保护

集成测试使用的 fixture 目录必须通过 `shutil.copytree` 复制到 `tmp_path`，禁止直接读写原 fixture。单元测试一律用 `tmp_path` 创建最小数据，不从 fixture 目录读取。

### env var 隔离

每个测试必须独立设置 env var，通过 `monkeypatch.setenv` + `importlib.reload` 刷新模块级 settings。`setup_env()` 封装了这个模式，集成测试统一使用它。

```python
app = setup_env(monkeypatch, data_home=tmp_path, sample_dir=fixture_dir)
```
