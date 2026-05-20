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
