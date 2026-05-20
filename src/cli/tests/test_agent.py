"""测试 ReAct 智能体"""

from unittest.mock import MagicMock

import pytest
from quanttide_agent import ChatResponse, LLM

from app.agent import Action, ActionParser, Message, ReActAgent, Tool


@pytest.fixture
def mock_llm() -> MagicMock:
    return MagicMock(spec=LLM)


def _tool(name: str, desc: str = "", executor=None) -> Tool:
    return Tool(name=name, description=desc, executor=executor)


class TestParseAction:
    def setup_method(self):
        self.parser = ActionParser()

    def test_parse_valid(self):
        result = self.parser.parse("Thought: 需要检查\nAction name: validate\nAction args: {}")
        assert isinstance(result, Action)
        assert result.name == "validate"
        assert result.args == {}

    def test_parse_with_json_args(self):
        result = self.parser.parse(
            'Thought: 检查特定领域\nAction name: validate\nAction args: {"domain": "org-gov"}'
        )
        assert result.name == "validate"
        assert result.args == {"domain": "org-gov"}

    def test_parse_no_action(self):
        assert self.parser.parse("这是一段普通文本") is None

    def test_parse_missing_input(self):
        assert self.parser.parse("Action name: validate\nSomething else") is None

    def test_parse_final_answer(self):
        assert self.parser.parse("Thought: 完成\nFinal Answer: 结果") is None


class TestExecute:
    def test_execute_known_tool(self):
        exec_records = []

        def tool_fn(args):
            exec_records.append(args)
            return "执行成功"

        tool = _tool("my-tool", executor=tool_fn)
        result = tool.execute({"key": "val"})
        assert result == "执行成功"
        assert exec_records == [{"key": "val"}]

    def test_execute_no_executor(self):
        tool = _tool("noop")
        result = tool.execute({})
        assert "未知工具" in result

    def test_execute_tool_error(self):
        def failing_fn(args):
            raise ValueError("工具崩溃")

        tool = _tool("failing", executor=failing_fn)
        result = tool.execute({})
        assert "执行错误" in result
        assert "工具崩溃" in result


class TestRun:
    def _msgs(self, task: str) -> list[Message]:
        return [Message(role="user", content=task)]

    def test_direct_final_answer(self, mock_llm):
        mock_llm.chat.return_value = ChatResponse(
            content="Thought: 无需工具\nFinal Answer: 一切正常", model="deepseek"
        )
        agent = ReActAgent(mock_llm, [], max_steps=5)
        result = agent.run(self._msgs("检查状态"))
        assert result == "一切正常"
        assert mock_llm.chat.call_count == 1

    def test_one_tool_call_then_answer(self, mock_llm):
        mock_llm.chat.side_effect = [
            ChatResponse(content="Thought: 需要检查\nAction name: validate\nAction args: {}", model="deepseek"),
            ChatResponse(content="Thought: 完成\nFinal Answer: 验证通过", model="deepseek"),
        ]
        exec_records = []

        def validate(args):
            exec_records.append(args)
            return "结构完整"

        agent = ReActAgent(mock_llm, [_tool("validate", executor=validate)])
        result = agent.run(self._msgs("验证一下"))
        assert result == "验证通过"
        assert mock_llm.chat.call_count == 2
        assert len(exec_records) == 1

    def test_multiple_tool_calls(self, mock_llm):
        mock_llm.chat.side_effect = [
            ChatResponse(content="Thought: 先验证\nAction name: validate\nAction args: {}", model="deepseek"),
            ChatResponse(content="Thought: 再融合检查\nAction name: fusion-check\nAction args: {}", model="deepseek"),
            ChatResponse(content="Thought: 完成\nFinal Answer: 全部通过", model="deepseek"),
        ]
        calls = []

        def validate(args):
            calls.append("validate")
            return "OK"

        def fusion(args):
            calls.append("fusion")
            return "OK"

        agent = ReActAgent(mock_llm, [_tool("validate", executor=validate), _tool("fusion-check", executor=fusion)])
        result = agent.run(self._msgs("全面检查"))
        assert result == "全部通过"
        assert calls == ["validate", "fusion"]

    def test_max_steps_reached(self, mock_llm):
        mock_llm.chat.return_value = ChatResponse(
            content="Thought: 继续\nAction name: validate\nAction args: {}", model="deepseek"
        )

        def validate(args):
            return "结果"

        agent = ReActAgent(mock_llm, [_tool("validate", executor=validate)], max_steps=3)
        result = agent.run(self._msgs("检查"))
        assert "达到最大步数" in result
        assert mock_llm.chat.call_count == 3

    def test_malformed_action_retry(self, mock_llm):
        mock_llm.chat.side_effect = [
            ChatResponse(content="这是一段乱写的文本", model="deepseek"),
            ChatResponse(content="Thought: 修正\nAction name: validate\nAction args: {}", model="deepseek"),
            ChatResponse(content="Thought: 完成\nFinal Answer: 好了", model="deepseek"),
        ]

        def validate(args):
            return "ok"

        agent = ReActAgent(mock_llm, [_tool("validate", executor=validate)], max_steps=5)
        result = agent.run(self._msgs("测试"))
        assert result == "好了"
        assert mock_llm.chat.call_count == 3

    def test_tool_execution_failure(self, mock_llm):
        mock_llm.chat.side_effect = [
            ChatResponse(content="Thought: 调用工具\nAction name: failing\nAction args: {}", model="deepseek"),
            ChatResponse(content="Thought: 完成\nFinal Answer: 已处理", model="deepseek"),
        ]

        def failing(args):
            raise ValueError("崩溃")

        agent = ReActAgent(mock_llm, [_tool("failing", executor=failing)])
        result = agent.run(self._msgs("测试"))
        assert result == "已处理"


class TestInit:
    def test_accepts_tools(self):
        def fn(args):
            return ""

        agent = ReActAgent(MagicMock(spec=LLM), [Tool(name="t1", executor=fn)])
        assert len(agent._tools) == 1
        assert "t1" in agent._tools

    def test_tool_schema_no_execute(self):
        tool = Tool(name="t1", description="d1")
        assert tool.name == "t1"
        assert tool.executor is None


class TestMessage:
    def test_system_message(self):
        m = Message(role="system", content="你好")
        assert m.to_dict() == {"role": "system", "content": "你好"}

    def test_user_message(self):
        m = Message(role="user", content="hello")
        assert m.to_dict() == {"role": "user", "content": "hello"}

    def test_tool_message(self):
        m = Message(role="tool", content="result", tool_call_id="call_1")
        assert m.to_dict() == {"role": "tool", "content": "result", "tool_call_id": "call_1"}

    def test_assistant_message(self):
        m = Message(role="assistant", content="回复")
        assert m.to_dict() == {"role": "assistant", "content": "回复"}


class TestAction:
    def test_action(self):
        a = Action(name="validate", args={"domain": "test"})
        assert a.name == "validate"
        assert a.args == {"domain": "test"}

    def test_action_default_args(self):
        a = Action(name="validate")
        assert a.args == {}

