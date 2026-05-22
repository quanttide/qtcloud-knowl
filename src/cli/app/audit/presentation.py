from dataclasses import dataclass

from app.audit.models import AuditMode


@dataclass(frozen=True)
class ReportSectionDef:
    key: str
    header: str
    description: str


@dataclass(frozen=True)
class ReportTemplate:
    sections_full: list
    sections_simple: list
    clean_message: str
    summary_header: str
    tail_messages: dict

    def sections_for(self, mode):
        return self.sections_simple if mode == AuditMode.SIMPLE else self.sections_full

    def tail_for(self, mode, has_confirm, has_fixable):
        if mode == AuditMode.SIMPLE:
            return self.tail_messages.get("simple", "")
        if has_confirm:
            return self.tail_messages.get("need_confirm", "")
        if has_fixable:
            return self.tail_messages.get("auto_fixable", "")
        return ""  # pragma: no cover


DEFAULT_REPORT_TEMPLATE = ReportTemplate(
    sections_full=[
        ReportSectionDef("need_confirm", "需要你确认的问题", "以下问题平台无法自动判断，需要你决定如何处理。"),
        ReportSectionDef("auto_fixable", "平台发现的问题", "以下问题平台已识别，可通过自动修复处理。"),
    ],
    sections_simple=[
        ReportSectionDef("need_confirm", "建议关注", "以下问题可由平台自动修复，无需手动处理。"),
        ReportSectionDef("auto_fixable", "平台发现的问题", "以下问题平台已识别，可通过自动修复处理。"),
    ],
    clean_message="✓ 未发现问题，知识库结构良好。",
    summary_header="  汇总",
    tail_messages={
        "simple": "当前为快速检查模式，运行 qtcloud-knowl audit --mode full 进行全面审计。",
        "need_confirm": "请先处理「需要你确认的问题」，其他问题可并行处理。",
        "auto_fixable": "运行 qtcloud-knowl auto-fix 自动修复平台发现的问题。",
    },
)
