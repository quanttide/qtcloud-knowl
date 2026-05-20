#!/usr/bin/env python3
"""
集成测试：验证 ReActAgent 能正确调用工具完成任务。

从 Vault 读取 API key，使用 default_agent 执行一次完整对话。
"""

import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _load_vault_key() -> str:
    """从本地 Vault 读取 DeepSeek API key。"""
    try:
        result = subprocess.run(
            ["vault", "kv", "get", "-field=api_key", "quanttide/deepseek"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0:
            return result.stdout.strip()
        print(f"Vault 错误: {result.stderr}")
    except Exception as e:
        print(f"Vault 调用失败: {e}")
    return ""


def main():
    api_key = _load_vault_key()
    if not api_key:
        print("错误: 无法从 Vault 读取 API key")
        sys.exit(1)

    os.environ["LLM_API_KEY"] = api_key

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
