"""全量质量审计 — 串行执行全部检测，生成业务语言报告。"""

import json
import re
from datetime import datetime
from pathlib import Path

from app.agents.tools import all_detection_tools
from app.config import settings
from app.knowl_loader import load_all_domains

AUDIT_STATE_FILE = "audit.json"

MISS_TAG = "[MISS] "
FAIL_TAG = "[FAIL] "
DETECTED_TAG = "[检测到] "
NEED_CONFIRM_TAG = "需人确认"
TERM_USED_PATTERN = "使用了术语"
SECTION_HEADER = re.compile(r"^=== (.+) ===")


def _collect_issues(need_confirm, auto_fixable, suggestions):
    flat = []
    for category, items in [
        ("need_confirm", need_confirm),
        ("auto_fixable", auto_fixable),
        ("suggestions", suggestions),
    ]:
        for group_title, issue_list in items:
            for label, action in issue_list:
                flat.append(
                    {"category": category, "group": group_title, "label": label}
                )
    return flat


def _issue_key(item):
    return f"{item['category']}|{item['group']}|{item['label']}"


def _load_audit_state(mode=None):
    fpath = settings.state_home / AUDIT_STATE_FILE
    if not fpath.exists():
        return None
    try:
        state = json.loads(fpath.read_text(encoding="utf-8"))
        if mode and state.get("mode") != mode:
            return None
        return state
    except Exception:
        return None


def _save_audit_state(issues, mode):
    fpath = settings.state_home / AUDIT_STATE_FILE
    state = {
        "timestamp": datetime.now().isoformat(),
        "mode": mode,
        "issues": issues,
    }
    fpath.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def _compute_diff(previous_issues, current_issues):
    prev_set = {_issue_key(i) for i in previous_issues}
    curr_set = {_issue_key(i) for i in current_issues}
    fixed = prev_set - curr_set
    new = curr_set - prev_set
    pending = prev_set & curr_set
    return fixed, new, pending, prev_set, curr_set


def _has_issue(output):
    return (
        MISS_TAG in output
        or FAIL_TAG in output
        or DETECTED_TAG in output
        or TERM_USED_PATTERN in output
        or NEED_CONFIRM_TAG in output
    )


def _parse_miss(line, current_domain, data_dir):
    if MISS_TAG not in line:
        return None
    fname = line.split(MISS_TAG, 1)[-1].strip()
    label = f"• 缺少文件 {fname}"
    if current_domain:
        action = f"运行 qtcloud-knowl auto-fix 自动补全，或创建文件 {data_dir}/{current_domain}/{fname}"
    else:
        action = "运行 qtcloud-knowl auto-fix 自动补全缺失文件"
    return label, action


def _parse_fail(line, current_domain, data_dir):
    if FAIL_TAG not in line:
        return None
    detail = line.split(FAIL_TAG, 1)[-1].strip()
    label = f"• JSON 格式错误: {detail}"
    action = (
        f"修复 {data_dir}/{current_domain}/ 下对应的 JSON 文件"
        if current_domain
        else "修复对应 JSON 文件格式"
    )
    return label, action


def _parse_term(line, _current_domain=None, _data_dir=None):
    if TERM_USED_PATTERN not in line:
        return None
    return f"• {line}", "在对应领域 domain.json 的 vocabulary 字段中补充该术语"


def _parse_confirm(line, _current_domain=None, _data_dir=None):
    if NEED_CONFIRM_TAG not in line:
        return None
    label = line.replace(f"【{NEED_CONFIRM_TAG}】", "").strip()
    return f"• {label}", "确认该引用是否必要，如必要则补充源文件或删除引用"


def _parse_abstraction(line, current_domain, data_dir):
    if DETECTED_TAG not in line:
        return None
    label = line.split(DETECTED_TAG, 1)[-1].strip()
    dest = (
        f"{data_dir}/{current_domain}/ontologies.json"
        if current_domain
        else "对应 ontologies.json"
    )
    return f"• {label}", f"重构 {dest} 中的 pattern，将具体值改为变量"


_PARSERS = [
    ("miss", _parse_miss),
    ("fail", _parse_fail),
    ("term", _parse_term),
    ("confirm", _parse_confirm),
    ("abstraction", _parse_abstraction),
]


def _parse_issues(output, data_dir=None):
    issues = []
    current_domain = None
    for line in output.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        m = SECTION_HEADER.match(stripped)
        if m:
            current_domain = m.group(1)
            continue
        for _, parser in _PARSERS:
            result = parser(stripped, current_domain, data_dir)
            if result:
                issues.append(result)
                break
    return issues


def _validate_args(ddir, mode):
    if not ddir.exists():
        print("审计中止：数据目录不存在")
        print(f"  当前路径: {ddir}")
        print(
            "请确认 QTCLOUD_KNOWL_DATA_HOME 环境变量已正确设置，或传入 data_dir 参数。"
        )
        return False
    if mode not in ("simple", "full"):
        print(f"错误: 不支持的审计模式 '{mode}'，仅支持 simple / full")
        return False
    return True


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


