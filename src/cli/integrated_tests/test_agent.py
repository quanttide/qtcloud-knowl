#!/usr/bin/env python3
"""
集成测试：验证 ReActAgent 能正确调用工具完成任务。

从 Vault 读取 API key，使用 default_agent 执行一次完整对话。
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    # 从 Vault 获取 API key（通过库的 config 机制，支持 env/vault/.env）
    from quanttide_agent.config import settings

    if not settings.llm_api_key:
        print("错误: LLM_API_KEY 未配置。检查 vault 或 LLM_API_KEY 环境变量。")
        sys.exit(1)

    from quanttide_agent import Message, ReActAgent
    from app.agent import default_agent

    agent = default_agent()

    tools_desc = "\n".join(f"- {t.name}: {t.description}" for t in agent._tools.values())

    print("=== 智能体可用工具 ===")
    print(tools_desc)
    print()

    task = "检查所有领域的结构完整性和跨领域融合情况"
    print(f"=== 用户: {task} ===")
    print()

    result = agent.run([
        Message(role="system", content=ReActAgent.system_prompt(tools_desc)),
        Message(role="user", content=task),
    ])

    print(f"=== 智能体回答 ===")
    print(result)


if __name__ == "__main__":
    main()
