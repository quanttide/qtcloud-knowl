"""文档一致性测试 — 确保文档描述与代码实现匹配"""

from pathlib import Path

from app.config import settings, Settings


CLI_DOCS_DIR = Path(__file__).resolve().parent.parent / "docs"
TOP_DOCS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "docs"


class TestCliHelp:
    """CLI --help 输出与文档一致"""

    def test_extract_command_listed(self):
        from app.cli import app
        from typer.testing import CliRunner

        runner = CliRunner()
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "extract" in result.output


class TestStorageDoc:
    """顶层 docs/storage.md 与环境变量一致"""

    def test_data_home_env_var_documented(self):
        doc = (TOP_DOCS_DIR / "storage.md").read_text(encoding="utf-8")
        assert "QTCLOUD_KNOWL_DATA_HOME" in doc
        assert hasattr(settings, "data_home")

    def test_sample_home_env_var_documented(self):
        doc = (TOP_DOCS_DIR / "storage.md").read_text(encoding="utf-8")
        assert "QTCLOUD_KNOWL_SAMPLE_HOME" in doc
        assert hasattr(settings, "sample_home")

    def test_cli_docs_exist(self):
        for name in ("index.md", "commands.md", "config.md"):
            assert (CLI_DOCS_DIR / name).exists(), f"缺失文档: {name}"


class TestSettingsDoc:
    """Settings 字段描述与文档一致"""

    def test_settings_fields_match_env_prefix(self):
        for field_name in Settings.model_fields:
            assert field_name in dir(settings), f"字段 {field_name} 不可访问"

    def test_data_home_is_path(self):
        assert isinstance(settings.data_home, Path)

    def test_sample_home_defaults_to_path(self):
        assert isinstance(settings.sample_home, Path)
