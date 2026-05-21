"""集成测试共享夹具 — 按 OCL 阶段组织。"""

from pathlib import Path
import json

import pytest
from typer.testing import CliRunner


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def sample_doc(tmp_path):
    """创建一份样本源文档。"""
    path = tmp_path / "samples"
    path.mkdir()
    doc = path / "charter.md"
    doc.write_text(
        "# 量潮科技数据治理章程\n\n"
        "## 第一章 总则\n\n"
        "**第一条 目的**\n"
        "为规范公司数据治理工作，保障数据安全，提升数据质量，特制定本章程。\n\n"
        "**第二条 适用范围**\n"
        "本章程适用于公司所有业务部门的数据治理活动。\n\n"
        "**第三条 数据治理机构**\n"
        "公司设立数据治理委员会，负责数据治理政策的制定和监督执行。\n"
        "委员会由首席数据官担任主任，各业务部门数据负责人担任委员。\n\n"
        "## 第二章 数据分类\n\n"
        "**第四条 数据分级**\n"
        "公司数据分为核心数据、重要数据和一般数据三个级别。\n"
        "核心数据包括客户身份信息、财务数据；\n"
        "重要数据包括业务运营数据、项目文档；\n"
        "一般数据包括公开信息、内部通知。\n\n"
        "**第五条 数据安全**\n"
        "核心数据须加密存储，访问需双人审批。\n"
        "重要数据须定期备份，访问需部门负责人审批。\n"
        "一般数据可公开访问。\n",
        encoding="utf-8",
    )
    return doc


@pytest.fixture
def knowledge_base(tmp_path):
    """创建含一个领域的知识库。"""
    kbase = tmp_path / "kbase"
    domain_dir = kbase / "data-gov"
    domain_dir.mkdir(parents=True)

    (domain_dir / "domain.json").write_text(
        json.dumps({"id": "data-gov", "name": "数据治理", "perspective": "数据治理视角", "vocabulary": ["数据", "治理", "安全", "分类"]}, ensure_ascii=False),
        encoding="utf-8",
    )
    (domain_dir / "ontologies.json").write_text(
        json.dumps({"ontologies": [{"id": "o1", "name": "data-classification", "label": "数据分类"}]}, ensure_ascii=False),
        encoding="utf-8",
    )
    (domain_dir / "instances.json").write_text(
        json.dumps({"instances": [{"id": "i1", "ontology": "o1", "subject": "核心数据", "source": "charter.md", "article": "第四条"}]}, ensure_ascii=False),
        encoding="utf-8",
    )
    (domain_dir / "relations.json").write_text(
        json.dumps({"relations": [{"id": "r1", "source_ontology": "o1", "target_ontology": "o1", "relation": "references", "description": "参考"}]}, ensure_ascii=False),
        encoding="utf-8",
    )
    return kbase
