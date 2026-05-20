import json
from pathlib import Path

from qtcloud_knowl.models import Domain, Instance, Ontology, Relation


def load_json(path: Path) -> dict:
    """从文件系统加载 JSON。

    Usage:
        >>> from pathlib import Path
        >>> import tempfile, json
        >>> with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        ...     json.dump({"key": "value"}, f)
        ...     p = Path(f.name)
        >>> load_json(p)
        {'key': 'value'}
        >>> p.unlink()
    """
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def get_domain_dirs(data_dir: Path) -> list[Path]:
    """扫描 data_dir 下包含 domain.json 的子目录。

    Usage:
        >>> from pathlib import Path
        >>> get_domain_dirs(Path("/nonexistent"))
        []
    """
    if not data_dir.exists():
        return []
    return sorted(d for d in data_dir.iterdir() if d.is_dir() and (d / "domain.json").exists())


def load_domain(domain_dir: Path) -> Domain:
    """从 domain_dir/domain.json 加载领域信息。

    Usage:
        >>> from pathlib import Path
        >>> import tempfile, json
        >>> with tempfile.TemporaryDirectory() as td:
        ...     d = Path(td) / "test-domain"
        ...     d.mkdir()
        ...     json.dump({"id": "test", "name": "test-name", "vocabulary": ["t1"]},
        ...         open(d / "domain.json", "w", encoding="utf-8"))
        ...     domain = load_domain(d)
        ...     (domain.id, domain.name)
        ('test', 'test-name')
    """
    data = load_json(domain_dir / "domain.json")
    return Domain(
        id=data.get("id", domain_dir.name),
        name=data.get("name", ""),
        perspective=data.get("perspective", ""),
        files=data.get("files", []),
        vocabulary=data.get("vocabulary", []),
    )


def load_ontologies(domain_dir: Path) -> list[Ontology]:
    """从 domain_dir/ontologies.json 加载本体列表。"""
    data = load_json(domain_dir / "ontologies.json")
    return [
        Ontology(
            id=o.get("id", o.get("name", "")),
            name=o.get("name", ""),
            label=o.get("label", ""),
            perspective=o.get("perspective", ""),
            description=o.get("description", ""),
            pattern=o.get("pattern", ""),
            source_files=o.get("source_files", []),
        )
        for o in data.get("ontologies", [])
    ]


def load_instances(domain_dir: Path) -> list[Instance]:
    """从 domain_dir/instances.json 加载实例列表。

    超出核心字段的杂项字段会折叠到 data dict 中。
    """
    data = load_json(domain_dir / "instances.json")
    return [
        Instance(
            id=inst.get("id", ""),
            ontology=inst.get("ontology", ""),
            subject=inst.get("subject", ""),
            source=inst.get("source", ""),
            article=inst.get("article", ""),
            data={k: v for k, v in inst.items() if k not in ("id", "ontology", "subject", "source", "article")},
        )
        for inst in data.get("instances", [])
    ]


def load_relations(domain_dir: Path) -> list[Relation]:
    """从 domain_dir/relations.json 加载关系列表。"""
    data = load_json(domain_dir / "relations.json")
    return [
        Relation(
            id=r.get("id", ""),
            source_ontology=r.get("source_ontology", ""),
            target_ontology=r.get("target_ontology", ""),
            source_instance=r.get("source_instance", ""),
            target_instance=r.get("target_instance", ""),
            relation=r.get("relation", ""),
            description=r.get("description", ""),
            detail=r.get("detail", ""),
        )
        for r in data.get("relations", [])
    ]


def load_all_domains(data_dir: Path) -> list[tuple[Path, Domain, list[Ontology], list[Instance], list[Relation]]]:
    """加载 data_dir 下所有领域及其完整本体/实例/关系。

    Usage:
        >>> from pathlib import Path
        >>> load_all_domains(Path("/nonexistent"))
        []
    """
    result = []
    for d in get_domain_dirs(data_dir):
        domain = load_domain(d)
        ontologies = load_ontologies(d)
        instances = load_instances(d)
        relations = load_relations(d)
        result.append((d, domain, ontologies, instances, relations))
    return result
