---
name: product-iteration
description: 8-step product iteration cycle — execute ROADMAP versions with built-in QA/PM review checkpoints
---

# Product Iteration Cycle

每次迭代 = 一个 ROADMAP 版本的交付。严格按 8 步循环执行。

## Step 1: 确认版本目标

- 读取 ROADMAP 当前版本的痛点和解决方向
- 确保目标是一个用户可感知的价值，不是一个技术功能

## Step 2: 分解 TODO

- 将版本目标拆解为可执行的 task，每条有停止条件
- 每个 task 不超过 1 人天的粒度
- 写入 TODO.md 对应版本下

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
```

## Step 4: 执行

- 按 TODO 逐条完成
- 每完成一条运行 `uv run pytest tests/` 确认无回归
- 超出能力范围的 task：标记 `[x]` + 追加 **【需人确认】** + 说明原因

## Step 5: QA 评审

- 验证每条 task 的停止条件是否满足
- 检查异常路径：空输入、错误输入、边界情况
- 检查回归：全部测试通过
- 输出评审表（md 格式）

## Step 6: PM 评审

- 检视交付物是否解决了 ROADMAP 定义的痛点
- 检视命名和交互是否符合业务用户直觉
- 输出评审结论：通过 / 需同版本迭代 / 需 bump 版本

## Step 7: 更新 TODO

- 评审通过 → 将版本下所有 task 标为完成
- 评审发现剩余工作 → 追加为同版本内迭代 task（#xxa、#xxb、...）
- 评审发现需新版本 → 追加到 TODO 下一版本

## Step 8: 更新 ROADMAP + 提交

- 确保 ROADMAP 的描述与 TODO 实际交付一致
- 如有版本号变化，更新 CHANGELOG + pyproject.toml
- git add -A && git commit

## 引用

- AGENTS.md — 元认知规则和工作纪律
- ROADMAP.md — 版本目标和痛点定义
- TODO.md — 具体 task 列表
- CHANGELOG.md — 发布记录
