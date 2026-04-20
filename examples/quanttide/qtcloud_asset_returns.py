#!/usr/bin/env python3
"""
qtcloud-asset-cli 的函数式编程实现

展示 returns 库在 qtcloud-asset-cli 中的应用
"""

from dataclasses import dataclass
from pathlib import Path
from typing import TypeVar

T = TypeVar('T')
E = TypeVar('E')


# ============================================================================
# returns 库风格实现
# ============================================================================

class Result:
    """Result 单子 - Railway Oriented Programming"""
    
    @staticmethod
    def success(value: T) -> 'Result[T, E]':
        return Success(value)
    
    @staticmethod
    def failure(error: E) -> 'Result[T, E]':
        return Failure(error)


class Success(Result):
    """成功结果"""
    def __init__(self, value: T):
        self.value = value


class Failure(Result):
    """失败结果"""
    def __init__(self, error: E):
        self.error = error


class Maybe:
    """Maybe 单子 - None 安全处理"""
    
    @staticmethod
    def from_optional(value):
        return Some(value) if value is not None else Nothing()


class Some(Maybe):
    """有值"""
    def __init__(self, value):
        self.value = value


class Nothing(Maybe):
    """无值"""
    pass


class IO:
    """IO 单子 - 副作用封装"""
    
    @staticmethod
    def of(effect):
        return IO(effect)


# ============================================================================
# qtcloud-asset-cli 映射
# ============================================================================

CONTRACT_MAPPING = """
╔═══════════════════════════════════╤══════════════════════════════════════════╗
║范畴论概念                           │qtcloud-asset-cli 实现                    ║
╠═══════════════════════════════════╪══════════════════════════════════════════╣
║ 对象 (Object)                     │Contract, Workflow, ArchiveTask        ║
║ 态射 (Morphism)                   │resolve_workflow, archive_product     ║
║ 函子 (Functor)                    │map, bind                            ║
║ 单子 (Monad)                      │Result[T,E], IO[T], Maybe[T]         ║
║ 逆态射 (Inverse Morphism)          │_rollback                           ║
║ 自然变换 (Natural Transformation)    │RequiresContext                      ║
║ 范畴复合 (Category Composition)   │flow (pipeline)                     ║
╚═══════════════════════════════════╧══════════════════════════════════════════╝
"""

# ============================================================================
# 原始代码 vs 函数式代码对比
# ============================================================================

ORIGINAL_VS_FUNCTIONAL = """
┌─────────────────────────────────────────────────────────────┐
│                  原始代码 vs 函数式代码                      │
├───────────────────��─────────────────────────────────────────┤
│ 原始代码：                                               │
│   try:                                                   │
│       workflow = resolve_workflow(...)                    │
│   except FileNotFoundError as e:                         │
│       typer.secho(f"错误: {e}", ...)                    │
│   except KeyError as e:                                │
│       typer.secho(f"错误: {e}", ...)                    │
│                                                          │
│ 函数式 (Result 版):                                     │
│   workflow = resolve_workflow(...)                      │
│       .map(process)                                     │
│       .alt(handle_error)                                │
├─────────────────────────────────────────────────────────────┤
│ 原始代码：                                               │
│   if file exists():                                     │
│       move_file()                                       │
│   else:                                                 │
│       skipped.append(file)                             │
│                                                          │
│   函数式 (IO 版):                                       │
│   files = find_matching(...)                           │
│       .map(move_file)                                  │
│       .alt(log_skipped)                                │
├─────────────────────────────────────────────────────────────┤
│ 原始代码：                                               │
│   value = get_config()                                  │
│   if value is None:                                    │
│       value = default                                  │
│                                                          │
│   函数式 (Maybe 版):                                   │
│   value = get_config()                                 │
│       .get_or_else(default)                             │
└─────────────────────────────────────────────────────────────┘
"""

# ============================================================================
# 关键函数映射
# ============================================================================

KEY_FUNCTIONS = """
┌──────────────────────┬──────────────────────────────────┐
│ 原始函数              │ 函数式版本                        │
├──────────────────────┼──────────────────────────────────┤
│ resolve_workflow    │ resolve_workflow: Result[W, E]  │
│ archive_product     │ archive_product: IOResult[R]    │
│ _move_file          │ _move_file: IO[None]            │
│ _rollback           │ _rollback: IO[list[str]]        │
│ find_contract       │ find_contract: Maybe[Path]     │
│ get_skill           │ get_skill: Result[S, KeyError]│
└──────────────────────┴──────────────────────────────────┘
"""


def demo():
    print("=" * 60)
    print("qtcloud-asset-cli 函数式编程 (returns 风格)")
    print("=" * 60)
    
    print("\n【范畴论映射】")
    print(CONTRACT_MAPPING)
    
    print("\n【关键函数映射】")
    print(KEY_FUNCTIONS)
    
    print("\n【原始 vs 函数式】")
    print(ORIGINAL_VS_FUNCTIONAL)
    
    print("\n【使用示例】")
    print("""
    # 1. 错误处理 (Railway Oriented)
    result = (
        resolve_workflow(skill, input, output, pattern, contract)
        .bind(execute_tasks)
        .alt(handle_error)
    )
    
    # 2. 可选值 (Maybe)
    pattern = (
        find_contract(root)
        .bind(load_yaml)
        .bind(parse_contract)
        .map(lambda c: c.skills.get(pattern))
        .get_or_else("*.md")
    )
    
    # 3. 副作用 (IO)
    (
        _mkdir_io(dst_dir)
        .flat_map(lambda _: _move_file_io(src, dst))
        .flat_map(lambda _: _cleanup(src_dir))
    )
    
    # 4. 管道组合 (Pipeline)
    workflow = flow(
        find_contract,
        load_yaml,
        parse_contract,
        resolve_workflow,
    )
    """)


if __name__ == "__main__":
    demo()