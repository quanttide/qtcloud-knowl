from pathlib import Path
from tests.conftest import FIXTURE_DIR
from app.reporters.summary import run


class TestSummary:
    def test_summary_outputs(self, capsys):
        result = run(FIXTURE_DIR)
        captured = capsys.readouterr()
        assert result == 0
        assert "领域" in captured.out
        assert "本体" in captured.out
        assert "实例" in captured.out

    def test_summary_lists_all_domains(self, capsys):
        result = run(FIXTURE_DIR)
        captured = capsys.readouterr()
        assert result == 0
        for domain in ("biz-ops", "doc-std", "hr", "org-gov"):
            assert domain in captured.out

    def test_summary_shows_counts(self, capsys):
        result = run(FIXTURE_DIR)
        captured = capsys.readouterr()
        assert result == 0
        lines = [l for l in captured.out.split("\n") if l.strip() and not l.startswith("-") and not l.startswith("领域")]
        # line format: "<id> <ont> <inst> <rel> <files>"
        counts = {}
        for line in lines:
            parts = line.split()
            if len(parts) >= 2:
                counts[parts[0]] = int(parts[1])
        assert counts.get("biz-ops") == 4
        assert counts.get("doc-std") == 3
        assert counts.get("hr") == 3
        assert counts.get("org-gov") == 4

    def test_empty_dir_returns_one(self, tmp_path):
        result = run(tmp_path)
        assert result == 1

    def test_empty_dir_prints_message(self, tmp_path, capsys):
        run(tmp_path)
        captured = capsys.readouterr()
        assert "未找到领域数据" in captured.out
