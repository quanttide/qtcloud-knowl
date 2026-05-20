"""测试 ReAct 智能体"""

from unittest.mock import MagicMock

import pytest
from quanttide_agent import ChatResponse, LLM, ToolDef

from app.agent import Agent


@pytest.fixture
def mock_llm() -> MagicMock:
    return MagicMock(spec=LLM)


def _tool(name: str, desc: str = "") -> ToolDef:
    return ToolDef(name=name, description=desc)


class TestParseAction:
    def test_parse_valid(self):
        agent = Agent.__new__(Agent)
        agent._tools = {}
        result = agent._parse_action("Thought: 需要检查\nAction: validate\nAction Input: {}")
        assert result == {"name": "validate", "input": {}}

    def test_parse_with_json_args(self):
        agent = Agent.__new__(Agent)
        agent._tools = {}
        result = agent._parse_action(
            'Thought: 检查特定领域\nAction: validate\nAction Input: {"domain": "org-gov"}'
        )
        assert result == {"name": "validate", "input": {"domain": "org-gov"}}

    def test_parse_no_action(self):
        agent = Agent.__new__(Agent)
        agent._tools = {}
        assert agent._parse_action("这是一段普通文本") is None

    def test_parse_missing_input(self):
        agent = Agent.__new__(Agent)
        agent._tools = {}
        result = agent._parse_action("Action: validate\nSomething else")
        assert result is None

    def test_parse_final_answer(self):
        agent = Agent.__new__(Agent)
        agent._tools = {}
        result = agent._parse_action("Thought: 完成\nFinal Answer: 结果")
        assert result is None


class TestExecute:
    def test_execute_known_tool(self):
        exec_records = []

        def tool_fn(args):
            exec_records.append(args)
            return "执行成功"

        agent = Agent.__new__(Agent)
        agent._tools = {"my-tool": (_tool("my-tool"), tool_fn)}
        result = agent._execute("my-tool", {"key": "val"})
        assert result == "执行成功"
        assert exec_records == [{"key": "val"}]

    def test_execute_unknown_tool(self):
        agent = Agent.__new__(Agent)
        agent._tools = {}
        result = agent._execute("unknown", {})
        assert "未知工具" in result

    def test_execute_tool_error(self):
        def failing_fn(args):
            raise ValueError("工具崩溃")

        agent = Agent.__new__(Agent)
        agent._tools = {"failing": (_tool("failing"), failing_fn)}
        result = agent._execute("failing", {})
        assert "执行错误" in result
        assert "工具崩溃" in result


class TestRun:
    def test_direct_final_answer(self, mock_llm):
        mock_llm.chat.return_value = ChatResponse(
            content="Thought: 无需工具\nFinal Answer: 一切正常", model="deepseek"
        )
        agent = Agent(mock_llm, [], max_steps=5)
        result = agent.run("检查状态")
        assert result == "一切正常"
        assert mock_llm.chat.call_count == 1

    def test_one_tool_call_then_answer(self, mock_llm):
        mock_llm.chat.side_effect = [
            ChatResponse(content="Thought: 需要检查\nAction: validate\nAction Input: {}", model="deepseek"),
            ChatResponse(content="Thought: 完成\nFinal Answer: 验证通过", model="deepseek"),
        ]
        exec_records = []

        def validate(args):
            exec_records.append(args)
            return "结构完整"

        agent = Agent(mock_llm, [(_tool("validate"), validate)])
        result = agent.run("验证一下")
        assert result == "验证通过"
        assert mock_llm.chat.call_count == 2
        assert len(exec_records) == 1

    def test_multiple_tool_calls(self, mock_llm):
        mock_llm.chat.side_effect = [
            ChatResponse(content="Thought: 先验证\nAction: validate\nAction Input: {}", model="deepseek"),
            ChatResponse(content="Thought: 再融合检查\nAction: fusion-check\nAction Input: {}", model="deepseek"),
            ChatResponse(content="Thought: 完成\nFinal Answer: 全部通过", model="deepseek"),
        ]
        calls = []

        def validate(args):
            calls.append("validate")
            return "OK"

        def fusion(args):
            calls.append("fusion")
            return "OK"

        agent = Agent(mock_llm, [(_tool("validate"), validate), (_tool("fusion-check"), fusion)])
        result = agent.run("全面检查")
        assert result == "全部通过"
        assert calls == ["validate", "fusion"]

    def test_max_steps_reached(self, mock_llm):
        mock_llm.chat.return_value = ChatResponse(
            content="Thought: 继续\nAction: validate\nAction Input: {}", model="deepseek"
        )

        def validate(args):
            return "结果"

        agent = Agent(mock_llm, [(_tool("validate"), validate)], max_steps=3)
        result = agent.run("检查")
        assert "达到最大步数" in result
        assert mock_llm.chat.call_count == 3

    def test_malformed_action_retry(self, mock_llm):
        mock_llm.chat.side_effect = [
            ChatResponse(content="这是一段乱写的文本", model="deepseek"),
            ChatResponse(content="Thought: 修正\nAction: validate\nAction Input: {}", model="deepseek"),
            ChatResponse(content="Thought: 完成\nFinal Answer: 好了", model="deepseek"),
        ]

        def validate(args):
            return "ok"

        agent = Agent(mock_llm, [(_tool("validate"), validate)], max_steps=5)
        result = agent.run("测试")
        assert result == "好了"
        assert mock_llm.chat.call_count == 3

    def test_tool_execution_failure(self, mock_llm):
        mock_llm.chat.side_effect = [
            ChatResponse(content="Thought: 调用工具\nAction: failing\nAction Input: {}", model="deepseek"),
            ChatResponse(content="Thought: 完成\nFinal Answer: 已处理", model="deepseek"),
        ]

        def failing(args):
            raise ValueError("崩溃")

        agent = Agent(mock_llm, [(_tool("failing"), failing)])
        result = agent.run("测试")
        assert result == "已处理"


class TestInit:
    def test_accepts_tool_pairs(self):
        def fn(args):
            return ""

        agent = Agent(MagicMock(spec=LLM), [(_tool("t1"), fn)])
        assert len(agent._tools) == 1
        assert "t1" in agent._tools

