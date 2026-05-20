"""测试全量审计命令"""

import json
from datetime import datetime
from typer.testing import CliRunner
from tests.conftest import FIXTURE_DIR, SAMPLE_DIR
from app.agents.audit import _collect_issues, _compute_diff, _load_audit_state, _save_audit_state


class TestAuditState:
    def test_collect_issues_flattens_all_categories(self):
        issues = _collect_issues(
            [("g1", [("l1", "a1")])],
            [("g2", [("l2", "a2")])],
            [("g3", [("l3", "a3")])],
        )
        assert len(issues) == 3
        assert issues[0]["category"] == "need_confirm"
        assert issues[1]["category"] == "auto_fixable"
        assert issues[2]["category"] == "suggestions"

    def test_compute_diff_all_cases(self):
        prev = [{"label": "a"}, {"label": "b"}, {"label": "c"}]
        curr = [{"label": "b"}, {"label": "c"}, {"label": "d"}]
        fixed, new, pending, _, _ = _compute_diff(prev, curr)
        assert fixed == {"a"}
        assert new == {"d"}
        assert pending == {"b", "c"}

    def test_save_and_load_audit_state(self, tmp_path):
        issues = [{"category": "need_confirm", "group": "t", "label": "l"}]
        _save_audit_state(tmp_path, issues, "full")
        state = _load_audit_state(tmp_path)
        assert state is not None
        assert state["mode"] == "full"
        assert len(state["issues"]) == 1

    def test_load_nonexistent_returns_none(self, tmp_path):
        assert _load_audit_state(tmp_path) is None

    def test_load_corrupted_returns_none(self, tmp_path):
        (tmp_path / ".audit.json").write_text("{invalid}", encoding="utf-8")
        assert _load_audit_state(tmp_path) is None


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
