"""测试知识抽取命令"""

from typer.testing import CliRunner
from tests.conftest import SAMPLE_DIR, FIXTURE_DIR


class TestExtract:
    def test_extract_empty_dir(self, tmp_path):
        from app.cli import app
        empty = tmp_path / "empty"
        empty.mkdir()
        result = CliRunner().invoke(app, ["extract", str(empty)])
        assert result.exit_code == 0
        assert "没有 .md 文件" in result.output

    def test_extract_runs_without_api_key(self):
        from app.cli import app
        result = CliRunner().invoke(app, ["extract", str(SAMPLE_DIR)])
        assert result.exit_code == 0
        assert "抽取完成" in result.output or "推荐领域" in result.output

    def test_extract_nonexistent_dir(self):
        from app.cli import app
        result = CliRunner().invoke(app, ["extract", "/nonexistent"])
        assert "不存在" in result.output

    def test_extract_creates_skeleton(self, tmp_path):
        from app.cli import app
        sample = tmp_path / "samples"
        sample.mkdir()
        (sample / "test.md").write_text(
            "这是一份公司治理章程，涉及董事会和股东会。", encoding="utf-8"
        )
        out = tmp_path / "out"
        result = CliRunner().invoke(app, ["extract", str(sample), "--data-dir", str(out)])
        assert result.exit_code == 0
        assert "抽取完成" in result.output or "推荐领域" in result.output or "词汇表" in result.output
