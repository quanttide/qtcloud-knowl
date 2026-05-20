"""测试 app/agent.py — default_agent 绑定 knowl 工具"""

from unittest.mock import MagicMock

import pytest
from quanttide_agent import LLM

from app.agent import default_agent


class TestDefaultAgent:
    def test_creates_agent_with_four_tools(self):
        agent = default_agent()
        assert len(agent._tools) == 4

    def test_has_validate_tool(self):
        agent = default_agent()
        assert "validate" in agent._tools

    def test_has_fusion_check_tool(self):
        agent = default_agent()
        assert "fusion-check" in agent._tools

    def test_has_abstraction_tool(self):
        agent = default_agent()
        assert "check-abstraction" in agent._tools

    def test_has_cross_domain_tool(self):
        agent = default_agent()
        assert "cross-domain-report" in agent._tools

    def test_accepts_custom_llm(self):
        mock = MagicMock(spec=LLM)
        agent = default_agent(llm=mock)
        assert agent.llm is mock
