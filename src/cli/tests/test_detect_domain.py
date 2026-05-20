"""测试领域检测 — 基于词汇匹配的文件-领域推荐"""

from pathlib import Path

from tests.conftest import FIXTURE_DIR, SAMPLE_DIR
from app.detectors.detect_domain import run


class TestDetectDomain:
    def test_detect_existing_file(self, capsys):
        sample = SAMPLE_DIR / "basic-charter.md"
        result = run(str(sample), FIXTURE_DIR)
        captured = capsys.readouterr()
        assert result == 0
        assert "basic-charter.md" in captured.out
        assert "doc-std" in captured.out

    def test_detect_returns_scores(self, capsys):
        sample = SAMPLE_DIR / "basic-charter.md"
        run(str(sample), FIXTURE_DIR)
        captured = capsys.readouterr()
        assert "org-gov" in captured.out or "biz-ops" in captured.out

    def test_nonexistent_file_returns_error(self, capsys):
        result = run("/nonexistent/file.md", FIXTURE_DIR)
        captured = capsys.readouterr()
        assert result == 1
        assert "文件不存在" in captured.out

    def test_hr_file_matches_hr_domain(self, capsys):
        sample = SAMPLE_DIR / "human-resignation.md"
        result = run(str(sample), FIXTURE_DIR)
        captured = capsys.readouterr()
        assert result == 0
        assert "hr" in captured.out

    def test_detect_uses_vocabulary_matching(self, capsys):
        sample = SAMPLE_DIR / "basic-charter.md"
        run(str(sample), FIXTURE_DIR)
        captured = capsys.readouterr()
        assert "doc-std" in captured.out
        assert "org-gov" in captured.out
