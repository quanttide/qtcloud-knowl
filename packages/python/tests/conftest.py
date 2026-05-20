import json
from pathlib import Path

import pytest


@pytest.fixture
def fixture_dir(tmp_path: Path) -> Path:
    """创建含完整领域数据的临时目录。

    biz-ops 领域包含 4 个本体、10 个实例、5 个关系。
    """
    domain = tmp_path / "biz-ops"
    domain.mkdir()

    with open(domain / "domain.json", "w", encoding="utf-8") as f:
        json.dump(
            {"id": "biz-ops", "name": "业务管理", "perspective": "业务管理视角", "files": ["biz.md"], "vocabulary": ["项目", "报价", "签约"]},
            f,
        )
    with open(domain / "ontologies.json", "w", encoding="utf-8") as f:
        json.dump(
            {"ontologies": [{"id": "o1", "name": "project-lifecycle", "label": "项目生命周期", "perspective": "业务管理", "description": "", "pattern": "", "source_files": []}, {"id": "o2", "name": "quote-flow", "label": "报价流程", "perspective": "业务管理", "description": "", "pattern": "", "source_files": []}]},
            f,
        )
    with open(domain / "instances.json", "w", encoding="utf-8") as f:
        json.dump(
            {"instances": [{"id": "i1", "ontology": "o1", "subject": "项目A", "source": "biz.md", "article": "第5条"}, {"id": "i2", "ontology": "o2", "subject": "报价单", "source": "biz.md", "article": "第8条", "amount": "100万"}]},
            f,
        )
    with open(domain / "relations.json", "w", encoding="utf-8") as f:
        json.dump(
            {"relations": [{"id": "r1", "source_ontology": "o1", "target_ontology": "o2", "relation": "triggers", "description": "项目启动触发报价", "detail": ""}]},
            f,
        )

    return tmp_path
