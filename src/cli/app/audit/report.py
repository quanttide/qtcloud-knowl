import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

from app.audit.models import AuditMode, AuditDiff, AuditReport as AuditIssues, IssueGroup, AuditIssue, KnowledgeBaseStats


# ── domain model ──────────────────────────────────────────────────────────

@dataclass
class Report:
    mode: AuditMode
    stats: KnowledgeBaseStats
    issues: AuditIssues
    diff: Optional[AuditDiff] = None
    previous_timestamp: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    @classmethod
    def build(cls, mode, stats, need_confirm, auto_fixable, suggestions, previous_state=None):
        issues = AuditIssues.from_raw(need_confirm, auto_fixable, suggestions, mode)
        diff = None
        prev_ts = None
        if previous_state:
            current_all = issues.need_confirm + issues.auto_fixable + issues.suggestions
            diff = AuditDiff.compute(previous_state.issues, current_all, previous_state.timestamp)
            prev_ts = previous_state.timestamp
        return cls(mode=mode, stats=stats, issues=issues, diff=diff, previous_timestamp=prev_ts)

    @property
    def exit_code(self) -> int:
        return self.issues.exit_code

    # ── rendering ─────────────────────────────────────────────────────────

    def render(self) -> None:
        self._print_stats()
        print("=" * 60)
        print("  检测结果")
        print("=" * 60)
        print()
        self._print_diff()
        self._print_issues()

    def _print_stats(self) -> None:
        print("=" * 60)
        print("  知识库概览")
        print("=" * 60)
        print(f"\n  数据目录: {self.stats.data_dir}")
        print(f"  领域数量: {self.stats.domain_count}")
        print(f"  本体数量: {self.stats.ontology_count}")
        print(f"  实例数量: {self.stats.instance_count}")
        print()
        if self.stats.has_domains:
            print("  领域清单:")
            for domain in self.stats.domains:
                print(f"    {str(domain.id):<20} {domain.name:<12}")
            print()

    def _print_diff(self) -> None:
        if not self.diff:
            return
        prev_time = (self.previous_timestamp or "未知")[:10]
        if self.diff.has_changes:
            parts = []
            if self.diff.fixed:
                parts.append(f"✅ 已修复 {len(self.diff.fixed)} 项")
            if self.diff.new:
                parts.append(f"🆕 新增 {len(self.diff.new)} 项")
            if self.diff.pending:
                parts.append(f"⏳ 待处理 {len(self.diff.pending)} 项")
            print(f"相比上次审计（{prev_time}）：{' / '.join(parts)}")
        else:
            print(f"✓ 与上次审计一致，无新增问题（{prev_time}）")
        print()

    def _print_issues(self) -> None:
        _print_report_to_stdout(self.issues)


# ── repository ────────────────────────────────────────────────────────────

JSON_FILE = "audit.json"


class ReportRepository:
    def __init__(self, state_home: Path):
        self._path = state_home / JSON_FILE

    def load_previous_state(self, mode: Optional[AuditMode] = None) -> Optional:
        """Load the previous audit's issue list for diff computation."""
        if not self._path.exists():
            return None
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
            if mode and data.get("mode") != mode.value:
                return None
            issues = [
                AuditIssue(category=i["category"], group=i["group"], label=i["label"], action=i.get("action", ""))
                for i in data.get("issues", [])
            ]
            return _PreviousAudit(
                issues=issues,
                timestamp=data.get("timestamp", ""),
                mode=AuditMode(data["mode"]),
            )
        except Exception:
            return None

    def save_report(self, report: Report) -> None:
        data = {
            "timestamp": report.timestamp,
            "mode": report.mode.value,
            "issues": [
                {"category": i.category, "group": i.group, "label": i.label, "action": i.action}
                for i in (report.issues.need_confirm + report.issues.auto_fixable + report.issues.suggestions)
            ],
        }
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


@dataclass
class _PreviousAudit:
    issues: list
    timestamp: str
    mode: AuditMode


# ── rendering helpers (kept separate for testability) ─────────────────────
# These are extracted from the old print_report; they operate on AuditIssues.

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


def _print_group(title: str, issues: list) -> None:
    print(f"  {title}")
    for issue in issues:
        print(f"    {issue.label}")
        if issue.action:
            print(f"    → {issue.action}")
    print()


def _print_section(header: str, desc: str, groups: list[IssueGroup]) -> None:
    if not groups:
        return
    print(f"━━━ {header} ━━━")
    print(f"{desc}\n")
    for group in groups:
        _print_group(group.group_name, group.issues)


def _print_report_to_stdout(report: AuditIssues, template=None) -> None:
    template = template or DEFAULT_REPORT_TEMPLATE
    has_problems = bool(report.need_confirm or report.auto_fixable)
    sections = template.sections_for(report.mode)

    if has_problems:
        for section in sections:
            groups = report.section_groups(section.key)
            if groups:
                _print_section(section.header, section.description, groups)

        print("=" * 60)
        print(template.summary_header)
        print("=" * 60)
        print(f"  · 需要你确认: {len(report.need_confirm)} 项")
        print(f"  · 平台可修复: {len(report.auto_fixable)} 项")
        print(f"  · 建议关注:   {len(report.suggestions)} 项")
        print()
        tail = template.tail_for(report.mode, bool(report.need_confirm), bool(report.auto_fixable))
        if tail:
            print(tail)

    if report.suggestions:
        _print_section(
            "建议关注",
            "以下优化建议在全面审计模式下提供。" if report.mode.value == "full"
            else "以下问题在快速模式下仅供参考，切换到 --mode full 进行全面审计。",
            report.section_groups("suggestions"),
        )

    if not has_problems and not report.suggestions:
        print(template.clean_message)
