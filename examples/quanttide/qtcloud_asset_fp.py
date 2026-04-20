#!/usr/bin/env python3
"""
qtcloud-asset-cli 的函数式编程完整实现

使用 returns 库的思维模式，不依赖外部库
展示如何将命令式代码转换为函数式代码
"""

from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, TypeVar, Generic, Any
from enum import Enum

T = TypeVar('T')
E = TypeVar('E')


# ============================================================================
# 基础单子实现 (returns 库思维)
# ============================================================================

class Result(Generic[T, E]):
    """Result 单子 - Railway Oriented Programming"""
    
    def __init__(self, _value: T | E, _is_success: bool):
        self._value = _value
        self._is_success = _is_success
    
    @classmethod
    def success(cls, value: T) -> 'Result[T, E]':
        return cls(value, True)
    
    @classmethod
    def failure(cls, error: E) -> 'Result[T, E]':
        return cls(error, False)
    
    @property
    def is_ok(self) -> bool:
        return self._is_success
    
    def map(self, f: Callable[[T], Any]) -> 'Result[T, E]':
        """Functor map: 转换成功值"""
        if self._is_success:
            return Result.success(f(self._value))
        return self
    
    def bind(self, f: Callable[[T], 'Result']) -> 'Result':
        """Monad bind: 链式处理"""
        if self._is_success:
            return f(self._value)
        return self
    
    def alt(self, f: Callable[[E], T]) -> 'Result':
        """处理错误"""
        if not self._is_success:
            return Result.success(f(self._value))
        return self
    
    def __repr__(self):
        if self._is_success:
            return f"Success({self._value})"
        return f"Failure({self._value})"


class Maybe(Generic[T]):
    """Maybe 单子 - None 安全"""
    
    def __init__(self, _value: T | None):
        self._value = _value
    
    @classmethod
    def just(cls, value: T) -> 'Maybe[T]':
        return cls(value)
    
    @classmethod
    def nothing(cls) -> 'Maybe[T]':
        return cls(None)
    
    @classmethod
    def from_optional(cls, value: T | None) -> 'Maybe[T]':
        return cls(value)
    
    @property
    def is_some(self) -> bool:
        return self._value is not None
    
    def map(self, f: Callable[[T], Any]) -> 'Maybe':
        if self._value is not None:
            return Maybe.just(f(self._value))
        return self
    
    def bind(self, f: Callable[[T], 'Maybe']) -> 'Maybe':
        if self._value is not None:
            return f(self._value)
        return self
    
    def get_or_else(self, default: T) -> T:
        return self._value if self._value is not None else default
    
    def __repr__(self):
        if self._value is not None:
            return f"Some({self._value})"
        return "Nothing"


# ============================================================================
# 数据类型
# ============================================================================

@dataclass(frozen=True)
class SkillConfig:
    version: str = "1.0"
    entrance: str = ""
    params: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AssetConfig:
    type: str
    provider: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ContractSchema:
    assets: dict[str, AssetConfig] = field(default_factory=dict)
    skills: dict[str, SkillConfig] = field(default_factory=dict)


@dataclass
class ArchiveTask:
    product: str
    src_dir: Path
    dst_dir: Path


@dataclass
class Workflow:
    name: str
    pattern: str
    tasks: list[ArchiveTask] = field(default_factory=list)


@dataclass
class ArchiveResult:
    product: str
    total: int = 0
    moved: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)
    source_removed: bool = False
    error: str | None = None
    
    @property
    def ok(self) -> bool:
        return self.error is None and len(self.failed) == 0


# ============================================================================
# 契约层函数
# ============================================================================

def load_yaml(path: Path) -> Result[dict[str, Any], Exception]:
    """安全加载 YAML"""
    try:
        import yaml
        with open(path, encoding="utf-8") as f:
            return Result.success(yaml.safe_load(f) or {})
    except Exception as e:
        return Result.failure(e)


def parse_contract(raw: dict[str, Any]) -> Result[ContractSchema, Exception]:
    """解析契约"""
    try:
        assets = {
            name: AssetConfig(**config)
            for name, config in raw.get("assets", {}).items()
        }
        skills = {
            name: SkillConfig(**config)
            for name, config in raw.get("skills", {}).items()
        }
        return Result.success(ContractSchema(assets=assets, skills=skills))
    except Exception as e:
        return Result.failure(e)


def find_contract(root: Path) -> Maybe[Path]:
    """查找契约文件"""
    path = root / ".quanttide" / "asset" / "contract.yaml"
    return Maybe.from_optional(path if path.exists() else None)


def get_skill(name: str, contract: ContractSchema) -> Result[SkillConfig, KeyError]:
    """获取技能"""
    if name in contract.skills:
        return Result.success(contract.skills[name])
    return Result.failure(KeyError(f"技能不存在: {name}"))


# ============================================================================
# 工作流层
# ============================================================================

def get_products(directory: Path) -> Result[list[str], Exception]:
    """获取产品列表"""
    if not directory.exists():
        return Result.failure(FileNotFoundError(f"目录不存在: {directory}"))
    return Result.success(sorted([
        d.name for d in directory.iterdir() if d.is_dir()
    ]))


