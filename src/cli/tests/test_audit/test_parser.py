from app.audit.parser import (
    ToolOutputParser,
    _parse_miss,
    _parse_fail,
    _parse_term,
    _parse_confirm,
    _parse_abstraction,
)


class TestParseMiss:
    def test_with_domain(self):
        result = _parse_miss("[MISS] ontologies.json", "org-gov", "/data")
        assert result is not None
        assert "缺少文件" in result.label
        assert "ontologies.json" in result.label

    def test_without_domain(self):
        result = _parse_miss("[MISS] ontologies.json", None, None)
        assert result is not None
        assert "auto-fix" in result.action

    def test_no_match(self):
        assert _parse_miss("[OK] domain.json", None, None) is None


class TestParseFail:
    def test_with_domain(self):
        result = _parse_fail("[FAIL] domain.json - format error", "org-gov", "/data")
        assert result is not None
        assert "JSON 格式错误" in result.label

    def test_without_domain(self):
        result = _parse_fail("[FAIL] domain.json - format error", None, None)
        assert result is not None

    def test_no_match(self):
        assert _parse_fail("[OK] domain.json", None, None) is None


class TestParseTerm:
    def test_matches(self):
        result = _parse_term("使用了术语 项目经理", None, None)
        assert result is not None
        assert "术语" in result.action

    def test_no_match(self):
        assert _parse_term("正常文本", None, None) is None


class TestParseConfirm:
    def test_matches(self):
        result = _parse_confirm("【需人确认】请检查此引用", None, None)
        assert result is not None
        assert "请检查此引用" in result.label

    def test_no_match(self):
        assert _parse_confirm("正常文本", None, None) is None


class TestParseAbstraction:
    def test_with_domain(self):
        result = _parse_abstraction("[检测到] onto1: [具体角色名]", "org-gov", "/data")
        assert result is not None
        assert "onto1" in result.label

    def test_without_domain(self):
        result = _parse_abstraction("[检测到] onto1: [信号]", None, None)
        assert result is not None

    def test_no_match(self):
        assert _parse_abstraction("[OK] onto1", None, None) is None


class TestToolOutputParser:
    def test_parse_empty(self):
        parser = ToolOutputParser()
        assert parser.parse("", None) == []

    def test_parse_section_header_tracking(self):
        parser = ToolOutputParser()
        output = "=== org-gov ===\n[MISS] ontologies.json\n"
        issues = parser.parse(output, "/data")
        assert len(issues) == 1
        assert "org-gov" in issues[0].action

    def test_parse_all_types(self):
        parser = ToolOutputParser()
        output = (
            "=== d1 ===\n"
            "[MISS] f1\n"
            "[FAIL] f2 - bad json\n"
            "使用了术语 项目经理\n"
            "【需人确认】引用 X\n"
            "[检测到] onto1: [具体角色名]\n"
        )
        issues = parser.parse(output, "/data")
        assert len(issues) == 5

    def test_has_issue_true(self):
        parser = ToolOutputParser()
        assert parser.has_issue("[MISS] file")
        assert parser.has_issue("[FAIL] file")
        assert parser.has_issue("[检测到] sig")
        assert parser.has_issue("使用了术语 x")
        assert parser.has_issue("需人确认")

    def test_has_issue_false(self):
        parser = ToolOutputParser()
        assert not parser.has_issue("[OK] file")
        assert not parser.has_issue("全部术语已有定义")
