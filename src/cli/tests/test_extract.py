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

    def test_extract_no_api_key(self, monkeypatch):
        monkeypatch.setattr("app.cli.settings.sample_home", None)
        monkeypatch.setattr("app.agents.extract.settings.llm_api_key", "")
        from app.cli import app
        result = CliRunner().invoke(app, ["extract", str(SAMPLE_DIR)])
        assert "API key 未配置" in result.output

    def test_extract_nonexistent_dir(self, monkeypatch):
        monkeypatch.setattr("app.agents.extract.settings.llm_api_key", "")
        from app.cli import app
        result = CliRunner().invoke(app, ["extract", "/nonexistent"])
        assert "不存在" in result.output