def resolve_workflow(
    skill_name: str,
    input_dir: Path,
    output_dir: Path,
    pattern: str | None,
    contract: ContractSchema,
) -> Result[Workflow, Exception]:
    """解析工作流 - 单子组合"""
    
    def build(skill: SkillConfig, products: list[str]) -> Workflow:
        return Workflow(
            name=skill.entrance,
            pattern=pattern or skill.params.get("pattern", "*.md"),
            tasks=[
                ArchiveTask(p, input_dir / p, output_dir / p)
                for p in products
            ],
        )
    
    return (
        get_skill(skill_name, contract)
        .bind(lambda s: get_products(input_dir))
        .map(lambda ps: build(contract.skills[skill_name], ps))
    )


# ============================================================================
# 操作层
# ============================================================================

import shutil
import os


def move_file(src: Path, dst: Path) -> Result[None, Exception]:
    """移动文件"""
    try:
        shutil.copy2(src, dst)
        os.unlink(src)
        return Result.success(None)
    except Exception as e:
        return Result.failure(e)


def make_dir(path: Path) -> Result[None, Exception]:
    """创建目录"""
    try:
        path.mkdir(parents=True, exist_ok=True)
        return Result.success(None)
    except Exception as e:
        return Result.failure(e)


def rollback(src: Path, dst: Path, moved: list[str]) -> Result[list[str], None]:
    """回滚"""
    rolled = []
    for name in moved:
        src_file = src / name
        dst_file = dst / name
        if dst_file.exists() and not src_file.exists():
            try:
                shutil.copy2(dst_file, src_file)
                os.unlink(dst_file)
                rolled.append(name)
            except Exception:
                pass
    return Result.success(rolled)


def archive_task(task: ArchiveTask, pattern: str) -> Result[ArchiveResult, Exception]:
    """归档任务"""
    result = ArchiveResult(product=task.product)
    src, dst = task.src_dir, task.dst_dir
    
    # 检查
    if not src.exists():
        return Result.failure(FileNotFoundError(f"源目录不存在: {src}"))
    
    # 收集
    files = list(src.glob(pattern))
    result.total = len(files)
    
    if not files:
        result.skipped = [f"(无匹配 {pattern})"]
        return Result.success(result)
    
    # 创建目录
    mkdir_result = make_dir(dst)
    if not mkdir_result.is_ok():
        result.error = str(mkdir_result._value)
        return Result.success(result)
    
    # 移动
    moved = []
    for f in files:
        dst_file = dst / f.name
        if dst_file.exists():
            result.skipped.append(f.name)
            continue
        
        m = move_file(f, dst_file)
        if m.is_ok():
            moved.append(f.name)
        else:
            result.failed.append(f.name)
            result.error = f"移动失败: {f.name}"
    
    result.moved = moved
    
    # 回滚
    if result.failed:
        rollback(src, dst, moved)
    
    # 清理
    if not result.failed and not result.error:
        try:
            if not any(src.iterdir()):
                src.rmdir()
                result.source_removed = True
        except Exception:
            pass
    
    return Result.success(result)


# ============================================================================
# pipeline
# ============================================================================

def flow(*functions: Callable) -> Callable:
    """管道组合"""
    def pipeline(initial):
        result = initial
        for fn in functions:
            result = fn(result)
        return result
    return pipeline


# ============================================================================
# 演示
# ============================================================================

def demo():
    print("=" * 60)
    print("qtcloud-asset-cli 函数式编程实现")
    print("=" * 60)
    
    # 1. Maybe
    print("\n【1. Maybe - 可选值】")
    path = find_contract(Path("/tmp"))
    print(f"  查找契约: {path}")
    print(f"  有值: {path.is_some}")
    print(f"  默认值: {path.get_or_else(Path('default'))}")
    
    # 2. Result
    print("\n【2. Result - 错误处理】")
    skill = SkillConfig(version="1.0", params={"pattern": "*.md"})
    contract = ContractSchema(skills={"archive": skill})
    
    ok = get_skill("archive", contract)
    print(f"  获取存在的技能: {ok}")
    
    err = get_skill("missing", contract)
    print(f"  获取不存在的技能: {err}")
    
    # 3. pipeline
    print("\n【3. Pipeline】")
    add_one = lambda x: x + 1
    double = lambda x: x * 2
    to_str = lambda x: f"value: {x}"
    
    p = flow(add_one, double, to_str)
    print(f"  5 → +1 → ×2 → str: {p(5)}")
    
    # 4. 范畴映射
    print("\n【4. 范畴映射表】")
    print("""
    ┌──────────────┬──────────────────────────────────┐
    │ 范畴论       │ 实现                            │
    ├──────────────┼──────────────────────────────────┤
    │ 对象        │ Result[T, E], Maybe[T], IO[T]   │
    │ 态射        │ .map(), .bind()                │
    │ 函子        │ map（保存结构）                  │
    │ 单子        │ bind（扁平化）                  │
    │ 逆态射      │ .alt()                         │
    │ 复合       │ flow()                         │
    └──────────────┴──────────────────────────────────┘
    """)
    
    # 5. 实际工作流
    print("\n【5. 工作流示例】")
    workflow_result = resolve_workflow(
        "archive",
        Path("/input"),
        Path("/output"),
        "*.md",
        contract,
    )
    print(f"  工作流: {workflow_result}")


if __name__ == "__main__":
    demo()