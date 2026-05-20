"""全量质量审计 — 串行执行全部检测，生成业务语言报告。"""

import io
import sys
import re
from pathlib import Path
from app.config import settings
from app.agents.tools import all_detection_tools
from app.loader import load_all_domains


def capture_run(fn, *args, **kwargs):
    buf = io.StringIO()
    old = sys.stdout
    sys.stdout = buf
    try:
        ret = fn(*args, **kwargs)
    except Exception as e:
        ret = f"执行错误: {e}"
    finally:
        sys.stdout = old
    return buf.getvalue(), ret


def _has_issue(output):
    return "[MISS]" in output or "[FAIL]" in output or "[检测到]" in output or "未定义" in output or "需人确认" in output


def _has_undefined_terms(output):
    return "使用了术语" in output


def _has_broken_refs(output):
    return "需人确认" in output


def _count(output, marker):
    return len(re.findall(marker, output))


def _format_issues(output, indent="    "):
    issues = []
    for line in output.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        if "[MISS] " in stripped:
            label = stripped.split("[MISS] ", 1)[-1].strip()
        elif "[FAIL] " in stripped:
            label = stripped.split("[FAIL] ", 1)[-1].strip()
        elif "使用了术语" in stripped:
            label = stripped
        elif "需人确认" in stripped:
            label = stripped.replace("【需人确认】", "").strip()
        elif "[检测到] " in stripped:
            label = stripped.split("[检测到] ", 1)[-1].strip()
        else:
            continue
        issues.append(f"{indent}• {label}")
    return issues


def run(data_dir=None, sample_dir=None):
    ddir = Path(data_dir) if data_dir else settings.data_home
    sdir = Path(sample_dir) if sample_dir else settings.sample_home

    import typer
    if not ddir.exists():
        print("审计中止：数据目录不存在")
        print(f"  路径: {ddir}")
        print("请确认 QTCLOUD_KNOWL_DATA_HOME 已正确设置。")
        raise typer.Exit(code=1)

    domain_count = 0
    try:
        domains = load_all_domains(ddir)
        domain_count = len(domains)
    except Exception:
        pass

    need_confirm = []
    auto_fixable = []
    suggestions = []

    for name, desc, fn in all_detection_tools():
        kwargs = {}
        if name in ("find-undefined-terms",):
            if sdir:
                kwargs["sample_dir"] = str(sdir)
            kwargs["data_dir"] = str(ddir)
        elif name in ("fusion-check",):
            kwargs["data_dir"] = str(ddir)
            if sdir:
                kwargs["sample_dir"] = str(sdir)
        else:
            kwargs["data_dir"] = str(ddir)

        output, ret = capture_run(fn, **kwargs)

        issues = _format_issues(output)

        if name == "validate" and issues:
            auto_fixable.append(("文件结构问题", issues, "运行 qtcloud-knowl auto-fix 可自动补全缺失的骨架文件"))
        elif name == "find-undefined-terms" and issues:
            need_confirm.append(("未定义术语", issues, "这些术语在源文档中使用了，但没有在任何领域中被定义"))
        elif name == "fusion-check" and issues:
            need_confirm.append(("名称冲突或引用断裂", issues, "请确认这些引用是否正确，或是否需要统一术语"))
        elif name == "check-abstraction" and issues:
            suggestions.append(("本体抽象度不足", issues, "建议按 docs/criteria.md 中的方法重新抽象"))
        elif name == "cross-domain-report" and issues:
            suggestions.append(("跨领域关系覆盖率", issues, "每个领域至少应有 2 条跨领域关系"))

    print("=" * 60)
    print("  知识库质量审计报告")
    print("=" * 60)

    print(f"\n审计目标: {ddir}")
    print(f"领域数量: {domain_count}")
    if sdir:
        print(f"源文件目录: {sdir}")
    print()

    if not need_confirm and not auto_fixable and not suggestions:
        print("✓ 未发现问题，知识库结构良好。")
        return 0

    if need_confirm:
        print("━━━ 需要你确认的问题 ━━━")
        print("以下问题平台无法自动判断，需要你决定如何处理。\n")
        for title, issues, hint in need_confirm:
            print(f"  {title}")
            for i in issues:
                print(i)
            print(f"  建议：{hint}")
            print()

    if auto_fixable:
        print("━━━ 平台发现的问题 ━━━")
        print("以下问题平台已识别，可通过自动修复处理。\n")
        for title, issues, hint in auto_fixable:
            print(f"  {title}")
            for i in issues:
                print(i)
            print(f"  建议：{hint}")
            print()

    if suggestions:
        print("━━━ 建议关注 ━━━")
        print("以下不是错误，但优化后可以提升知识库质量。\n")
        for title, issues, hint in suggestions:
            print(f"  {title}")
            for i in issues:
                print(i)
            print(f"  建议：{hint}")
            print()

    print("=" * 60)
    print("  汇总")
    print("=" * 60)
    total = len(need_confirm) + len(auto_fixable) + len(suggestions)
    print(f"  · 需要你确认: {len(need_confirm)} 项")
    print(f"  · 平台可修复: {len(auto_fixable)} 项")
    print(f"  · 建议关注:   {len(suggestions)} 项")
    print()
    if need_confirm:
        print("请先处理「需要你确认的问题」，其他问题可并行处理。")
    elif auto_fixable:
        print("运行 qtcloud-knowl audit --auto-fix 自动修复平台发现的问题。")

    return 0 if not need_confirm and not auto_fixable else 1
