from pathlib import Path
from tests.conftest import FIXTURE_DIR
from app.loader import load_all_domains, get_domain_dirs, load_json


class TestLoader:
    def test_load_all_domains(self):
        domains = load_all_domains(FIXTURE_DIR)
        assert len(domains) == 4
        names = {d[1].id for d in domains}
        assert names == {"biz-ops", "doc-std", "hr", "org-gov"}

    def test_each_domain_has_required_files(self):
        for d, domain, ontologies, instances, relations in load_all_domains(FIXTURE_DIR):
            assert len(ontologies) >= 1
            assert len(instances) >= 1

    def test_empty_dir_returns_empty(self, tmp_path):
        empty = tmp_path / "empty"
        empty.mkdir()
        result = get_domain_dirs(empty)
        assert result == []

    def test_nonexistent_dir_returns_empty(self):
        result = get_domain_dirs(Path("/nonexistent/path"))
        assert result == []

    def test_load_json_raises_on_missing(self, tmp_path):
        import json
        missing = tmp_path / "missing.json"
        try:
            load_json(missing)
            assert False, "should have raised"
        except (FileNotFoundError, json.JSONDecodeError):
            pass
