from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional


class AuditMode(Enum):
    SIMPLE = "simple"
    FULL = "full"

    @classmethod
    def _missing_(cls, value):  # pragma: no cover
        if isinstance(value, str):
            for member in cls:
                if member.value == value:
                    return member
        return None


@dataclass(frozen=True)
class AuditIssue:
    category: str
    group: str
    label: str
    action: str = ""

    def issue_key(self) -> str:
        return f"{self.category}|{self.group}|{self.label}"


@dataclass(frozen=True)
class AuditDiff:
    fixed: frozenset
    new: frozenset
    pending: frozenset
    previous_timestamp: Optional[str] = None

    @classmethod
    def compute(cls, previous, current, prev_timestamp=None):
        prev_set = frozenset(i.issue_key() for i in previous)
        curr_set = frozenset(i.issue_key() for i in current)
        return cls(
            fixed=prev_set - curr_set,
            new=curr_set - prev_set,
            pending=prev_set & curr_set,
            previous_timestamp=prev_timestamp,
        )

    @property
    def has_changes(self) -> bool:
        return bool(self.fixed or self.new or self.pending)

    @property
    def is_identical(self) -> bool:
        return not self.has_changes


@dataclass
class AuditState:
    mode: AuditMode
    issues: list
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass(frozen=True)
class IssueGroup:
    group_name: str
    issues: list

    @classmethod
    def from_issues(cls, issues):
        groups = {}
        for i in issues:
            groups.setdefault(i.group, []).append(i)
        return [cls(group_name=name, issues=lst) for name, lst in groups.items()]


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


@dataclass
class KnowledgeBaseStats:
    data_dir: Path
    domains: list
    ontology_count: int
    instance_count: int

    @property
    def domain_count(self) -> int:
        return len(self.domains)

    @property
    def has_domains(self) -> bool:
        return bool(self.domains)


@dataclass
class AuditReport:
    need_confirm: list
    auto_fixable: list
    suggestions: list
    mode: AuditMode

    @classmethod
    def from_raw(cls, need_confirm, auto_fixable, suggestions, mode):
        if mode == AuditMode.SIMPLE:
            suggestions = need_confirm + suggestions
            need_confirm = auto_fixable
            auto_fixable = []
        return cls(need_confirm=need_confirm, auto_fixable=auto_fixable, suggestions=suggestions, mode=mode)

    @property
    def is_clean(self) -> bool:
        return not self.need_confirm and not self.auto_fixable

    @property
    def exit_code(self) -> int:
        return 0 if self.is_clean else 1

    def section_groups(self, key):
        issues = {"need_confirm": self.need_confirm, "auto_fixable": self.auto_fixable, "suggestions": self.suggestions}.get(key, [])
        return IssueGroup.from_issues(issues)
