from app.audit.models import AuditDiff, AuditReport


def print_stats(ddir, domains, ontology_count, instance_count):
    print("=" * 60)
    print("  知识库概览")
    print("=" * 60)
    print(f"\n  数据目录: {ddir}")
    print(f"  领域数量: {len(domains)}")
    print(f"  本体数量: {ontology_count}")
    print(f"  实例数量: {instance_count}")
    print()
    if domains:
        print("  领域清单:")
        for domain in domains:
            print(f"    {str(domain.id):<20} {domain.name:<12}")
        print()


def _print_group(title, issues):
    print(f"  {title}")
    for issue in issues:
        print(f"    {issue.label}")
        if issue.action:
            print(f"    → {issue.action}")
    print()


def _print_section(header, desc, groups):
    if not groups:
        return
    print(f"━━━ {header} ━━━")
    print(f"{desc}\n")
    for issue in groups:
        _print_group(issue.group, [issue])


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


def print_report(report: AuditReport) -> None:
    if not report.need_confirm and not report.auto_fixable and not report.suggestions:
        print("✓ 未发现问题，知识库结构良好。")
        return

    if report.need_confirm:
        header = "建议关注" if report.mode.value == "simple" else "需要你确认的问题"
        desc = (
            "以下问题可由平台自动修复，无需手动处理。"
            if report.mode.value == "simple"
            else "以下问题平台无法自动判断，需要你决定如何处理。"
        )
        _print_section(header, desc, report.need_confirm)

    if report.auto_fixable:
        _print_section(
            "平台发现的问题",
            "以下问题平台已识别，可通过自动修复处理。",
            report.auto_fixable,
        )

    if report.suggestions:
        header = "建议关注"
        desc = (
            "以下优化建议在全面审计模式下提供。"
            if report.mode.value == "full"
            else "以下问题在快速模式下仅供参考，切换到 --mode full 进行全面审计。"
        )
        _print_section(header, desc, report.suggestions)

    print("=" * 60)
    print("  汇总")
    print("=" * 60)
    print(f"  · 需要你确认: {len(report.need_confirm)} 项")
    print(f"  · 平台可修复: {len(report.auto_fixable)} 项")
    print(f"  · 建议关注:   {len(report.suggestions)} 项")
    print()
    if report.mode.value == "simple":
        print("当前为快速检查模式，运行 qtcloud-knowl audit --mode full 进行全面审计。")
    elif report.need_confirm:
        print("请先处理「需要你确认的问题」，其他问题可并行处理。")
    elif report.auto_fixable:
        print("运行 qtcloud-knowl auto-fix 自动修复平台发现的问题。")
