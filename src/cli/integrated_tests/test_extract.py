"""
集成测试：从 information 到 knowledge 的真实 LLM 抽取链路。

## 设计目标

验证 extract 模块在真实 LLM 环境下的端到端行为。测试不 mock 任何外部依赖，
使用配置在环境变量 / Vault 中的真实 API Key 调用 LLM。

## 被测对象

`app.extract.extract(source: str) -> dict`

输入：单个 .md 文件路径
输出：{"domain": ..., "ontologies": [...], "instances": [...]}

## 测试数据

- fixtures/information/code-refactor.md    → 原始文档（LLM 输入）
- fixtures/knowledge/code-refactor.json    → gallery 标准答案（结构对比用）

## 测试策略

| 测试 | 类型 | 验证点 |
|------|------|--------|
| test_extract_code_refactor | 正向链路 | LLM 能正确理解文档，输出结构化知识 |
| test_extract_output_matches_gallery_structure | 结构一致性 | 输出 JSON 的顶层键和 domain 字段与 gallery 对齐 |
| test_extract_non_md_file | 异常路径 | 非 .md 文件不被接受 |
| test_extract_nonexistent_file | 异常路径 | 不存在的文件报错 |

## 与单元测试的分工

单元测试（tests/test_extract.py）负责：
- mock LLM 后的内部逻辑验证（fence 剥离、ontology 字段保留、API key 缺失等）
- typer 参数路由
- extract() 内部的纯函数（_strip_fences、_load_prompt、_clean）

集成测试（本文件）负责：
- 真实 LLM 端到端调用
- LLM 输出质量的结构化验证
- 不重复单元测试已覆盖的纯函数行为

## 断言设计说明

对 LLM 输出的断言是有损的——无法预测具体措辞，只能验证：
1. 结构存在性（key 不少、字段不空）
2. 本体粒度的合理性（数量 ≥ 3，涵盖重构手法和异味两类核心本体）
3. 实例的完整性（数量 ≥ 5，所有实例附带 ontology 引用）
4. 关键概念覆盖（提炼手法和异味各至少有一个实例被提取）

断言采用多关键词匹配（如 "异味" / "smell" / "坏味道"），
因为不同 LLM 输出的中文/英文措辞不稳定。
"""

import json


def test_extract_code_refactor(info_path, knowledge_path):
    """
    正向链路：从 code-refactor.md 抽取知识，验证核心概念完整。

    这是最核心的集成测试，覆盖了整个 extract() 函数的主路径：
      读文件 → 填充 prompt → 调用 LLM → 解析 JSON → 清理字段 → 返回 dict

    断言策略分为四层：
    1. domain 非空：LLM 理解了文档主题
    2. ontologies ≥ 3 且覆盖核心概念：
       - "重构手法"（refactoring-technique）—— 怎么做
       - "代码异味"（code-smell）—— 什么时候做
       这两个是重构领域最基础的本体，缺少任意一个说明 LLM 没有正确
       理解文档的知识结构。
    3. instances ≥ 5 且全部带 ontology 字段：
       - 数量要求确保 LLM 不只是提取了顶层概念
       - ontology 字段是 extract.txt 提示词新增的要求，验证 prompt 生效
    4. 实例覆盖具体手法和异味：
       - 至少有一个"提炼函数"/"Extract Method"类实例（手法）
       - 至少有一个"重复代码"/"过长函数"类实例（异味）

    输入：fixtures/information/code-refactor.md（约 120 行 Markdown）
    输出预期：{"domain": {...}, "ontologies": [...], "instances": [...]}

    不验证的具体值：
    - 本体的具体措辞（如"代码异味"vs"代码坏味道"）
    - 实例的精确数量
    - 实例的 description 格式
    - domain.id 的具体值（被 _clean 转换为 UUID）
    """
    from app.extract import extract

    result = extract(str(info_path))
    assert "error" not in result, result.get("error", "")

    # === 第一层：domain ===
    # domain 是知识库的入口，LLM 必须至少识别出主题名称和简要描述。
    # label 和 description 同时为空说明 LLM 没有理解文档在讲什么。
    assert result["domain"] is not None
    assert result["domain"]["label"] != ""
    assert result["domain"]["description"] != ""

    # === 第二层：ontologies ===
    # 本体是提取质量的直接体现。数量过少（< 3）说明 LLM 只做了
    # 关键词提取而非知识结构化。重构领域至少有五类本体：
    # 手法、异味、目标、流程、安全网——3 个是最低要求。
    assert isinstance(result["ontologies"], list)
    assert len(result["ontologies"]) >= 3

    all_onto_text = ""
    for o in result["ontologies"]:
        all_onto_text += o.get("label", "") + o.get("description", "")

    # "重构手法"（refactoring-technique）是重构领域的核心本体，
    # 定义了"手法=动机+步骤+效果+条件"的抽象模式。
    assert any(kw in all_onto_text for kw in ["重构手法", "refactoring technique", "Refactoring"]), \
        "缺少重构手法相关本体"

    # "代码异味"（code-smell）是另一个核心本体，定义了"症状→手法"
    # 的映射关系。它与重构手法成对出现。
    assert any(kw in all_onto_text for kw in ["异味", "smell", "坏味道"]), \
        "缺少代码异味相关本体"

    # === 第三层：instances ===
    # 实例是本体的具体填充。数量 ≥ 5 确保 LLM 不只是列出了本体名字
    # 而是真正从文档中提取了具体条目。
    assert isinstance(result["instances"], list)
    assert len(result["instances"]) >= 5

    # ontology 字段是 extract.txt 新加的要求。每个实例必须标注它
    # 属于哪个本体。这个断言验证 prompt 的效果：
    # LLM 确实在输出中包含了 ontology 字段，且 _clean(is_instance=True)
    # 没有把它丢弃。
    for inst in result["instances"]:
        assert inst.get("ontology", "") != "", \
            f"实例 {inst.get('id')} 缺少 ontology 字段"

    # === 第四层：具体实例内容 ===
    # 文档中明确列出了"过长函数→提炼函数"和"重复代码→提取公共方法"
    # 的对应关系。LLM 应至少提取出其中一对。
    all_inst_text = ""
    for i in result["instances"]:
        all_inst_text += i.get("label", "") + i.get("description", "")

    assert any(kw in all_inst_text for kw in ["提炼函数", "extract function", "提取函数", "Extract Method"]), \
        "缺少提炼函数/提取函数实例"

    assert any(kw in all_inst_text for kw in ["重复代码", "duplicate code", "Duplicate", "过长函数", "long function"]), \
        "缺少重复代码或过长函数等异味实例"


