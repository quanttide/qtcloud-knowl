#!/usr/bin/env python3
"""
心理治疗理论的范畴论建模

使用 Python 实现范畴论基础结构，展示 CBT、心理动力学、人本主义三种疗法的建模
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Set, TypeVar, Generic
from dataclasses import dataclass, field
from enum import Enum

T = TypeVar('T')
U = TypeVar('U')


class Morphism(Generic[T, U]):
    """态射：范畴论中的态射定义"""
    
    def __init__(self, name: str, domain: 'Object', codomain: 'Object', 
                 transform: Callable[[Any], Any] | None = None):
        self.name = name
        self.domain = domain
        self.codomain = codomain
        self.transform = transform or (lambda x: x)
    
    def __call__(self, x: Any) -> Any:
        return self.transform(x)
    
    def __repr__(self):
        return f"{self.name}: {self.domain.name} → {self.codomain.name}"


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


class Category(ABC):
    """范畴基类"""
    
    def __init__(self, name: str):
        self.name = name
        self.objects: Dict[str, Object] = {}
        self.morphisms: List[Morphism] = []
    
    def add_object(self, obj: Object) -> None:
        self.objects[obj.name] = obj
    
    def add_morphism(self, m: Morphism) -> None:
        self.morphisms.append(m)
    
    def compose(self, f: Morphism, g: Morphism) -> Morphism | None:
        """态射复合：g ∘ f"""
        if f.codomain == g.domain:
            name = f"{g.name} ∘ {f.name}"
            return Morphism(
                name, 
                f.domain, 
                g.codomain,
                lambda x: g(f(x))
            )
        return None
    
    def identity(self, obj: Object) -> Morphism:
        """单位态射"""
        return Morphism(f"id_{obj.name}", obj, obj, lambda x: x)
    
    def __repr__(self):
        return f"Category({self.name}, objects={list(self.objects.keys())})"


class CBTCategory(Category):
    """认知行为疗法范畴"""
    
    def __init__(self):
        super().__init__("CBT")
        
        # 定义对象
        X = Object("X", {"client"})           # 来访者
        B = Object("B", {"behavior"})          # 行为模式
        N = Object("N", {"belief"})            # 核心信念
        E = Object("E", {"emotion"})           # 情绪体验
        
        self.add_object(X)
        self.add_object(B)
        self.add_object(N)
        self.add_object(E)
        
        # 定义态射（干预机制）
        f = Morphism("identify", X, B, 
                     lambda x: f"识别{x}的自动思维")
        g = Morphism("restructure", B, N, 
                     lambda b: f"重塑{b}的认知图式")
        h = Morphism("regulate", N, E, 
                     lambda n: f"调节{n}引发的情绪")
        
        self.add_morphism(f)
        self.add_morphism(g)
        self.add_morphism(h)
        
        # 复合态射：X → E
        self.full_morphism = self.compose(f, self.compose(g, h))
    
    def therapy_sequence(self) -> str:
        """治疗序列"""
        return " → ".join([
            self.morphisms[0].name,
            self.morphisms[1].name,
            self.morphisms[2].name
        ])


class PsychoDynamicCategory(Category):
    """心理动力学范畴"""
    
    def __init__(self):
        super().__init__("PsychoDynamic")
        
        # 定义对象
        X = Object("X", {"client"})
        R = Object("R", {"relational_field"})  # 关系场
        N = Object("N", {"belief"})
        U = Object("U", {"unconscious"})        # 无意识
        E = Object("E", {"emotion"})
        
        self.add_object(X)
        self.add_object(R)
        self.add_object(N)
        self.add_object(U)
        self.add_object(E)
        
        # 定义态射
        defense = Morphism("defense", R, N, 
                          lambda r: f"防御机制处理{r}")
        transference = Morphism("transference", X, R, 
                               lambda x: f"移情关系{x}")
        manifestation = Morphism("manifestation", N, E, 
                                 lambda n: f"无意识显现{n}")
        
        self.add_morphism(transference)
        self.add_morphism(defense)
        self.add_morphism(manifestation)


class HumanisticCategory(Category):
    """人本主义范畴"""
    
    def __init__(self):
        super().__init__("Humanistic")
        
        # 定义对象
        X = Object("X", {"client"})
        R = Object("R", {"relational_field"})
        S = Object("S", {"self_consciousness"})  # 自我意识
        E = Object("E", {"emotion"})
        
        self.add_object(X)
        self.add_object(R)
        self.add_object(S)
        self.add_object(E)
        
        # 定义态射
        empathy = Morphism("empathy", X, R, 
                          lambda x: f"共情理解{x}")
        unconditional = Morphism("unconditional", R, S, 
                                lambda r: f"无条件积极关注{r}")
        self_actualization = Morphism("self_actualization", S, E, 
                                      lambda s: f"自我实现{s}")
        
        self.add_morphism(empathy)
        self.add_morphism(unconditional)
        self.add_morphism(self_actualization)
        
        # 复合态射
        self.full_morphism = self.compose(
            empathy, 
            self.compose(unconditional, self_actualization)
        )


class Functor(Generic[T, U]):
    """函子：范畴之间的映射"""
    
    def __init__(self, name: str, source: Category, target: Category):
        self.name = name
        self.source = source
        self.target = target
        self.object_map: Dict[str, str] = {}
        self.morphism_map: Dict[str, str] = {}
    
    def map_object(self, obj_name: str, target_name: str) -> None:
        self.object_map[obj_name] = target_name
    
    def map_morphism(self, morph_name: str, target_name: str) -> None:
        self.morphism_map[morph_name] = target_name


class NaturalTransformation:
    """自然变换：函子之间的映射"""
    
    def __init__(self, name: str, functor_f: Functor, functor_g: Functor):
        self.name = name
        self.functor_f = functor_f
        self.functor_g = functor_g
        self.components: Dict[str, Morphism] = {}
    
    def add_component(self, obj: Object, morphism: Morphism) -> None:
        self.components[obj.name] = morphism


def demo():
    """演示"""
    print("=" * 60)
    print("心理治疗理论的范畴论建模")
    print("=" * 60)
    
    # CBT 范畴
    print("\n【认知行为疗法 CBT】")
    cbt = CBTCategory()
    print(f"范畴: {cbt.name}")
    print(f"对象: {list(cbt.objects.keys())}")
    print("态射:")
    for m in cbt.morphisms:
        print(f"  {m}")
    print(f"治疗序列: {cbt.therapy_sequence()}")
    print(f"完整映射: {cbt.full_morphism}")
    
    # 心理动力学范畴
    print("\n【心理动力学】")
    psycho = PsychoDynamicCategory()
    print(f"范畴: {psycho.name}")
    print(f"对象: {list(psycho.objects.keys())}")
    print("态射:")
    for m in psycho.morphisms:
        print(f"  {m}")
    
    # 人本主义范畴
    print("\n【人本主义】")
    human = HumanisticCategory()
    print(f"范畴: {human.name}")
    print(f"对象: {list(human.objects.keys())}")
    print("态射:")
    for m in human.morphisms:
        print(f"  {m}")
    print(f"完整映射: {human.full_morphism}")
    
    # 函子示例
    print("\n【函子映射】")
    f_cbt_to_set = Functor("F_CBT", cbt, cbt)
    f_cbt_to_set.map_object("X", "X")
    f_cbt_to_set.map_object("B", "B")
    print(f"函子: {f_cbt_to_set.name}")
    print(f"  X ↦ {f_cbt_to_set.object_map.get('X')}")
    print(f"  B ↦ {f_cbt_to_set.object_map.get('B')}")
    
    print("\n" + "=" * 60)
    print("范畴论结构对比")
    print("=" * 60)
    
    comparison = """
    | 疗法 | 核心态射 | 范畴结构 | 主要性质 |
    |------|----------|----------|----------|
    | CBT | B → N → E | 预加法范畴 | 单态射→满射 |
    | 心理动力学 | R → N | 完备范畴 | 纤维函子 |
    | 人本主义 | S → E | 加法范畴 | 同构映射 |
    """
    print(comparison)


if __name__ == "__main__":
    demo()
