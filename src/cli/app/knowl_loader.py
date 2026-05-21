"""知识库加载器 — 读取目录结构中的 JSON 文件。"""

import json
import uuid
from pathlib import Path

from pydantic import ValidationError
from quanttide_knowl.models import Domain, Instance, Ontology


def load_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def get_domain_dirs(data_dir: Path) -> list[Path]:
    if not data_dir.exists():
        return []
    return sorted(
        d for d in data_dir.iterdir() if d.is_dir() and (d / "domain.json").exists()
    )


def load_domain(domain_dir: Path) -> Domain | None:
    data = load_json(domain_dir / "domain.json")
    try:
        return Domain(
            id=data.get("id", domain_dir.name),
            name=data.get("name", ""),
            label=data.get("label", ""),
            description=data.get("description", ""),
        )
    except ValidationError:
        return None


def load_ontologies(domain_dir: Path) -> list[Ontology]:
    data = load_json(domain_dir / "ontologies.json")
    return [
        Ontology(
            id=o.get("id", ""),
            name=o.get("name", ""),
            label=o.get("label", ""),
            description=o.get("description", ""),
        )
        for o in data.get("ontologies", [])
    ]


def load_instances(domain_dir: Path) -> list[Instance]:
    data = load_json(domain_dir / "instances.json")
    return [
        Instance(
            id=inst.get("id", ""),
            name=inst.get("name", ""),
            label=inst.get("label", ""),
            description=inst.get("description", ""),
        )
        for inst in data.get("instances", [])
    ]


def load_all_domains(data_dir: Path):
    result = []
    for d in get_domain_dirs(data_dir):
        domain = load_domain(d)
        if domain is None:
            continue
        ontologies = load_ontologies(d)
        instances = load_instances(d)
        result.append((d, domain, ontologies, instances))
    return result
