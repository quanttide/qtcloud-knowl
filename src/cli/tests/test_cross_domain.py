"""测试跨领域关系覆盖率报告"""

from tests.conftest import FIXTURE_DIR
from app.reporters.cross_domain import run


class TestCrossDomain:
    def test_run_returns_zero(self):
        result = run(FIXTURE_DIR)
        assert result == 0

    def test_output_contains_report_header(self, capsys):
        run(FIXTURE_DIR)
        captured = capsys.readouterr()
        assert "跨领域关系覆盖率报告" in captured.out

    def test_output_contains_all_domains(self, capsys):
        run(FIXTURE_DIR)
        captured = capsys.readouterr()
        for domain in ("biz-ops", "doc-std", "hr", "org-gov"):
            assert domain in captured.out

    def test_output_shows_cross_relation_count(self, capsys):
        run(FIXTURE_DIR)
        captured = capsys.readouterr()
        assert "跨域关系数" in captured.out or "跨域关系总数" in captured.out

    def test_output_shows_pass_fail_judgment(self, capsys):
        run(FIXTURE_DIR)
        captured = capsys.readouterr()
        assert "达标" in captured.out or "未达标" in captured.out

    def test_domain_with_one_cross_shows_unfulfilled(self, tmp_path, capsys):
        domain_dir = tmp_path / "test-domain"
        domain_dir.mkdir()
        (domain_dir / "domain.json").write_text(
            '{"id": "test", "name": "test", "vocabulary": []}', encoding="utf-8"
        )
        (domain_dir / "ontologies.json").write_text(
            '{"ontologies": [{"id": "o1", "name": "o1"}]}', encoding="utf-8"
        )
        (domain_dir / "instances.json").write_text('{"instances": []}', encoding="utf-8")
        (domain_dir / "relations.json").write_text(
            '{"relations": [{"id": "r1", "source_ontology": "o1", "target_ontology": "other:o2"}]}',
            encoding="utf-8",
        )
        result = run(tmp_path)
        captured = capsys.readouterr()
        assert result == 0
        assert "未达标" in captured.out