def test_extract_output_matches_gallery_structure(info_path, knowledge_path):
    """
    结构一致性：抽取结果的顶层结构应与 gallery 标准答案对齐。

    gallery 的 knowledge/code-refactor.json 是人工审核过的标准输出。
    但 LLM 输出的具体值不可能与人工标注完全一致，所以本测试只验证
    结构约束而不验证具体值：

    1. 顶层键一致：result.keys() == {"domain", "ontologies", "instances"}
       —— 确保 extract() 的输出结构与 gallery 的标准定义对齐。
       如果键不匹配，说明 extract.txt prompt 的 JSON 格式指令没有被 LLM 遵循，
       或者 extract() 函数的返回结构被改动过。

    2. domain 字段完整：domain 必须包含 id/name/label/description 四个字段。
       这四个字段是 extract.txt 定义的基础契约。如果缺少某个字段，
       说明 LLM 输出不完整或 _clean() 有 bug。

    不验证：
    - ontologies 和 instances 的具体内容（由 test_extract_code_refactor 覆盖）
    - domain.id 的值（被 UUID 化后不可预测）
    - 字段的语义正确性
    """
    from app.extract import extract

    result = extract(str(info_path))
    assert "error" not in result, result.get("error", "")

    knowledge = json.loads(knowledge_path.read_text(encoding="utf-8"))

    # 顶层键必须与 gallery 一致：只有 domain / ontologies / instances
    # 多一个或少一个都说明结构契约被打破。
    assert set(result.keys()) == set(knowledge.keys()), \
        f"顶层键不一致: {set(result.keys())} vs {set(knowledge.keys())}"

    # domain 必须包含所有四个基础字段
    for field in ["id", "name", "label", "description"]:
        assert field in result["domain"], f"domain 缺少字段: {field}"


def test_extract_non_md_file(tmp_path):
    """
    异常路径：非 .md 文件应被拒绝。

    extract() 目前限定只处理 .md 文件。传入 .txt 或其他格式应返回
    {"error": "仅支持 .md 文件: ..."}。

    这个测试在集成层保留是为了确保环境部署后这个验证逻辑没有被
    配置或依赖问题破坏。纯函数逻辑本身由单元测试覆盖。
    """
    from app.extract import extract
    f = tmp_path / "test.txt"
    f.write_text("content")
    result = extract(str(f))
    assert "error" in result
    assert "仅支持" in result["error"]


def test_extract_nonexistent_file():
    """
    异常路径：不存在的文件路径应返回错误。

    extract() 在文件不存在时应返回 {"error": "文件不存在: ..."}，
    而不是抛出 FileNotFoundError 让程序崩溃。

    这个测试在集成层保留的目的与 test_extract_non_md_file 相同：
    确保实际部署环境中文件系统访问逻辑正常。
    """
    from app.extract import extract
    result = extract("/nonexistent/test.md")
    assert "error" in result
    assert "不存在" in result["error"]
