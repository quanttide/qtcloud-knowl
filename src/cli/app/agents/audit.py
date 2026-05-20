"""全量质量审计 — 串行执行全部检测，聚合结果。"""

import io
import sys
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


def run(data_dir=None, sample_dir=None):
    ddir = Path(data_dir) if data_dir else settings.data_home
    sdir = Path(sample_dir) if sample_dir else settings.sample_home

    import typer
    if not ddir.exists():
        print(f"错误: data_home 目录不存在: {ddir}")
        raise typer.Exit(code=1)

    print("=" * 60)
    print("  知识库质量审计报告")
    print("=" * 60)

    domain_count = 0
    try:
        domains = load_all_domains(ddir)
        domain_count = len(domains)
    except Exception as e:
        print(f"\n! 加载领域数据失败: {e}")

    print(f"\n审计目标: {ddir}")
    print(f"领域数量: {domain_count}")
    if sdir:
        print(f"源文件目录: {sdir}")
    print()

    results = []
    all_pass = True

    for name, desc, fn in all_detection_tools():
        print(f"[运行] {name} — {desc}")
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
        is_pass = (ret == 0 or (isinstance(ret, str) and "通过" in ret))
        status = "通过" if is_pass else "警告"
        if not is_pass:
            all_pass = False
        results.append((name, status, output))
        print(f"  状态: {status}")
        print()

    print("=" * 60)
    print("  汇总")
    print("=" * 60)
    for name, status, output in results:
        icon = "✓" if status == "通过" else "⚠"
        print(f"  {icon} {name}: {status}")

    print()
    if all_pass:
        print("结果: 全部检测通过")
    else:
        print("结果: 存在需要关注的问题，详见上方各检测输出")

    print("\n--- 检测详情 ---")
    for name, status, output in results:
        print(f"\n>>> {name} ({status})")
        for line in output.strip().split("\n"):
            print(f"  {line}")

    return 0 if all_pass else 1
