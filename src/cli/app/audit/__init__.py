"""全量质量审计 — 串行执行全部检测，生成业务语言报告。"""
from datetime import datetime
from pathlib import Path
from typing import Optional

from app.agents.tools import all_detection_tools
from app.audit.models import AuditMode, AuditIssue, AuditDiff, AuditReport, AuditState
from app.audit.repository import AuditStateRepository
from app.audit.parser import ToolOutputParser
from app.audit.report import print_stats, print_report, print_diff
from app.config import settings
from app.knowl_loader import load_all_domains


def _collect_stats(ddir):
    domains = []
    ontology_count = 0
    instance_count = 0
    try:
        for d, domain, ontologies, instances in load_all_domains(ddir):
            domains.append(domain)
            ontology_count += len(ontologies)
            instance_count += len(instances)
    except Exception:
        pass
    return domains, ontology_count, instance_count


def _run_tools(ddir, mode):
    parser = ToolOutputParser()
    tools = all_detection_tools(mode.value)
    raw_issues = []
    for tool in tools:
        inp = {"data_dir": str(ddir)}
        output = tool.execute(inp)
        issues = parser.parse(output, str(ddir))
        if not issues and parser.has_issue(output):
            issues.append(
                AuditIssue(
                    category="need_confirm",
                    group=tool.name,
                    label="检测到异常但无法解析具体位置",
                    action="请查看上方原始日志确认问题",
                )
            )
        raw_issues.append((tool.name, issues))
    return _categorize_issues(raw_issues, mode)


def _categorize_issues(raw_issues, mode):
    need_confirm = []
    auto_fixable = []
    suggestions = []
    mapping = {
        "validate": ("文件结构问题", "auto_fixable"),
        "find-undefined-terms": ("未定义术语", "need_confirm"),
        "fusion-check": ("名称冲突或引用断裂", "need_confirm"),
        "check-abstraction": ("本体抽象度不足", "suggestions"),
        "cross-domain-report": ("跨领域关系覆盖率", "suggestions"),
    }
    for tool_name, issues in raw_issues:
        entry = mapping.get(tool_name)
        if not entry or not issues:
            continue
        group, category = entry
        target = {"need_confirm": need_confirm, "auto_fixable": auto_fixable, "suggestions": suggestions}
        for issue in issues:
            target[category].append(
                AuditIssue(category=category, group=group, label=issue.label, action=issue.action)
            )
    if mode == AuditMode.SIMPLE:
        suggestions = need_confirm + suggestions
        need_confirm = auto_fixable
        auto_fixable = []
    return need_confirm, auto_fixable, suggestions


def _validate_args(ddir, mode):
    if not ddir.exists():
        print("审计中止：数据目录不存在")
        print(f"  当前路径: {ddir}")
        print("请确认 QTCLOUD_KNOWL_DATA_HOME 环境变量已正确设置，或传入 data_dir 参数。")
        return False
    return True


def run(data_dir: Optional[str] = None, mode: str = "full") -> int:
    ddir = Path(data_dir) if data_dir else settings.data_home
    try:
        mode_vo = AuditMode(mode) if isinstance(mode, str) else mode
    except ValueError:
        print(f"错误: 不支持的审计模式 '{mode}'，仅支持 simple / full")
        return 1

    if not _validate_args(ddir, mode_vo):
        return 1

    domains, ontology_count, instance_count = _collect_stats(ddir)
    print_stats(ddir, domains, ontology_count, instance_count)

    print("=" * 60)
    print("  检测结果")
    print("=" * 60)
    print()

    need_confirm, auto_fixable, suggestions = _run_tools(ddir, mode_vo)
    current_issues = [i for lst in (need_confirm, auto_fixable, suggestions) for i in lst]

    repo = AuditStateRepository(settings.state_home)
    previous = repo.load(mode=mode_vo)
    repo.save(AuditState(mode=mode_vo, issues=current_issues))

    if previous:
        diff = AuditDiff.compute(previous.issues, current_issues, previous.timestamp)
        print_diff(diff)
    print()

    report = AuditReport(
        need_confirm=need_confirm,
        auto_fixable=auto_fixable,
        suggestions=suggestions,
        mode=mode_vo,
    )
    print_report(report)
    return 0 if not need_confirm and not auto_fixable else 1
