from pathlib import Path
from tests.conftest import FIXTURE_DIR
from app.validators.validate import run


class TestValidate:
    def test_validate_passes(self, capsys):
        result = run(FIXTURE_DIR)
        captured = capsys.readouterr()
        assert "全部验证通过" in result
        assert "[OK]" in captured.out

    def test_validate_lists_all_domains(self, capsys):
        result = run(FIXTURE_DIR)
        captured = capsys.readouterr()
        assert "全部验证通过" in result
        for domain in ("biz-ops", "doc-std", "hr", "org-gov"):
            assert domain in captured.out

    def test_validate_missing_dir(self, capsys):
        result = run("/nonexistent")
        captured = capsys.readouterr()
        assert "数据目录不存在" in result

    def test_detects_missing_file(self, tmp_path, capsys):
        domain_dir = tmp_path / "bad-domain"
        domain_dir.mkdir()
        (domain_dir / "domain.json").write_text(
            '{"id": "bad", "name": "bad", "vocabulary": []}', encoding="utf-8"
        )
        (domain_dir / "ontologies.json").write_text("{}", encoding="utf-8")
        result = run(tmp_path)
        captured = capsys.readouterr()
        assert "[MISS]" in captured.out
        assert "instances.json" in captured.out