def _print_stats(ddir, domains, ontology_count, instance_count):
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


def _run_tools(ddir, mode):
    need_confirm = []
    auto_fixable = []
    suggestions = []
    tools = all_detection_tools(mode)
    for tool in tools:
        inp = {"data_dir": str(ddir)}
        output = tool.execute(inp)
        issues = _parse_issues(output, str(ddir))
        if not issues and _has_issue(output):
            issues.append(
                ("• 检测到异常但无法解析具体位置", "请查看上方原始日志确认问题")
            )
        _categorize_issues(tool.name, issues, need_confirm, auto_fixable, suggestions)
    if mode == "simple":
        suggestions = need_confirm + suggestions
        need_confirm = auto_fixable
        auto_fixable = []
    return need_confirm, auto_fixable, suggestions


def _categorize_issues(tool_name, issues, need_confirm, auto_fixable, suggestions):
    if not issues:
        return
    mapping = {
        "validate": ("文件结构问题", auto_fixable),
        "find-undefined-terms": ("未定义术语", need_confirm),
        "fusion-check": ("名称冲突或引用断裂", need_confirm),
        "check-abstraction": ("本体抽象度不足", suggestions),
        "cross-domain-report": ("跨领域关系覆盖率", suggestions),
    }
    entry = mapping.get(tool_name)
    if entry:
        entry[1].append((entry[0], issues))


def _print_diff(previous, current_issues):
    fixed, new, pending, _, _ = _compute_diff(
        previous.get("issues", []), current_issues
    )
    prev_time = previous.get("timestamp", "未知")[:10]
    if fixed or new or pending:
        parts = []
        if fixed:
            parts.append(f"✅ 已修复 {len(fixed)} 项")
        if new:
            parts.append(f"🆕 新增 {len(new)} 项")
        if pending:
            parts.append(f"⏳ 待处理 {len(pending)} 项")
        print(f"相比上次审计（{prev_time}）：{' / '.join(parts)}")
    else:
        print(f"✓ 与上次审计一致，无新增问题（{prev_time}）")


def _print_group(title, issues):
    print(f"  {title}")
    for label, action in issues:
        print(f"    {label}")
        if action:
            print(f"    → {action}")
    print()


def _print_section(header, desc, groups):
    if not groups:
        return
    print(f"━━━ {header} ━━━")
    print(f"{desc}\n")
    for title, issues in groups:
        _print_group(title, issues)


def _print_report(need_confirm, auto_fixable, suggestions, mode):
    if not need_confirm and not auto_fixable and not suggestions:
        print("✓ 未发现问题，知识库结构良好。")
        return

    if need_confirm:
        header = "建议关注" if mode == "simple" else "需要你确认的问题"
        desc = (
            "以下问题可由平台自动修复，无需手动处理。"
            if mode == "simple"
            else "以下问题平台无法自动判断，需要你决定如何处理。"
        )
        _print_section(header, desc, need_confirm)

    if auto_fixable:
        _print_section(
            "平台发现的问题",
            "以下问题平台已识别，可通过自动修复处理。",
            auto_fixable,
        )

    if suggestions:
        header = "建议关注"
        desc = (
            "以下优化建议在全面审计模式下提供。"
            if mode == "full"
            else "以下问题在快速模式下仅供参考，切换到 --mode full 进行全面审计。"
        )
        _print_section(header, desc, suggestions)

    print("=" * 60)
    print("  汇总")
    print("=" * 60)
    print(f"  · 需要你确认: {len(need_confirm)} 项")
    print(f"  · 平台可修复: {len(auto_fixable)} 项")
    print(f"  · 建议关注:   {len(suggestions)} 项")
    print()
    if mode == "simple":
        print("当前为快速检查模式，运行 qtcloud-knowl audit --mode full 进行全面审计。")
    elif need_confirm:
        print("请先处理「需要你确认的问题」，其他问题可并行处理。")
    elif auto_fixable:
        print("运行 qtcloud-knowl auto-fix 自动修复平台发现的问题。")


def run(data_dir=None, mode="full"):
    ddir = Path(data_dir) if data_dir else settings.data_home
    if not _validate_args(ddir, mode):
        return 1

    domains, ontology_count, instance_count = _collect_stats(ddir)
    _print_stats(ddir, domains, ontology_count, instance_count)

    print("=" * 60)
    print("  检测结果")
    print("=" * 60)
    print()

    need_confirm, auto_fixable, suggestions = _run_tools(ddir, mode)
    current_issues = _collect_issues(need_confirm, auto_fixable, suggestions)
    previous = _load_audit_state(mode=mode)
    _save_audit_state(current_issues, mode)

    if previous:
        _print_diff(previous, current_issues)
    print()

    _print_report(need_confirm, auto_fixable, suggestions, mode)
    return 0 if not need_confirm and not auto_fixable else 1
