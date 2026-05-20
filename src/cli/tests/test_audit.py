"""测试全量审计命令"""

import json
from typer.testing import CliRunner
from tests.conftest import FIXTURE_DIR, SAMPLE_DIR


class TestAudit:
    def _invoke(self, data_dir, sample_dir=None, mode=None):
        from app.cli import app
        args = ["audit", str(data_dir)]
        if sample_dir:
            args.extend(["--sample-dir", str(sample_dir)])
        if mode:
            args.extend(["--mode", mode])
        return CliRunner().invoke(app, args)

    def test_audit_with_fixtures(self):
        result = self._invoke(FIXTURE_DIR, SAMPLE_DIR)
        assert "知识库质量审计报告" in result.output
        assert "需要你确认的问题" in result.output or "未发现问题" in result.output

    def test_audit_empty_dir(self, tmp_path):
        empty = tmp_path / "empty"
        empty.mkdir()
        result = self._invoke(empty)
        assert "领域数量: 0" in result.output

    def test_audit_with_json_error(self, tmp_path):
        domain_dir = tmp_path / "bad-domain"
        domain_dir.mkdir()
        (domain_dir / "domain.json").write_text("{invalid}", encoding="utf-8")
        (domain_dir / "ontologies.json").write_text("{}", encoding="utf-8")
        (domain_dir / "instances.json").write_text("{}", encoding="utf-8")
        (domain_dir / "relations.json").write_text("{}", encoding="utf-8")
        result = self._invoke(tmp_path)
        assert "平台发现的问题" in result.output or "需要你确认" in result.output or "未发现问题" in result.output

    def test_audit_mode_simple_shows_label(self):
        result = self._invoke(FIXTURE_DIR, SAMPLE_DIR, mode="simple")
        assert "快速检查模式" in result.output
        assert "当前为快速检查模式" in result.output

    def test_audit_mode_full_shows_label(self):
        result = self._invoke(FIXTURE_DIR, SAMPLE_DIR, mode="full")
        assert "全面审计模式" in result.output

    def test_audit_invalid_mode(self):
        result = self._invoke(FIXTURE_DIR, mode="invalid")
        assert "不支持的审计模式" in result.output
