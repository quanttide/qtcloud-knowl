"""
ReAct 智能体实验 — 基于 quanttide-agent 的工具调用循环。

用法:
    from app.agent import Agent, Tool
    from quanttide_agent import LLM

    llm = LLM(model="deepseek-v4-flash")
    agent = Agent(llm, [
        Tool(name="validate", description="检查目录结构", executor=validate_fn),
    ])
    result = agent.run("检查 org-gov 领域有没有问题")
"""

from __future__ import annotations

import json
import re
from collections.abc import Callable
from typing import Any, ClassVar, Literal

from pydantic import BaseModel
from quanttide_agent import LLM, ToolDef


class Message(BaseModel):
    """消息"""

    role: Literal["system", "user", "assistant", "tool"]
    content: str
    tool_call_id: str | None = None

    def to_dict(self) -> dict:
        d: dict[str, Any] = {"role": self.role, "content": self.content}
        if self.tool_call_id:
            d["tool_call_id"] = self.tool_call_id
        return d


class Action(BaseModel):
    """LLM 输出的动作指令"""

    name: str
    args: dict = {}
    pattern: ClassVar[str] = r"Action name:\s*(.+)\nAction args:\s*(.+)"

    @classmethod
    def from_text(cls, text: str) -> Action | None:
        m = re.search(cls.pattern, text)
        if not m:
            return None
        name = m.group(1).strip()
        raw = m.group(2).strip()
        try:
            inp = json.loads(raw)
        except json.JSONDecodeError:
            inp = raw
        return cls(name=name, args=inp)


class Tool(BaseModel):
    """工具定义（schema + execute）"""

    name: str
    description: str = ""
    parameters: dict | None = None
    executor: Callable | None = None

    def execute(self, inp: dict) -> str:
        if not self.executor:
            return f"未知工具: {self.name}"
        try:
            return str(self.executor(inp))
        except Exception as e:
            return f"执行错误: {e}"


REACT_PROMPT = """你是一个知识工程助手。你有以下工具可用：

{tool_descriptions}

每次回复按以下格式（不要输出其他内容）：

Thought: 你当前的思考
Action name: 工具名称
Action args: 给工具的参数（JSON 格式）

当得到最终答案时：

Thought: 我得到答案了
Final Answer: 你的最终回复
"""


class Agent:
    def __init__(self, llm: LLM, tools: list[Tool], max_steps: int = 10):
        self.llm = llm
        self._tools = {t.name: t for t in tools}
        self.max_steps = max_steps

    def run(self, task: str) -> str:
        tool_desc = "\n".join(f"- {t.name}: {t.description}" for t in self._tools.values())
        system = REACT_PROMPT.format(tool_descriptions=tool_desc)
        messages: list[Message] = [
            Message(role="system", content=system),
            Message(role="user", content=task),
        ]

        for _ in range(self.max_steps):
            resp = self.llm.chat([m.to_dict() for m in messages])
            output = resp.content.strip()

            if "Final Answer:" in output:
                return output.split("Final Answer:", 1)[1].strip()

            action = Action.from_text(output)
            messages.append(Message(role="assistant", content=output))
            if not action:
                messages.append(Message(role="user", content="无法解析指令，请使用正确的 ReAct 格式。"))
                continue

            tool = self._tools.get(action.name)
            result = tool.execute(action.args) if tool else f"未知工具: {action.name}"
            messages.append(Message(role="tool", tool_call_id=action.name, content=result))

        return "达到最大步数，未得到最终答案。"
def default_agent(llm: LLM | None = None) -> Agent:
    from app.validators.validate import run as validate_run
    from app.validators.fusion_check import run as fusion_run
    from app.reporters.abstraction import run as abstraction_run
    from app.reporters.cross_domain import run as cross_domain_run
    from quanttide_agent import LLM as _LLM

    llm = llm or _LLM(model="deepseek-v4-flash")
    return Agent(llm, [
        Tool(name="validate", description="检查领域目录结构完整性", executor=validate_run),
        Tool(name="fusion-check", description="跨领域融合检测（名称冲突、引用断裂）", executor=fusion_run),
        Tool(name="check-abstraction", description="本体抽象度检测", executor=abstraction_run),
        Tool(name="cross-domain-report", description="跨领域关系覆盖率报告", executor=cross_domain_run),
    ])
