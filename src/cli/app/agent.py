"""
ReAct 智能体实验 — 基于 quanttide-agent 的工具调用循环。

用法:
    from app.agent import Agent, Tool
    from quanttide_agent import LLM

    llm = LLM(model="deepseek-v4-flash")
    agent = Agent(llm, [
        Tool(name="validate", description="检查目录结构", execute=validate_fn),
    ])
    result = agent.run("检查 org-gov 领域有没有问题")
"""

from __future__ import annotations

import json
import re
from collections.abc import Callable
from pathlib import Path
from typing import Any

from pydantic import BaseModel
from quanttide_agent import LLM, ToolDef


class Tool(BaseModel):
    """工具定义（schema + execute）"""

    name: str
    description: str = ""
    parameters: dict | None = None
    execute: Callable | None = None

REACT_PROMPT = """你是一个知识工程助手。你有以下工具可用：

{tool_descriptions}

每次回复按以下格式（不要输出其他内容）：

Thought: 你当前的思考
Action: 工具名称
Action Input: 给工具的参数（JSON 格式）

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
        messages = [{"role": "system", "content": system}, {"role": "user", "content": task}]

        for _ in range(self.max_steps):
            resp = self.llm.chat(messages)
            output = resp.content.strip()

            if "Final Answer:" in output:
                return output.split("Final Answer:", 1)[1].strip()

            action = self._parse_action(output)
            if not action:
                messages.append({"role": "assistant", "content": output})
                messages.append({"role": "user", "content": "无法解析指令，请使用正确的 ReAct 格式。"})
                continue

            messages.append({"role": "assistant", "content": output})
            result = self._execute(action["name"], action["input"])
            messages.append({"role": "tool", "tool_call_id": action["name"], "content": str(result)})

        return "达到最大步数，未得到最终答案。"

    def _parse_action(self, text: str) -> dict | None:
        m = re.search(r"Action:\s*(.+)\nAction Input:\s*(.+)", text)
        if not m:
            return None
        name = m.group(1).strip()
        raw = m.group(2).strip()
        try:
            inp = json.loads(raw)
        except json.JSONDecodeError:
            inp = raw
        return {"name": name, "input": inp}

    def _execute(self, name: str, inp: dict) -> str:
        tool = self._tools.get(name)
        if not tool or not tool.execute:
            return f"未知工具: {name}"
        try:
            return str(tool.execute(inp))
        except Exception as e:
            return f"执行错误: {e}"


def _import_run(module_path: str) -> Callable:
    def fn(_args: dict | None = None) -> str:
        import importlib

        mod = importlib.import_module(module_path)
        result = mod.run()
        if result is None or result == 0:
            return "成功"
        return f"退出码 {result}"

    return fn


def default_agent(llm: LLM | None = None) -> Agent:
    from quanttide_agent import LLM as _LLM

    llm = llm or _LLM(model="deepseek-v4-flash")
    return Agent(llm, [
        Tool(name="validate", description="检查领域目录结构完整性", execute=_import_run("app.validators.validate")),
        Tool(name="fusion-check", description="跨领域融合检测（名称冲突、引用断裂）", execute=_import_run("app.validators.fusion_check")),
        Tool(name="check-abstraction", description="本体抽象度检测", execute=_import_run("app.reporters.abstraction")),
        Tool(name="cross-domain-report", description="跨领域关系覆盖率报告", execute=_import_run("app.reporters.cross_domain")),
    ])
