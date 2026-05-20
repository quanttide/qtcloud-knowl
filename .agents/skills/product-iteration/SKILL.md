---
name: product-iteration
description: 8-step product iteration cycle — execute ROADMAP versions with built-in QA/PM review checkpoints
---

# Product Iteration Cycle

每次迭代 = 一个 ROADMAP 版本的交付。严格按 9 步循环执行。

## Step 1: 确认版本目标

- 读取 ROADMAP 当前版本的痛点和解决方向
- 确保目标是一个用户可感知的价值，不是一个技术功能

## Step 2: 分解 TODO + 文档计划

- 将版本目标拆解为可执行的 task，每条有停止条件
- 每个 task 不超过 1 人天的粒度
- 写入 TODO.md 对应版本下
- 标注本次迭代可能涉及的文档：STATUS.md / CHANGELOG.md / README.md / docs/index.md / AGENTS.md

## Step 3: 自我检查（进入执行前）

打开 AGENTS.md，逐条确认以下检查项。**不跳过、不默念、逐条回答。**

```
[ ] 元认知 1: 交付物完整性 — 这次要交付什么？功能跑通还是 ROADMAP 承诺？
[ ] 元认知 2: 代码是真相 — 最近有文档变更吗？先跑测试再写文档
[ ] 元认知 3: 模式切换 — 我在做什么模式（执行/文档/分析）？切换对了吗？
[ ] 元认知 4: 置信度 — 我确定这么做对吗？不确定就去验证
[ ] 元认知 5: TODO 标记 — 做完的标 [x]，做不完的标【需人确认】+ 原因
[ ] 工作纪律: 没用 /tmp，没在仓库外写文件
[ ] 测试安全: 上一次全部测试通过是什么时候？
[ ] 测试覆盖率: 新增代码有测试吗？跑 `--cov=app` 确认不降覆盖率
```

## Step 4: 执行 + 文档同步

- 按 TODO 逐条完成
- 每完成一条运行 `uv run pytest tests/` 确认无回归
- 新增代码必须有测试覆盖。每完成一条 task 跑 `uv run pytest --cov=app --cov-report=term-missing --doctest-modules` 确认：
  - **新增模块的语句覆盖率达到 100%**
  - **总体覆盖率不降低**（当前基线 77%）
  - **doctest 全部通过**，新增函数/类必须有 docstring + 可执行的 doctest 示例
  - 未覆盖的行必须有明确理由（如 `if __name__ == "__main__"` 守卫）
- 超出能力范围的 task：标记 `[x]` + 追加 **【需人确认】** + 说明原因
- **代码变更后立即更新相关文档**，不积压到 Step 8：
  - 新增/修改 CLI 参数 → 同步 `docs/index.md` 命令表格
  - 修改工具行为 → 检查 `README.md` 快速开始是否仍准确
  - 修改配置 → 检查 `docs/index.md` 配置表
  - 添加反例 → 同步 `AGENTS.md`
  - 下一阶段：大模型使用步骤 -> 更新 AGENTS.md 知识抽取工作流

## Step 5: QA 评审 + 文档核查

- 验证每条 task 的停止条件是否满足
- 检查异常路径：空输入、错误输入、边界情况
- 检查回归：`uv run pytest tests/` 全部通过
- 检查覆盖率：`uv run pytest --cov=app --cov-report=term-missing --doctest-modules`，**新增模块 100%，总体不降**
- 检查 doctest：`uv run pytest --doctest-modules app/` 全部通过
- 输出评审表（md 格式）
- 检查 Step 4 中同步的文档是否完整、准确

## Step 6: PM 评审 + 文档检查

- 检视交付物是否解决了 ROADMAP 定义的痛点
- 检视命名和交互是否符合业务用户直觉
- 检查 STATUS.md 的工具链状态、已知问题是否已更新
- 输出评审结论：通过 / 需同版本迭代 / 需 bump 版本

## Step 7: 更新 TODO + 文档

- 评审通过 → 将版本下所有 task 标为完成
- 评审发现剩余工作 → 追加为同版本内迭代 task（#xxa、#xxb、...）
- 评审发现需新版本 → 追加到 TODO 下一版本
- **更新 STATUS.md**：日期、工具链、已解决问题

## Step 8: 文档验证（最终检查）

确认以下文档与代码事实一致。**不验证不提交。**

- [ ] ROADMAP.md — 描述是否与交付匹配？痛点是否真实？
- [ ] TODO.md — 当前版本下所有 task 是否已标记？
- [ ] STATUS.md — 日期、工具链状态、已知问题是否最新？
- [ ] CHANGELOG.md — 如有版本变化，是否追加了条目？
- [ ] README.md — CLI 说明是否需要同步？
- [ ] AGENTS.md — 元认知是否有新的反例可追加？
- [ ] docs/index.md — 功能描述是否过时？

## Step 9: 提交

- `git add -A && git commit -m "类型: vX.X 版本说明"`
- 提交后 `git status` 确认无残留变更

## 引用

- AGENTS.md — 元认知规则和工作纪律
- ROADMAP.md — 版本目标和痛点定义
- TODO.md — 具体 task 列表
- CHANGELOG.md — 发布记录
