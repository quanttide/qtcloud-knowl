from dataclasses import dataclass

from app.audit.models import AuditDiff, AuditReport, KnowledgeBaseStats, IssueGroup, AuditMode


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


def print_stats(stats: KnowledgeBaseStats) -> None:
    print("=" * 60)
    print("  知识库概览")
    print("=" * 60)
    print(f"\n  数据目录: {stats.data_dir}")
    print(f"  领域数量: {stats.domain_count}")
    print(f"  本体数量: {stats.ontology_count}")
    print(f"  实例数量: {stats.instance_count}")
    print()
    if stats.has_domains:
        print("  领域清单:")
        for domain in stats.domains:
            print(f"    {str(domain.id):<20} {domain.name:<12}")
        print()


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


def print_diff(diff: AuditDiff) -> None:
    prev_time = (diff.previous_timestamp or "未知")[:10]
    if diff.has_changes:
        parts = []
        if diff.fixed:
            parts.append(f"✅ 已修复 {len(diff.fixed)} 项")
        if diff.new:
            parts.append(f"🆕 新增 {len(diff.new)} 项")
        if diff.pending:
            parts.append(f"⏳ 待处理 {len(diff.pending)} 项")
        print(f"相比上次审计（{prev_time}）：{' / '.join(parts)}")
    else:
        print(f"✓ 与上次审计一致，无新增问题（{prev_time}）")


def print_report(report: AuditReport, template=None) -> None:
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
