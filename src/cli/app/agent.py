"""知识工程 ReAct 智能体 — 绑定 knowl 项目工具。"""

from quanttide_agent import ActionParser, LLM, ReActAgent, Tool


def default_agent(llm: LLM | None = None) -> ReActAgent:
    from app.validators.validate import run as validate_run
    from app.validators.fusion_check import run as fusion_run
    from app.reporters.abstraction import run as abstraction_run
    from app.reporters.cross_domain import run as cross_domain_run

    llm = llm or LLM()
    tools = [
        Tool(name="validate", description="检查领域目录结构完整性", executor=validate_run),
        Tool(name="fusion-check", description="跨领域融合检测（名称冲突、引用断裂）", executor=fusion_run),
        Tool(name="check-abstraction", description="本体抽象度检测", executor=abstraction_run),
        Tool(name="cross-domain-report", description="跨领域关系覆盖率报告", executor=cross_domain_run),
    ]
    return ReActAgent(llm, tools, parser=ActionParser())
