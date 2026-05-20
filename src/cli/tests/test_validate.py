from app.config import FIXTURE_DIR
from app.validators.validate import run


class TestValidate:
    def test_validate_passes(self, capsys):
        result = run(FIXTURE_DIR)
        captured = capsys.readouterr()
        assert result == 0
        assert "[OK]" in captured.out
        assert "全部验证通过" in captured.out

    def test_validate_lists_all_domains(self, capsys):
        result = run(FIXTURE_DIR)
        captured = capsys.readouterr()
        assert result == 0
        for domain in ("biz-ops", "doc-std", "hr", "org-gov"):
            assert domain in captured.out
