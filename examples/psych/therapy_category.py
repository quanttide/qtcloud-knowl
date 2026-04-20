#!/usr/bin/env python3
"""
心理治疗理论的范畴论建模 v2.0

使用 Python 实现范畴论基础结构，支持：
- 运算符重载（@ 和 >>）用于态射复合
- 自动单位态射
- Monad 实现治疗阻抗
- 自然变换完整实现
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Set, TypeVar, Generic, Optional
from dataclasses import dataclass, field
from enum import Enum
from functools import reduce

T = TypeVar('T')
U = TypeVar('U')
V = TypeVar('V')


# ============================================================================
# 基础范畴论结构
# ============================================================================

class Object:
    """对象：范畴论中的对象定义"""
    
    def __init__(self, name: str, elements: Set[Any] | None = None):
        self.name = name
        self.elements = elements or set()
    
    def __repr__(self):
        return self.name
    
    def __hash__(self):
        return hash(self.name)
    
    def __eq__(self, other):
        return isinstance(other, Object) and self.name == other.name
    
    def __matmul__(self, other: 'Morphism') -> 'Morphism':
        """左结合复合：self @ f = f ∘ self（不推荐使用）"""
        raise NotImplementedError("对象不支持 @ 运算，请使用态射")


class Morphism(Generic[T, U]):
    """态射：范畴论中的态射定义"""
    
    def __init__(self, name: str, domain: Object, codomain: Object, 
                 transform: Callable[[Any], Any] | None = None):
        self.name = name
        self.domain = domain
        self.codomain = codomain
        self.transform = transform or (lambda x: x)
    
    def __call__(self, x: Any) -> Any:
        return self.transform(x)
    
    def __repr__(self):
        return f"{self.name}: {self.domain.name} → {self.codomain.name}"
    
    def __matmul__(self, other: 'Morphism') -> 'Morphism':
        """@ 运算符：复合态射 g @ f = g ∘ f（先执行 other，再执行 self）"""
        if self.domain == other.codomain:
            return Morphism(
                f"{self.name} ∘ {other.name}",
                other.domain,
                self.codomain,
                lambda x: self(other(x))
            )
        raise TypeError(f"态射不可复合：{other.codomain} ≠ {self.domain}")
    
    def __rshift__(self, other: 'Morphism') -> 'Morphism':
        """>> 运算符：右结合复合 f >> g = g ∘ f"""
        if other.domain == self.codomain:
            return Morphism(
                f"{other.name} >> {self.name}",
                self.domain,
                other.codomain,
                lambda x: other(self(x))
            )
        raise TypeError(f"态射不可复合：{self.codomain} ≠ {other.domain}")
    
    def __lshift__(self, other: 'Morphism') -> 'Morphism':
        """<< 运算符：左结合复合 f << g = f ∘ g"""
        if self.domain == other.codomain:
            return Morphism(
                f"{self.name} << {other.name}",
                other.domain,
                self.codomain,
                lambda x: self(other(x))
            )
        raise TypeError(f"态射不可复合：{other.codomain} ≠ {self.domain}")


class Category(ABC):
    """范畴基类"""
    
    def __init__(self, name: str):
        self.name = name
        self.objects: Dict[str, Object] = {}
        self.morphisms: List[Morphism] = []
        self._identity_morphisms: Dict[str, Morphism] = {}
    
    def add_object(self, obj: Object, auto_identity: bool = True) -> None:
        """添加对象，自动创建单位态射"""
        self.objects[obj.name] = obj
        if auto_identity:
            self._identity_morphisms[obj.name] = Morphism(
                f"id_{obj.name}", obj, obj, lambda x: x
            )
    
    def add_morphism(self, m: Morphism) -> None:
        self.morphisms.append(m)
    
    def id(self, obj_name: str) -> Optional[Morphism]:
        """获取单位态射"""
        return self._identity_morphisms.get(obj_name)
    
    def compose(self, f: Morphism, g: Morphism) -> Morphism | None:
        """态射复合：g ∘ f"""
        if f.codomain == g.domain:
            return g @ f
        return None
    
    def __repr__(self):
        return f"Category({self.name}, |Obj|={len(self.objects)}, |Hom|={len(self.morphisms)})"


# ============================================================================
# 心理治疗范畴
# ============================================================================

class CBTCategory(Category):
    """认知行为疗法范畴 - 线性状态机"""
    
    def __init__(self):
        super().__init__("CBT")
        
        # 定义对象
        X = Object("X", {"client"})           # 来访者
        B = Object("B", {"behavior"})          # 行为模式
        N = Object("N", {"belief"})            # 核心信念
        E = Object("E", {"emotion"})           # 情绪体验
        
        for obj in [X, B, N, E]:
            self.add_object(obj)
        
        # 定义态射
        f = Morphism("identify", X, B, 
                     lambda x: f"识别{x}的自动思维")
        g = Morphism("restructure", B, N, 
                     lambda b: f"重塑{b}的认知图式")
        h = Morphism("regulate", N, E, 
                     lambda n: f"调节{n}引发的情绪")
        
        for m in [f, g, h]:
            self.add_morphism(m)
        
        # 使用 >> 运算符复合
        # f >> g >> h 等价于 h ∘ g ∘ f
        self.full_morphism = f >> g >> h
    
    def therapy_sequence(self) -> str:
        return " → ".join([m.name for m in self.morphisms])


class PsychoDynamicCategory(Category):
    """心理动力学范畴 - 纤维结构"""
    
    def __init__(self):
        super().__init__("PsychoDynamic")
        
        # 定义对象
        X = Object("X", {"client"})
        R = Object("R", {"relational_field"})  # 关系场
        N = Object("N", {"belief"})
        U = Object("U", {"unconscious"})        # 无意识（隐藏对象）
        E = Object("E", {"emotion"})
        
        for obj in [X, R, N, U, E]:
            self.add_object(obj)
        
        # 定义态射（纤维结构）
        defense = Morphism("defense", R, N, 
                          lambda r: f"防御机制处理{r}")
        transference = Morphism("transference", X, R, 
                                lambda x: f"移情关系{x}")
        manifestation = Morphism("manifestation", N, E, 
                                lambda n: f"无意识显现{n}")
        
        for m in [defense, transference, manifestation]:
            self.add_morphism(m)


class HumanisticCategory(Category):
    """人本主义范畴 - 同构映射"""
    
    def __init__(self):
        super().__init__("Humanistic")
        
        # 定义对象
        X = Object("X", {"client"})
        R = Object("R", {"relational_field"})
        S = Object("S", {"self_consciousness"})  # 自我意识
        E = Object("E", {"emotion"})
        
        for obj in [X, R, S, E]:
            self.add_object(obj)
        
        # 定义态射
        empathy = Morphism("empathy", X, R, 
                          lambda x: f"共情理解{x}")
        unconditional = Morphism("unconditional", R, S, 
                                lambda r: f"无条件积极关注{r}")
        self_actualization = Morphism("self_actualization", S, E, 
                                    lambda s: f"自我实现{s}")
        
        for m in [empathy, unconditional, self_actualization]:
            self.add_morphism(m)
        
        # 使用 >> 运算符复合
        self.full_morphism = empathy >> unconditional >> self_actualization


# ============================================================================
# 函子与自然变换
# ============================================================================

class Functor(Generic[T, U]):
    """函子：范畴之间的映射"""
    
    def __init__(self, name: str, source: Category, target: Category):
        self.name = name
        self.source = source
        self.target = target
        self.object_map: Dict[str, Object] = {}
        self.morphism_map: Dict[str, Morphism] = {}
    
    def map_object(self, obj: Object, target_obj: Object) -> None:
        self.object_map[obj.name] = target_obj
    
    def map_morphism(self, morph: Morphism, target_morph: Morphism) -> None:
        self.morphism_map[morph.name] = target_morph
    
    def __repr__(self):
        return f"Functor({self.name}): {self.source.name} → {self.target.name}"


class NaturalTransformation:
    """自然变换：函子之间的映射
    
    α: F ⇒ G
    
    对于范畴 C 中的每个对象 X，定义一个分量 α_X: F(X) → G(X)
    使得对于每个态射 f: X → Y，以下方块图可交换：
    
        F(X) ──α_X──► G(X)
         │             │
         │ F(f)       │ G(f)
         ▼             ▼
        F(Y) ──α_Y──► G(Y)
    """
    
    def __init__(self, name: str, functor_f: Functor, functor_g: Functor):
        self.name = name
        self.functor_f = functor_f  # F
        self.functor_g = functor_g    # G
        self.components: Dict[str, Morphism] = {}
    
    def add_component(self, obj: Object, morphism: Morphism) -> None:
        """添加分量 α_obj: F(obj) → G(obj)"""
        self.components[obj.name] = morphism
    
    def check_naturality(self, morph: Morphism) -> bool:
        """验证自然性：F(f) ∘ α_X = α_Y ∘ G(f)"""
        X, Y = morph.domain, morph.codomain
        
        if X.name not in self.components or Y.name not in self.components:
            return False
        
        alpha_x = self.components[X.name]
        alpha_y = self.components[Y.name]
        
        # 检查：α_Y ∘ F(f) = G(f) ∘ α_X
        left = alpha_y(self.functor_f.morphism_map.get(morph.name, morph)(X))
        right = self.functor_g.morphism_map.get(morph.name, morph)(alpha_x(X))
        
        return left == right
    
    def __repr__(self):
        comps = ", ".join(self.components.keys())
        return f"NaturalTransformation({self.name}): [{comps}]"


# ============================================================================
# Monad：治疗阻抗
# ============================================================================

class Resistance(Enum):
    """阻抗类型"""
    DEFENSIVE = "防御阻抗"
    UNCONSCIOUS = "无意识阻抗"
    TRANSFERENCE = "移情阻抗"
    NO_CHANGE = "无变化"


@dataclass
class TherapyResult:
    """治疗结果：包含成功值和阻抗信息"""
    value: Any
    resistance: Optional[Resistance] = None
    message: str = ""
    
    def is_successful(self) -> bool:
        return self.resistance is None
    
    def __repr__(self):
        if self.is_successful():
            return f"Success({self.value})"
        return f"Resistance({self.resistance.value}: {self.message})"


class TherapyMonad:
    """治疗单子：模拟带阻抗的治疗过程
    
    T(A) = Result[A, Resistance]
    
    - Return: η_A: A → T(A)
    - Bind: μ: T(T(A)) → T(A)
    """
    
    def __init__(self, name: str):
        self.name = name
    
    def return_(self, value: Any) -> TherapyResult:
        """Return: 将普通值提升到治疗上下文"""
        return TherapyResult(value=value, message=f"return({value})")
    
    def bind(self, result: TherapyResult, 
            f: Callable[[Any], TherapyResult]) -> TherapyResult:
        """Bind: 链式处理带阻抗的治疗"""
        if not result.is_successful():
            return result  # 传播阻抗
        return f(result.value)
    
    def fail(self, resistance: Resistance, message: str) -> TherapyResult:
        """创建阻抗结果"""
        return TherapyResult(
            value=None,
            resistance=resistance,
            message=message
        )
    
    def map(self, result: TherapyResult, 
           transform: Callable[[Any], Any]) -> TherapyResult:
        """Functorial map: 转换成功值"""
        if result.is_successful():
            return TherapyResult(
                value=transform(result.value),
                message=f"map({result.message})"
            )
        return result
    
    def flat_map(self, result: TherapyResult,
                f: Callable[[Any], TherapyResult]) -> TherapyResult:
        """Flat map: 处理返回单子的函数"""
        return self.bind(result, f)


# ============================================================================
# 演示
# ============================================================================

def demo():
    """演示"""
    print("=" * 60)
    print("心理治疗理论的范畴论建模 v2.0")
    print("=" * 60)
    
    # 运算符演示
    print("\n【运算符重载演示】")
    cbt = CBTCategory()
    f, g, h = cbt.morphisms[0], cbt.morphisms[1], cbt.morphisms[2]
    
    print(f"态射 f: {f}")
    print(f"态射 g: {g}")
    print(f"态射 h: {h}")
    print(f"f >> g: {f >> g}")
    print(f"f >> g >> h: {cbt.full_morphism}")
    
    # 单位态射演示
    print("\n【单位态射演示】")
    X = cbt.objects["X"]
    id_x = cbt.id("X")
    print(f"对象 X 的单位态射: {id_x}")
    
    # 三种范畴
    print("\n【三种疗法范畴】")
    cbt = CBTCategory()
    psycho = PsychoDynamicCategory()
    human = HumanisticCategory()
    
    print(f"CBT: {cbt}")
    print(f"  序列: {cbt.therapy_sequence()}")
    print(f"Psycho: {psycho}")
    print(f"Human: {human}")
    
    # Monad 演示
    print("\n【Monad 治疗阻抗演示】")
    m = TherapyMonad("therapy")
    
    # 成功的治疗
    success = m.return_("情绪改善")
    print(f"Return: {success}")
    
    # 链式处理
    chained = m.bind(success, lambda v: TherapyResult(value=f"处理{v}"))
    print(f"Bind: {chained}")
    
    # 阻抗
    resistance = m.fail(Resistance.DEFENSIVE, "来访者启动防御机制")
    print(f"阻抗: {resistance}")
    
    # 阻抗传播
    chained_r = m.bind(resistance, lambda v: TherapyResult(value="继续治疗"))
    print(f"阻抗传播: {chained_r}")


if __name__ == "__main__":
    demo()