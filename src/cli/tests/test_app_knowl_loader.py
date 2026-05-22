"""Direct tests for app.knowl_loader using valid UUIDs."""

import uuid
from pathlib import Path

from tests.conftest import FIXTURE_DIR
from app.knowl_loader import (
    load_json,
    get_domain_dirs,
    load_domain,
    load_ontologies,
    load_instances,
    load_all_domains,
)


_DOMAIN_ID = "00000000-0000-0000-0000-000000000001"
_ONTO_ID = "00000000-0000-0000-0000-000000000010"
_INST_ID = "00000000-0000-0000-0000-000000000020"


def _write_fixtures(base: Path, did: str = _DOMAIN_ID):
    domain_dir = base / "test-domain"
    domain_dir.mkdir()
    (domain_dir / "domain.json").write_text(
        f'{{"id": "{did}", "name": "test", "label": "test", "description": "desc"}}',
        encoding="utf-8",
    )
    (domain_dir / "ontologies.json").write_text(
        f'{{"ontologies": [{{"id": "{_ONTO_ID}", "name": "onto1", "label": "本体1", "description": "本体1描述"}}]}}',
        encoding="utf-8",
    )
    (domain_dir / "instances.json").write_text(
        f'{{"instances": [{{"id": "{_INST_ID}", "name": "inst1", "label": "实例1", "description": "实例1描述"}}]}}',
        encoding="utf-8",
    )
    (domain_dir / "relations.json").write_text('{"relations": []}', encoding="utf-8")
    return domain_dir


class TestAppKnowlLoader:
    def test_load_json(self, tmp_path):
        p = tmp_path / "test.json"
        p.write_text('{"key": "value"}', encoding="utf-8")
        assert load_json(p) == {"key": "value"}

    def test_get_domain_dirs_fixtures(self):
        dirs = get_domain_dirs(FIXTURE_DIR)
        assert len(dirs) == 4

    def test_get_domain_dirs_nonexistent(self):
        assert get_domain_dirs(Path("/nonexistent")) == []

    def test_load_domain_success(self, tmp_path):
        dd = _write_fixtures(tmp_path)
        domain = load_domain(dd)
        assert domain is not None
        assert domain.id == uuid.UUID(_DOMAIN_ID)
        assert domain.name == "test"

    def test_load_domain_invalid_returns_none(self, tmp_path):
        dd = tmp_path / "bad"
        dd.mkdir()
        (dd / "domain.json").write_text(
            '{"id": "not-a-uuid", "name": "bad"}', encoding="utf-8"
        )
        domain = load_domain(dd)
        assert domain is None

    def test_load_ontologies_success(self, tmp_path):
        dd = _write_fixtures(tmp_path)
        ontologies = load_ontologies(dd)
        assert len(ontologies) == 1
        assert ontologies[0].id == uuid.UUID(_ONTO_ID)

    def test_load_instances_success(self, tmp_path):
        dd = _write_fixtures(tmp_path)
        instances = load_instances(dd)
        assert len(instances) == 1
        assert instances[0].id == uuid.UUID(_INST_ID)

    def test_load_all_domains_success(self, tmp_path):
        _write_fixtures(tmp_path)
        result = load_all_domains(tmp_path)
        assert len(result) == 1
        d, domain, ontologies, instances = result[0]
        assert domain.id == uuid.UUID(_DOMAIN_ID)
        assert len(ontologies) == 1
        assert len(instances) == 1

    def test_load_all_domains_with_invalid_skips(self, tmp_path):
        dd = _write_fixtures(tmp_path, did="bad-id")
        bad = tmp_path / "also-bad"
        bad.mkdir()
        (bad / "domain.json").write_text(
            '{"id": "not-uuid"}', encoding="utf-8"
        )
        result = load_all_domains(tmp_path)
        assert len(result) == 0

    def test_load_all_domains_nonexistent(self):
        assert load_all_domains(Path("/nonexistent")) == []
