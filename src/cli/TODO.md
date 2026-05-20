# TODO

## v0.0.6 — 面向任务的 CLI 重构

前置依赖：v0.0.5 agent 基础设施（`app/agents/` 子包，包含 engine、tools、llm 模块）。

### CLI 收敛

- [ ] **#9** 新增 `qtcloud-knowl audit` 命令
  - 停止条件：对 fixtures 输出完整审计报告；空目录、无 sample_home、单领域等异常情况给出明确错误而非崩溃
  - [ ] Agent 自动串行执行全部检测（validate + fusion-check + find-undefined-terms + check-abstraction + cross-domain-report）
  - [ ] 聚合各检测结果，解释根因
  - [ ] 输出标记 **【需人确认】**
  - [ ] 输出一份可读审计报告
  - 异常情况：
    - `data_home` 目录不存在 → 打印错误并退出
    - 某领域 JSON 格式错误 → 标记该领域为"跳过"并继续其他领域
    - 所有检测均失败 → 输出带警告的空报告而非崩溃
  - 超出能力（标记 **【需人确认】**）：
    - 检测出术语冲突 → 智能体列出冲突，由人决定保留/重命名/合并
    - 引用断裂涉及模糊名称 → 智能体列出候选，由人确认目标文件
    - `sample_home` 未设置且未传参 → 打印错误并退出
- [ ] **#10** 新增 `qtcloud-knowl extract` 命令
  - 停止条件：对 fixtures input 执行 `extract`，输出 JSON 能通过 `validate` 且人工检查无严重缺失；异常输入不导致静默失败
  - [ ] 输入：源文档目录
  - [ ] Agent 自动执行完整知识发现流程（领域→本体→实例→关系→跨域融合）
  - [ ] 输出：填充完成的 domain/ontologies/instances/relations JSON
  - 异常情况：
    - 源文档目录不存在 → 打印错误并退出
    - 源文档空目录 → 输出空知识库骨架并提示"无内容"
    - 源文件格式不支持（非 .md）→ 跳过该文件并警告
    - 抽取过程中 LLM 调用失败 → 重试 2 次后跳过当前步骤并标记 **【需人确认】**
  - 超出能力（标记 **【需人确认】**）：
    - 领域视角选择 → 智能体推荐最佳匹配视角，由人确认或切换
    - 本体抽象度是否达标 → 按 `docs/criteria.md` 自检，列出不确认项由人判断
    - 实例内容准确性 → 智能体标注"AI 抽取"，由人审核修正
    - 跨领域关系真实性 → 智能体推荐候选关系，由人确认是否存在
    - 本体/实例 ID 和命名 → 智能体按约定生成建议名，由人确认

### 底层 API 降级

- [ ] **#11** 将当前 9 个命令的 Typer 注册方式改为不公开 / 仅 `--help` 隐藏
  - 停止条件：`qtcloud-knowl --help` 只显示 `audit` 和 `extract`；测试中仍可通过 CliRunner 直接调用底层命令
  - [ ] 标记为 `hidden=True` 或移入 `app/agents/tools.py` 作为内部可调用工具
  - [ ] 更新 `--help` 输出：用户只看到 `audit` 和 `extract`

### 文档与测试

- [ ] **#12** 更新 README.md CLI 使用说明
  - 停止条件：README 中 CLI 章节只描述 `audit` 和 `extract`，不含底层命令
- [ ] **#13** 更新 STATUS.md
  - 停止条件：STATUS.md 工具链表格包含 `audit` 和 `extract`，不列底层命令
- [ ] **#14** 测试 `audit` 命令（集成测试）
  - 停止条件：测试覆盖正常路径（对 fixtures 输出报告）和异常路径（空目录、无效路径）
- [ ] **#15** 测试 `extract` 命令（集成测试）
  - 停止条件：测试覆盖正常路径（对 fixtures input 抽取）和异常路径（空目录、无效路径）

---

## 存量问题

- [ ] **#8** fusion-check 引用文件 `《量潮数据项目岗位权责章程》` 不存在
  - 停止条件：确认该文件是否应存在于 SAMPLE_DIR 中，或是引用错误。若是引用错误则修复或标记忽略。
