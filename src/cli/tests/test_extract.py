"""测试知识抽取命令"""

import json
from pathlib import Path
from unittest.mock import patch, MagicMock

from typer.testing import CliRunner
from app.cli import app
from tests.conftest import SAMPLE_DIR


SAMPLE_LLM_DATA = {
    "domain": {"id": "test-domain", "name": "test-domain", "label": "测试领域", "description": ""},
    "ontologies": [
        {"id": "test-onto-1", "name": "test-onto-1", "label": "测试本体", "description": "测试本体"},
    ],
    "instances": [
        {"id": "test-inst-1", "name": "test-inst-1", "label": "测试实例", "description": "测试实例", "ontology": "test-onto-1"},
    ],
}

SAMPLE_LLM_RESPONSE = json.dumps(SAMPLE_LLM_DATA, ensure_ascii=False)


class TestExtract:
    """知识抽取命令测试"""

    # === extract() 函数测试 ===

    def test_extract_file_not_found(self):
        from app.extract import extract
        result = extract("/nonexistent/test.md")
        assert "error" in result
        assert "不存在" in result["error"]

    def test_extract_non_md_file(self, tmp_path):
        from app.extract import extract
        f = tmp_path / "test.txt"
        f.write_text("content", encoding="utf-8")
        result = extract(str(f))
        assert "error" in result
        assert "仅支持 .md" in result["error"]

    def test_extract_missing_prompt(self, tmp_path):
        from app.extract import extract
        f = tmp_path / "test.md"
        f.write_text("content", encoding="utf-8")
        result = extract(str(f), prompt_template="nonexistent.txt")
        assert "error" in result
        assert "prompt 模板不存在" in result["error"]

    def test_extract_no_api_key(self, tmp_path):
        from app.extract import extract
        f = tmp_path / "test.md"
        f.write_text("content", encoding="utf-8")
        result = extract(str(f))
        assert "error" in result
        assert "未设置 LLM API Key" in result["error"]

    def test_extract_calls_llm(self, tmp_path):
        from app.extract import extract, settings

        f = tmp_path / "test.md"
        f.write_text("关于董事会与股东会的治理章程", encoding="utf-8")

        mock_resp = MagicMock()
        mock_resp.content = SAMPLE_LLM_RESPONSE

        with patch("quanttide_agent.LLM") as MockLLM:
            MockLLM.return_value.complete.return_value = mock_resp
            old_key = settings.llm_api_key
            settings.llm_api_key = "test-key"
            try:
                result = extract(str(f))
            finally:
                settings.llm_api_key = old_key

        assert "error" not in result
        assert result["domain"]["label"] == "测试领域"
        assert len(result["ontologies"]) == 1
        assert result["ontologies"][0]["label"] == "测试本体"
        assert len(result["instances"]) == 1
        assert result["instances"][0]["label"] == "测试实例"

    def test_extract_llm_json_error(self, tmp_path):
        from app.extract import extract, settings

        f = tmp_path / "test.md"
        f.write_text("content", encoding="utf-8")

        mock_resp = MagicMock()
        mock_resp.content = "这不是 JSON"

        with patch("quanttide_agent.LLM") as MockLLM:
            MockLLM.return_value.complete.return_value = mock_resp
            old_key = settings.llm_api_key
            settings.llm_api_key = "test-key"
            try:
                result = extract(str(f))
            finally:
                settings.llm_api_key = old_key

        assert "error" in result
        assert "解析失败" in result["error"]

    def test_extract_keeps_ontology_field(self, tmp_path):
        """验证实例的 ontology 字段被保留。"""
        from app.extract import extract, settings

        f = tmp_path / "test.md"
        f.write_text("content", encoding="utf-8")

        data = {
            "domain": {"id": "d", "name": "d", "label": "D", "description": ""},
            "ontologies": [{"id": "onto-1", "name": "onto-1", "label": "O1", "description": ""}],
            "instances": [{"id": "i1", "name": "i1", "label": "I1", "description": "", "ontology": "onto-1"}],
        }
        mock_resp = MagicMock()
        mock_resp.content = json.dumps(data, ensure_ascii=False)

        with patch("quanttide_agent.LLM") as MockLLM:
            MockLLM.return_value.complete.return_value = mock_resp
            old_key = settings.llm_api_key
            settings.llm_api_key = "test-key"
            try:
                result = extract(str(f))
            finally:
                settings.llm_api_key = old_key

        assert result["instances"][0]["ontology"] == "onto-1"

    def test_extract_strips_code_fences(self, tmp_path):
        from app.extract import extract, settings

        f = tmp_path / "test.md"
        f.write_text("content", encoding="utf-8")
        wrapped = "```json\n" + '{"domain": {"id": "d1"}, "ontologies": [], "instances": []}\n' + "```"
        mock_resp = MagicMock()
        mock_resp.content = wrapped

        with patch("quanttide_agent.LLM") as MockLLM:
            MockLLM.return_value.complete.return_value = mock_resp
            old_key = settings.llm_api_key
            settings.llm_api_key = "test-key"
            try:
                result = extract(str(f))
            finally:
                settings.llm_api_key = old_key

        assert result["domain"]["label"] == ""

    # === CLI 集成测试 ===

    def test_cli_empty_dir(self, tmp_path):
        empty = tmp_path / "empty"
        empty.mkdir()
        result = CliRunner().invoke(app, ["--source", str(empty)])
        assert result.exit_code == 1
        assert "没有 .md 文件" in result.output

    def test_cli_nonexistent_path(self):
        result = CliRunner().invoke(app, ["--source", "/nonexistent"])
        assert result.exit_code == 1
        assert "不存在" in result.output

    def test_cli_missing_source(self):
        result = CliRunner().invoke(app, [])
        assert result.exit_code == 1

    def test_cli_single_file_writes_json(self, tmp_path):
        f = tmp_path / "test.md"
        f.write_text("content", encoding="utf-8")
        out = tmp_path / "out"

        with patch("app.extract.extract") as mock_extract:
            mock_extract.return_value = {
                "domain": {"id": "d", "name": "d", "label": "D", "description": ""},
                "ontologies": [],
                "instances": [],
            }
            result = CliRunner().invoke(app, ["--source", str(f), "--data-dir", str(out)])

        assert result.exit_code == 0
        assert (out / "test.json").exists()
        assert json.loads((out / "test.json").read_text())["domain"]["label"] == "D"

    # === _load_prompt 函数测试 ===

    def test_load_prompt_missing(self):
        from app.extract import _load_prompt
        assert _load_prompt("nonexistent.txt") is None

    def test_load_prompt_found(self):
        from app.extract import _load_prompt
        content = _load_prompt("extract.txt")
        assert content is not None
        assert "{document}" in content

    # === _strip_fences 测试 ===

    def test_strip_fences_json(self):
        from app.extract import _strip_fences
        assert _strip_fences("```json\n{\"a\": 1}\n```") == "{\"a\": 1}"

    def test_strip_fences_no_fences(self):
        from app.extract import _strip_fences
        assert _strip_fences("plain text") == "plain text"

    def test_strip_fences_leading_only(self):
        from app.extract import _strip_fences
        assert _strip_fences("```\ncontent") == "content"

    def test_strip_fences_trailing_only(self):
        from app.extract import _strip_fences
        assert _strip_fences("content\n```") == "content"

    # === run() 目录模式 ===

    def test_run_dir_creates_files(self, tmp_path):
        from unittest.mock import patch
        from app.extract import run

        sdir = tmp_path / "samples"
        sdir.mkdir()
        (sdir / "test.md").write_text("content", encoding="utf-8")
        out = tmp_path / "out"

        with patch("app.extract.extract") as mock_extract:
            mock_extract.return_value = {
                "domain": {"id": "the-domain", "name": "the-domain", "label": "领域", "description": ""},
                "ontologies": [{"id": "o1", "name": "o1", "label": "O1", "description": ""}],
                "instances": [{"id": "i1", "name": "i1", "label": "I1", "description": "", "ontology": "o1"}],
            }
            result = run(source=str(sdir), data_dir=str(out))

        assert result == 0
        assert (out / "the-domain" / "domain.json").exists()
        assert (out / "the-domain" / "ontologies.json").exists()
        assert (out / "the-domain" / "instances.json").exists()

    def test_run_skips_empty_domain_id(self, tmp_path):
        from unittest.mock import patch
        from app.extract import run

        sdir = tmp_path / "samples"
        sdir.mkdir()
        (sdir / "test.md").write_text("content", encoding="utf-8")

        with patch("app.extract.extract") as mock_extract:
            mock_extract.return_value = {
                "domain": {"id": "", "name": "", "label": "", "description": ""},
                "ontologies": [],
                "instances": [],
            }
            result = run(source=str(sdir), data_dir=str(tmp_path / "out"))
        assert result == 0
