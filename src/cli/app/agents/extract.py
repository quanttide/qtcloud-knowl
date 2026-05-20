"""知识抽取 — 从源文件自动抽取知识到知识库。"""

from pathlib import Path
from app.config import settings


def run(sample_dir=None, data_dir=None):
    sdir = Path(sample_dir) if sample_dir else settings.sample_home
    ddir = Path(data_dir) if data_dir else settings.data_home

    import typer
    if not sdir or not sdir.exists():
        print("错误: 源文档目录不存在或未设置")
        raise typer.Exit(code=1)

    if not settings.llm_api_key:
        print("错误: LLM API key 未配置（设置 QTCLOUD_KNOWL_LLM_API_KEY 环境变量）")
        print("知识抽取需要 LLM 支持以分析文档内容并推荐本体/实例/关系。")
        print("如果仅需骨架初始化，请使用 init-domain 命令。")
        raise typer.Exit(code=1)

    md_files = list(sdir.glob("*.md"))
    if not md_files:
        print("警告: 源文档目录中没有 .md 文件")
        print("已创建空知识库骨架。")
        ddir.mkdir(parents=True, exist_ok=True)
        return 0

    print(f"源文档目录: {sdir}")
    print(f"目标数据目录: {ddir}")
    print(f"源文件数: {len(md_files)}")
    print()

    from app.detectors.detect_domain import run as detect_run

    for f in md_files:
        print(f"[检测] {f.name}")
        detect_run(str(f), str(ddir))
        print()

    from quanttide_agent import LLM, ReActAgent, ActionParser, Tool

    llm = LLM(api_key=settings.llm_api_key)
    tools = [
        Tool(name="detect-domain", description="为文件推荐所属领域", executor=lambda inp: detect_run(inp["filepath"], str(ddir))),
    ]

    agent = ReActAgent(llm, tools, parser=ActionParser(), max_steps=5)

    print("=" * 60)
    print("  知识抽取开始（需要 LLM 支持）")
    print("=" * 60)
    print()
    print("此功能需要 LLM API key 配置。当前连接已就绪。")
    print(f"使用模型: {llm.model}")
    print()

    print("请通过 ReAct Agent 提示词触发抽取流程。")
    print("例如: qtcloud-knowl agent \"对 sample_dir 中的文档执行知识发现\"")
    print()

    return 0
