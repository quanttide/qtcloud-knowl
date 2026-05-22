"""
集成测试：从 information 到 knowledge 的真实 LLM 抽取链路。

## 设计目标

验证 extract 模块在真实 LLM 环境下的端到端行为。测试不 mock 任何外部依赖，
使用配置在环境变量 / Vault 中的真实 API Key 调用 LLM。

## 与单元测试的分工

单元测试（tests/test_extract.py）负责 mock LLM 后的内部逻辑验证、
typer 参数路由、纯函数（_strip_fences、_load_prompt、_clean）以及异常路径。

集成测试（本文件）只做一件单元测试做不了的事：**真实 LLM 端到端调用**。
不做重复验证，不做 LLM 无关的纯文件操作检查。

## 测试策略

因为 LLM 调用有成本且非确定性，所有断言合并在一个测试内，
一次调用完成全部验证，避免重复消耗。

## 断言设计

### 有损断言

对 LLM 输出的断言是有损的——无法预测具体措辞，通过多关键词匹配
（如 "异味" / "smell" / "坏味道"）容忍措辞波动。

### 避免魔法数字

不写 `len(ontologies) >= N` 或 `len(instances) >= M` 这类阈值断言。
模型升级或 prompt 微调后粒度会变，固定阈值频繁假阳性。

用语义断言替代：
- "是否包含某类本体"（文本匹配）而非"本体数量是否达标"
- "实例是否分布在多个本体类别下"而非"实例数量是否达标"

### 快照

每次运行通过后，实际输出 dump 到 `_snapshots/{timestamp}.json`，
供人工抽查 LLM 输出质量随模型升级的变化。
"""

import json
from datetime import datetime
from pathlib import Path

SNAPSHOT_DIR = Path(__file__).resolve().parent / "_snapshots"


def _dump_snapshot(result: dict) -> str:
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = SNAPSHOT_DIR / f"extract_{ts}.json"
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(path)


def test_extract_code_refactor(info_path, knowledge_path):
    """
    从 code-refactor.md 抽取知识，验证输出结构和语义完整性。

    一次 LLM 调用完成四层断言 + 结构对比 + 快照：

    1. domain 非空
       LLM 理解了文档主题。label 和 description 同时为空说明 LLM
       连文档在讲什么都没识别出来。

    2. 核心本体存在
       不检查数量，检查文本中是否包含两类必须的本体：
       - "重构手法"相关——怎么做
       - "代码异味"相关——什么时候做
       缺少任意一个说明 LLM 没有正确理解文档的知识结构。

    3. 实例完整且附属于本体
       每个实例必须带有 ontology 字段（extract.txt 的要求），
       且实例分布在至少 2 个不同本体下。后者确保 LLM 不只是
       把所有东西塞进一个类别，而是做了多类别的知识映射。

    4. 关键概念实例被提取
       LLM 应至少提取出手法类和异味类各一个具体实例。

    5. 结构对齐 gallery
       顶层键和 domain 字段与 knowledge/code-refactor.json 一致。
       不验证具体值（LLM 输出不可能与人工标注完全一致）。
    """
    from app.extract import extract

    result = extract(str(info_path))
    assert "error" not in result, result.get("error", "")

    # === 1. domain ===
    assert result["domain"] is not None
    assert result["domain"]["label"] != ""
    assert result["domain"]["description"] != ""

    # === 2. 核心本体存在 ===
    assert isinstance(result["ontologies"], list)
    assert len(result["ontologies"]) > 0

    all_onto_text = ""
    for o in result["ontologies"]:
        all_onto_text += o.get("label", "") + o.get("description", "")

    assert any(kw in all_onto_text for kw in [
        "重构手法", "refactoring technique", "Refactoring",
        "重构技术", "重构操作",
    ]), f"缺少重构手法本体。已有:\n{all_onto_text[:500]}"

    assert any(kw in all_onto_text for kw in [
        "异味", "smell", "坏味道", "Code Smell",
    ]), f"缺少代码异味本体。已有:\n{all_onto_text[:500]}"

    # === 3. 实例完整且分布合理 ===
    assert isinstance(result["instances"], list)
    assert len(result["instances"]) > 0

    for inst in result["instances"]:
        assert inst.get("ontology", "") != "", \
            f"实例 {inst.get('id')} 缺少 ontology 字段"

    covered_ontologies = {inst.get("ontology", "") for inst in result["instances"]}
    assert len(covered_ontologies) >= 2, \
        f"实例只分布在 {len(covered_ontologies)} 个本体下: {covered_ontologies}"

    # === 4. 关键概念实例 ===
    all_inst_text = ""
    for i in result["instances"]:
        all_inst_text += i.get("label", "") + i.get("description", "")

    assert any(kw in all_inst_text for kw in [
        "提炼函数", "extract function", "提取函数", "Extract Method",
        "提取方法", "提炼方法",
    ]), f"缺少提炼函数实例。已有:\n{all_inst_text[:500]}"

    assert any(kw in all_inst_text for kw in [
        "重复代码", "duplicate code", "Duplicate", "过长函数", "long function",
        "Long Method", "重复逻辑",
    ]), f"缺少代码异味实例。已有:\n{all_inst_text[:500]}"

    # === 5. 结构对齐 gallery ===
    knowledge = json.loads(knowledge_path.read_text(encoding="utf-8"))
    assert set(result.keys()) == set(knowledge.keys()), \
        f"顶层键不一致: {set(result.keys())} vs {set(knowledge.keys())}"
    for field in ["id", "name", "label", "description"]:
        assert field in result["domain"], f"domain 缺少字段: {field}"

    # === 快照 ===
    snapshot_path = _dump_snapshot(result)
    print(f"\n  快照保存至: {snapshot_path}")
