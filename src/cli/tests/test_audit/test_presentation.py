from app.audit.models import AuditMode
from app.audit.renderer import ReportSectionDef, ReportTemplate, DEFAULT_REPORT_TEMPLATE


class TestReportSectionDef:
    def test_create(self):
        s = ReportSectionDef("need_confirm", "标题", "描述")
        assert s.key == "need_confirm"
        assert s.header == "标题"
        assert s.description == "描述"


class TestReportTemplate:
    def test_default_full_sections(self):
        sections = DEFAULT_REPORT_TEMPLATE.sections_for(AuditMode.FULL)
        assert len(sections) == 2
        assert sections[0].key == "need_confirm"

    def test_default_simple_sections(self):
        sections = DEFAULT_REPORT_TEMPLATE.sections_for(AuditMode.SIMPLE)
        assert sections[0].header == "建议关注"

    def test_tail_for_simple(self):
        msg = DEFAULT_REPORT_TEMPLATE.tail_for(AuditMode.SIMPLE, False, False)
        assert "快速检查模式" in msg

    def test_tail_for_need_confirm(self):
        msg = DEFAULT_REPORT_TEMPLATE.tail_for(AuditMode.FULL, True, False)
        assert "请先处理" in msg

    def test_sections_for_unknown_mode_falls_back_to_full(self):
        tmpl = ReportTemplate(
            sections_full=[ReportSectionDef("a", "A", "d")],
            sections_simple=[],
            clean_message="",
            summary_header="",
            tail_messages={},
        )
        class UnknownMode:
            value = "unknown"
        sections = tmpl.sections_for(UnknownMode())
        assert len(sections) == 1
        assert sections[0].key == "a"
