"""知识工程 ReAct 智能体 — 绑定 knowl 项目工具。"""

from quanttide_agent import ActionParser, LLM, ReActAgent

from app.agents.tools import STRUCTURAL_TOOLS, QUALITY_TOOLS
from app.config import settings


_DEFAULT_TOOLS = [t for t in STRUCTURAL_TOOLS + QUALITY_TOOLS
                  if t.name in ("validate", "fusion-check", "check-abstraction", "cross-domain-report")]


def default_agent(llm: LLM | None = None) -> ReActAgent:
    llm = llm or LLM(api_key=settings.llm_api_key)
    return ReActAgent(llm, list(_DEFAULT_TOOLS), parser=ActionParser())
