"""测试知识抽取命令"""

import json
from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner
from tests.conftest import SAMPLE_DIR, FIXTURE_DIR


class FakeChatResponse:
    def __init__(self, content):
        self.content = content


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
        assert "抽取完成" in result.output

    def test_extract_nonexistent_dir(self):
        from app.cli import app
        result = CliRunner().invoke(app, ["extract", "/nonexistent"])
        assert "不存在" in result.output
        assert "确认目录路径" in result.output

    def test_extract_llm_no_api_key(self, tmp_path):
        from app.cli import app
        doc = tmp_path / "test.md"
        doc.write_text("测试内容", encoding="utf-8")
        result = CliRunner().invoke(app, ["extract", "--llm", str(doc)])
        assert result.exit_code == 1
        assert "未设置" in result.output

    def test_extract_llm_calls_llm(self, tmp_path, monkeypatch):
        monkeypatch.setenv("QTCLOUD_KNOWL_LLM_API_KEY", "test-key")
        import importlib
        from app import config
        importlib.reload(config)
        from app.agents.extract import extract_with_llm

        doc = tmp_path / "test.md"
        doc.write_text("这是一份章程，涉及董事会和股东会。", encoding="utf-8")

        with patch("quanttide_agent.LLM") as MockLLM:
            mock_llm = MockLLM.return_value
            mock_llm.complete.return_value = FakeChatResponse(
                json.dumps({"concepts": [{"name": "董事会", "type": "职务"}]}, ensure_ascii=False)
            )
            result = extract_with_llm(str(doc))
            data = json.loads(result)
            assert data["concepts"][0]["name"] == "董事会"

    def test_extract_llm_nonexistent_file(self, tmp_path, monkeypatch):
        monkeypatch.setenv("QTCLOUD_KNOWL_LLM_API_KEY", "test-key")
        import importlib
        from app import config
        importlib.reload(config)
        import app.cli as cli_mod
        importlib.reload(cli_mod)
        result = CliRunner().invoke(cli_mod.app, ["extract", "--llm", str(tmp_path / "nope.md")])
        assert "不存在" in result.output

    def test_extract_llm_prompt_not_found(self, tmp_path, monkeypatch):
        monkeypatch.setenv("QTCLOUD_KNOWL_LLM_API_KEY", "test-key")
        from app.agents.extract import extract_with_llm
        doc = tmp_path / "test.md"
        doc.write_text("内容", encoding="utf-8")
        result = extract_with_llm(str(doc), prompt_name="nonexistent.txt")
        assert "不存在" in result

    def test_extract_llm_missing_prompt_name(self):
        from app.agents.extract import _load_prompt
        assert _load_prompt("nonexistent.txt") is None

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
        assert "抽取完成" in result.output
