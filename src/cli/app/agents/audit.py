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
    return "[MISS]" in output or "[FAIL]" in output or "[检测到]" in output or "使用了术语" in output or "需人确认" in output


def _parse_issues(output, data_dir=None):
    issues = []
    current_domain = None
    for line in output.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        m = re.match(r"^=== (.+) ===", stripped)
        if m:
            current_domain = m.group(1)
            continue
        if "[MISS] " in stripped:
            fname = stripped.split("[MISS] ", 1)[-1].strip()
            label = f"• 缺少文件 {fname}"
            if current_domain:
                action = f"运行 qtcloud-knowl auto-fix 自动补全，或创建文件 {data_dir}/{current_domain}/{fname}"
            else:
                action = "运行 qtcloud-knowl auto-fix 自动补全缺失文件"
            issues.append((label, action))
        elif "[FAIL] " in stripped:
            detail = stripped.split("[FAIL] ", 1)[-1].strip()
            label = f"• JSON 格式错误: {detail}"
            action = f"修复 {data_dir}/{current_domain}/ 下对应的 JSON 文件" if current_domain else "修复对应 JSON 文件格式"
            issues.append((label, action))
        elif "使用了术语" in stripped:
            issues.append((f"• {stripped}", "在对应领域 domain.json 的 vocabulary 字段中补充该术语"))
        elif "需人确认" in stripped:
            label = stripped.replace("【需人确认】", "").strip()
            issues.append((f"• {label}", "确认该引用是否必要，如必要则补充源文件或删除引用"))
        elif "[检测到] " in stripped:
            label = stripped.split("[检测到] ", 1)[-1].strip()
            dest = f"{data_dir}/{current_domain}/ontologies.json" if current_domain else "对应 ontologies.json"
            issues.append((f"• {label}", f"重构 {dest} 中的 pattern，将具体值改为变量"))
    return issues


def run(data_dir=None, sample_dir=None, mode="full"):
    ddir = Path(data_dir) if data_dir else settings.data_home
    sdir = Path(sample_dir) if sample_dir else settings.sample_home

    import typer
    if not ddir.exists():
        print("审计中止：数据目录不存在")
        print(f"  当前路径: {ddir}")
        print("请确认 QTCLOUD_KNOWL_DATA_HOME 环境变量已正确设置，或传入 data_dir 参数。")
        raise typer.Exit(code=1)

    if mode not in ("simple", "full"):
        print(f"错误: 不支持的审计模式 '{mode}'，仅支持 simple（快速）/ full（全面）")
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

    tools = all_detection_tools(mode)
    for name, desc, fn in tools:
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

        issues = _parse_issues(output, str(ddir))
        if not issues and _has_issue(output):
            issues.append(("• 检测到异常但无法解析具体位置", "请查看上方原始日志确认问题"))

        if name == "validate" and issues:
            auto_fixable.append(("文件结构问题", issues))
        elif name == "find-undefined-terms" and issues:
            need_confirm.append(("未定义术语", issues))
        elif name == "fusion-check" and issues:
            need_confirm.append(("名称冲突或引用断裂", issues))
        elif name == "check-abstraction" and issues:
            suggestions.append(("本体抽象度不足", issues))
        elif name == "cross-domain-report" and issues:
            suggestions.append(("跨领域关系覆盖率", issues))

    if mode == "simple":
        suggestions = need_confirm + suggestions
        need_confirm = auto_fixable
        auto_fixable = []

    mode_label = "快速检查模式" if mode == "simple" else "全面审计模式"
    print("=" * 60)
    print(f"  知识库质量审计报告（{mode_label}）")
    print("=" * 60)

    print(f"\n审计目标: {ddir}")
    print(f"领域数量: {domain_count}")
    if sdir:
        print(f"源文件目录: {sdir}")
    print()

    if not need_confirm and not auto_fixable and not suggestions:
        print("✓ 未发现问题，知识库结构良好。")
        return 0

    def _print_group(title, issues):
        print(f"  {title}")
        for label, action in issues:
            print(f"    {label}")
            if action:
                print(f"    → {action}")
        print()

    if need_confirm:
        title_label = "建议关注" if mode == "simple" else "需要你确认的问题"
        desc = "以下问题可通过 auto-fix 自动修复，无需手动处理。" if mode == "simple" else "以下问题平台无法自动判断，需要你决定如何处理。"
        print(f"━━━ {title_label} ━━━")
        print(f"{desc}\n")
        for title, issues in need_confirm:
            _print_group(title, issues)

    if auto_fixable:
        title_label = "平台发现的问题"
        desc = "以下问题平台已识别，可通过自动修复处理。"
        print(f"━━━ {title_label} ━━━")
        print(f"{desc}\n")
        for title, issues in auto_fixable:
            _print_group(title, issues)

    if suggestions:
        title_label = "建议关注"
        desc = "以下优化建议在全面审计模式下提供。" if mode == "full" else "以下问题在快速模式下仅供参考，切换到 --mode full 进行全面审计。"
        print(f"━━━ {title_label} ━━━")
        print(f"{desc}\n")
        for title, issues in suggestions:
            _print_group(title, issues)

    print("=" * 60)
    print("  汇总")
    print("=" * 60)
    total = len(need_confirm) + len(auto_fixable) + len(suggestions)
    print(f"  · 需要你确认: {len(need_confirm)} 项")
    print(f"  · 平台可修复: {len(auto_fixable)} 项")
    print(f"  · 建议关注:   {len(suggestions)} 项")
    print()
    if mode == "simple":
        print("当前为快速检查模式，运行 qtcloud-knowl audit --mode full 进行全面审计。")
    elif need_confirm:
        print("请先处理「需要你确认的问题」，其他问题可并行处理。")
    elif auto_fixable:
        print("运行 qtcloud-knowl audit --auto-fix 自动修复平台发现的问题。")

    return 0 if not need_confirm and not auto_fixable else 1
