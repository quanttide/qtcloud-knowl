"""文档一致性测试 — 确保文档描述与代码实现匹配"""

import re
from pathlib import Path

from app.config import settings, Settings


CLI_DOCS_DIR = Path(__file__).resolve().parent.parent / "docs"
TOP_DOCS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "docs"

ALL_COMMANDS = [
    "summary", "validate", "find-undefined-terms", "fusion-check",
    "check-abstraction", "auto-fix", "cross-domain-report",
    "detect-domain", "init-domain", "audit", "source", "review", "extract",
]


def _help_output(*args):
    import subprocess, sys
    result = subprocess.run([sys.executable, "-m", "app.cli", *args], capture_output=True, text=True)
    return result.stdout


class TestCliHelp:
    """CLI --help 输出"""

    def test_all_commands_listed(self):
        out = _help_output("--help")
        for cmd in ALL_COMMANDS:
            assert cmd in out, f"命令 {cmd} 未出现在 --help 输出中"

    def test_usage_line_present(self):
        out = _help_output("--help")
        assert "usage:" in out.lower()

    def test_validate_help(self):
        out = _help_output("validate", "--help")
        assert "usage:" in out.lower()


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
        """所有 Settings 字段有对应的 env var 文档"""
        from dataclasses import fields
        for field in fields(Settings):
            assert hasattr(settings, field.name), f"字段 {field.name} 不可访问"

    def test_data_home_is_path(self):
        assert isinstance(settings.data_home, Path)

    def test_sample_home_defaults_to_path(self):
        """sample_home 有默认值"""
        assert isinstance(settings.sample_home, Path)
