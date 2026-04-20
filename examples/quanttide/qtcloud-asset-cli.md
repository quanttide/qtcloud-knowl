# qtcloud-asset-cli 的范畴论建模

## 概述

使用范畴论建模 qtcloud-asset CLI 应用的架构设计，揭示契约驱动的工作流系统在范畴论视角下的结构。

## 应用架构

CLI 应用分为四层：

```
CLI 层 (cli.py)
    ↓
契约层 (contract.py)
    ↓
工作流层 (workflow.py)
    ↓
操作层 (file_operator.py)
```

## 范畴论建模

### 基础对象定义

| 符号 | 含义 | 代码对应 |
|------|------|----------|
| $C$ | 契约 (Contract) | `Contract` 类 |
| $S$ | 技能 (Skill) | `SkillConfig` |
| $A$ | 资产 (Asset) | `AssetConfig` |
| $W$ | 工作流 (Workflow) | `Workflow` 类 |
| $T$ | 任务 (Task) | `ArchiveTask` |
| $F$ | 文件操作 (File) | `archive_product()` |
| $R$ | 结果 (Result) | `ArchiveResult` |

## 范畴定义

### 范畴一：契约层 (Contract Category)

**定义** $\mathbf{Contract}$：

- **对象**：$\text{Obj} = \{C, S, A\}$
- **态射**：配置解析和验证

### 结构

```
C ──get_skill──▶ S
      │
      └──get_asset──▶ A
```

### 函子

**配置加载函子** $F_{\text{load}}: \mathbf{YAML} \to \mathbf{Contract}$：

- $F(\text{yaml})$ = `ContractSchema.model_validate(raw)`
- $F(\text{技能定义})$ = `SkillConfig`

### 范畴论性质

- 契约是 **冻结的 Pydantic 模型**（frozen=True），保证不可变性
- 资产和技能配置构成 **有限集合**（finite set）
- 配置查找构成 **遗忘函子**：$\mathbf{Contract} \to \mathbf{Set}$

---

### 范畴二：工作流层 (Workflow Category)

**定义** $\mathbf{Workflow}$：

- **对象**：$\text{Obj} = \{W, T, P\}$
- $W$：工作流
- $T$：任务列表
- $P$：产品集合

### 结构

```
resolve_workflow
      │
      ▼
S ──────────────▶ W ──▶ T* ──▶ P
(技能)           (工作流)  (任务) (产品)
```

### 函子

**工作流解析函子** $F_{\text{resolve}}: \mathbf{Contract} \to \mathbf{Workflow}$：

- $F(S)$ = 根据技能配置生成的工作流
- $F(\text{pattern})$ = 文件匹配规则
- $F(\text{products})$ = 任务列表

### 范畴论性质

- 工作流到任务的映射是 **列表函子**（List Functor）
- 任务是 **余极限**（colimit）：$\sum_i T_i$
- 产品列表是 **有限集合**

---

### 范畴三：操作层 (Operator Category)

**定义** $\mathbf{Operator}$：

- **对象**：$\text{Obj} = \{F, R, \text{Path}\}$
- **态射**：文件操作

### 结构

```
archive_product: Src ──▶ Dst
                      │
                      ▼
                   Result
```

### 函子

**文件操作函子** $F_{\text{file}}: \mathbf{Path} \to \mathbf{Result}$：

- $F(\text{src_dir})$ = 源目录中的文件集合
- $F(\text{dst_dir})$ = 目标目录
- $F(\text{操作})$ = `ArchiveResult`

### 范畴论性质

- 文件移动构成 **态射** $m: \text{Source} \to \text{Destination}$
- 回滚构成 **逆态射** $m^{-1}$：失败时的逆向操作
- 预览模式构成 **恒等函子**：$\text{Id}: \mathbf{Operator} \to \mathbf{Operator}$

---

## 态射复合

### 完整工作流

```
CLI 输入
    │
    ▼
resolve_workflow (S → W)
    │
    ▼
archive_product (W → R)
    │
    ▼
结果输出
```

使用范畴论符号表示：

$$ \text{Result} = \text{archive\_product} \circ \text{resolve\_workflow} (\text{CLI Input}) $$

即：

$$ R = F_{\text{file}} \circ F_{\text{resolve}}(S) $$

## Monad：错误处理

### 定义

使用 **单子**（Monad）建模错误处理和回滚：

$$ T(\text{Path}) = \text{Result}[\text{Path}, \text{Error}] $$

### 结构

```python
@dataclass
class ArchiveResult:
    product: str
    total: int = 0
    moved: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)
    source_removed: bool = False
    error: str | None = None
```

- **Return**：成功时返回结果
- **Bind**：链式处理，错误时短路
- **失败回滚**：$\mu: T(T(\text{Path})) \to T(\text{Path})$

## 自然变换：配置驱动

### 定义

配置变化如何驱动行为变化：

$$ \eta: F_{\text{pattern}} \Rightarrow F_{\text{default}} $$

- $\eta_S$: 指定 pattern → 使用技能默认 pattern
- $\eta_W$: 工作流配置 → 实际执行参数

