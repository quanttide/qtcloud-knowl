import json
from pathlib import Path

import pytest

from qtcloud_knowl.loader import (
    get_domain_dirs,
    load_all_domains,
    load_domain,
    load_instances,
    load_json,
    load_ontologies,
    load_relations,
)


class TestLoadJson:
    def test_load_valid(self, tmp_path):
        p = tmp_path / "test.json"
        with open(p, "w", encoding="utf-8") as f:
            json.dump({"a": 1}, f)
        assert load_json(p) == {"a": 1}

    def test_raises_on_missing(self, tmp_path):
        with pytest.raises((FileNotFoundError, json.JSONDecodeError)):
            load_json(tmp_path / "missing.json")


class TestGetDomainDirs:
    def test_empty_on_nonexistent(self):
        assert get_domain_dirs(Path("/nonexistent")) == []

    def test_empty_on_empty_dir(self, tmp_path):
        assert get_domain_dirs(tmp_path) == []

    def test_ignores_dir_without_domain_json(self, tmp_path):
        (tmp_path / "no-domain-file").mkdir()
        assert get_domain_dirs(tmp_path) == []

    def test_finds_domain_dir(self, tmp_path):
        d = tmp_path / "my-domain"
        d.mkdir()
        with open(d / "domain.json", "w", encoding="utf-8") as f:
            json.dump({}, f)
        result = get_domain_dirs(tmp_path)
        assert result == [d]


class TestLoadDomain:
    def test_load(self, tmp_path):
        d = tmp_path / "t"
        d.mkdir()
        with open(d / "domain.json", "w", encoding="utf-8") as f:
            json.dump({"id": "t1", "name": "Test", "vocabulary": ["v1"]}, f)
        domain = load_domain(d)
        assert domain.id == "t1"
        assert domain.name == "Test"
        assert "v1" in domain.vocabulary

    def test_fallback_to_dir_name(self, tmp_path):
        d = tmp_path / "fallback-name"
        d.mkdir()
        with open(d / "domain.json", "w", encoding="utf-8") as f:
            json.dump({}, f)
        domain = load_domain(d)
        assert domain.id == "fallback-name"


class TestLoadOntologies:
    def test_load(self, tmp_path):
        d = tmp_path / "t"
        d.mkdir()
        with open(d / "ontologies.json", "w", encoding="utf-8") as f:
            json.dump({"ontologies": [{"id": "o1", "name": "onto1", "label": "本体1"}]}, f)
        ontos = load_ontologies(d)
        assert len(ontos) == 1
        assert ontos[0].name == "onto1"

    def test_empty_list(self, tmp_path):
        d = tmp_path / "t"
        d.mkdir()
        with open(d / "ontologies.json", "w", encoding="utf-8") as f:
            json.dump({"ontologies": []}, f)
        assert load_ontologies(d) == []


class TestLoadInstances:
    def test_load(self, tmp_path):
        d = tmp_path / "t"
        d.mkdir()
        with open(d / "instances.json", "w", encoding="utf-8") as f:
            json.dump({"instances": [{"id": "i1", "subject": "subj", "extra": "val"}]}, f)
        insts = load_instances(d)
        assert len(insts) == 1
        assert insts[0].subject == "subj"
        assert insts[0].data["extra"] == "val"

    def test_empty(self, tmp_path):
        d = tmp_path / "t"
        d.mkdir()
        with open(d / "instances.json", "w", encoding="utf-8") as f:
            json.dump({"instances": []}, f)
        assert load_instances(d) == []


class TestLoadRelations:
    def test_load(self, tmp_path):
        d = tmp_path / "t"
        d.mkdir()
        with open(d / "relations.json", "w", encoding="utf-8") as f:
            json.dump({"relations": [{"id": "r1", "source_ontology": "o1", "target_ontology": "o2", "relation": "depends"}]}, f)
        rels = load_relations(d)
        assert len(rels) == 1
        assert rels[0].relation == "depends"

    def test_empty(self, tmp_path):
        d = tmp_path / "t"
        d.mkdir()
        with open(d / "relations.json", "w", encoding="utf-8") as f:
            json.dump({"relations": []}, f)
        assert load_relations(d) == []


class TestLoadAllDomains:
    def test_load_multiple(self, tmp_path):
        for name in ["a", "b"]:
            d = tmp_path / name
            d.mkdir()
            for fname in ["domain.json", "ontologies.json", "instances.json", "relations.json"]:
                with open(d / fname, "w", encoding="utf-8") as f:
                    json.dump({fname.replace(".json", "s"): []} if fname != "domain.json" else {"id": name, "name": name}, f)
        result = load_all_domains(tmp_path)
        assert len(result) == 2
        names = {d[1].id for d in result}
        assert names == {"a", "b"}

    def test_empty_on_nonexistent(self):
        assert load_all_domains(Path("/nonexistent")) == []

    def test_integration_with_fixture(self, fixture_dir):
        """使用 conftest 中定义的完整领域数据做集成测试。"""
        result = load_all_domains(fixture_dir)
        assert len(result) == 1

        path, domain, ontologies, instances, relations = result[0]
        assert domain.id == "biz-ops"
        assert len(ontologies) == 2
        assert len(instances) == 2
        assert len(relations) == 1
        assert instances[1].data.get("amount") == "100万"