### 交换图

```
     CLI 参数
        │
        │ F_param
        ▼
   Skill 配置 ──η──▶ Workflow
        │                │
        │ F_resolve      │ F_execute
        ▼                ▼
   Contract        Result
```

## 设计原则的范畴论解释

| 设计原则 | 范畴论解释 |
|----------|-----------|
| 契约层不依赖操作层 | 函子方向：$\mathbf{Contract} \to \mathbf{Operator}$，单向依赖 |
| 操作层无状态 | 态射是纯函数：$f: A \to B$，无副作用 |
| 预览模式 | 恒等函子：$\text{Id}(\text{Operator})$ |
| 失败回滚 | 逆态射：$m^{-1} \circ m = \text{id}$ |
| 契约冻结 | 对象不可变：$\text{Hom}(A, B)$ 稳定 |

## 代码结构映射

```
┌─────────────────────────────────────────────────────┐
│                    CLI 层                            │
│                 cli.py (Typer)                      │
│                     │                                │
│                     ▼                                │
│  ┌───────────────────────────────────────────────┐   │
│  │              契约层 Category                   │   │
│  │     contract.py (Contract, SkillConfig)       │   │
│  │           C ──get_skill──▶ S                   │   │
│  │           C ──get_asset──▶ A                   │   │
│  └───────────────────────────────────────────────┘   │
│                     │                                │
│                     ▼                                │
│  ┌───────────────────────────────────────────────┐   │
│  │            工作流层 Category                    │   │
│  │           workflow.py (Workflow)               │   │
│  │        S ──resolve──▶ W ──tasks──▶ T*         │   │
│  └───────────────────────────────────────────────┘   │
│                     │                                │
│                     ▼                                │
│  ┌───────────────────────────────────────────────┐   │
│  │             操作层 Category                     │   │
│  │      file_operator.py (archive_product)        │   │
│  │      Path ──m──▶ Result (with rollback)       │   │
│  └───────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

## 结论

- **契约层**：静态配置构成 **有限集合范畴**，支持查询和验证
- **工作流层**：动态生成构成 **列表函子**，任务是余极限
- **操作层**：文件操作构成 **态射**，回滚是逆态射
- **整体架构**：是一个 **函子复合** $F_{\text{total}} = F_{\text{file}} \circ F_{\text{resolve}} \circ F_{\text{load}}$

这种范畴论建模揭示了 CLI 应用的核心结构：**契约驱动** 的 **单向数据流**，通过 **自然变换** 实现配置到行为的映射。

## 函数式编程实现

### returns 库映射

使用 [returns](https://returns.readthedocs.io/) 库实现函数式编程：

| 范畴论概念 | returns 库 | qtcloud-asset-cli 实现 |
|----------|----------|-------------------|
| 对象 | `Result[T, E]` | `Workflow`, `ArchiveTask` |
| 态射 | `bind`, `map` | `resolve_workflow` |
| 函子 | `map_`, `bind` | `flow` 管道 |
| 单子 | `Result`, `IO`, `Maybe` | `ArchiveResult`, IO 操作 |
| 逆态射 | `.alt`, `.lash` | `_rollback` |
| 自然变换 | `RequiresContext` | 依赖注入 |

### 代码示例

```python
from returns.result import Result, safe, Success, Failure
from returns.maybe import Maybe, Nothing, Some
from returns.io import IO, IOResult
from returns.pipeline import flow
from returns.pointfree import bind

# 1. 错误处理 (Result)
result = (
    resolve_workflow(skill, input, output, pattern, contract)
    .bind(execute_tasks)
    .alt(handle_error)  # 错误处理
)

# 2. 可选值 (Maybe)
pattern = (
    find_contract(root)
    .bind(load_yaml)
    .bind(parse_contract)
    .map(lambda c: c.skills.get(skill))
    .get_or_else("*.md")
)

# 3. 副作用 (IO)
archive_result = (
    _mkdir_io(dst_dir)
    .flat_map(lambda _: _move_file_io(src, dst))
    .flat_map(lambda _: _cleanup(src_dir))
)

# 4. 管道组合 (flow)
workflow = flow(
    find_contract,      # Maybe[Path]
    load_yaml,        # Result[dict]
    parse_contract,   # Result[ContractSchema]
    resolve_workflow, # Result[Workflow]
)
```

### 原始 vs 函数式对比

| 场景 | 原始代码 | 函数式 |
|------|---------|--------|
| 错误处理 | `try/except` | `.bind().alt()` |
| 可选值 | `if x is None` | `.get_or_else()` |
| 副作用 | 直接调用 | `.flat_map()` |
| 组合 | 嵌套函数调用 | `flow()` 管道 |

### 关键函数映射

| 原始函数 | 函数式版本 |
|----------|-----------|
| `resolve_workflow` | `Result[Workflow, Exception]` |
| `archive_product` | `IOResult[ArchiveResult]` |
| `_move_file` | `IO[None]` |
| `_rollback` | `IO[list[str]]` |
| `find_contract` | `Maybe[Path]` |
| `get_skill` | `Result[SkillConfig, KeyError]` |
