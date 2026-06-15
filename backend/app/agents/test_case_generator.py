"""Test Case Generator agent node."""

import json

from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI

from app.agents.prompts.test_cases import TEST_CASE_PROMPT
from app.agents.state import CoachState


async def test_case_generator_node(state: CoachState) -> dict:
    """Generate edge cases, bounds, and adversarial test inputs."""
    from app.config import get_settings
    settings = get_settings()

    model = ChatOpenAI(
        model=settings.llm_model,
        temperature=0.4,
        api_key=settings.openai_api_key,
    )

    user_code = state.get("user_code")
    code_lang = state.get("code_language", "C++")
    code_context = f"\n\nStudent's Current Code ({code_lang}):\n```\n{user_code}\n```" if user_code else ""

    messages = [
        {"role": "system", "content": TEST_CASE_PROMPT + code_context}
    ] + [
        {"role": msg.role if hasattr(msg, "role") else ("user" if msg.type == "human" else "assistant"), "content": msg.content}
        for msg in state["messages"][-10:]
    ]

    try:
        response = await model.ainvoke(messages)
        content = response.content.strip()
    except Exception as e:
        print(f"Test case generator invoke failed: {e}")
        content = "Let's work together to construct some tricky test cases for your solution."

    reasoning_frame = {}
    clean_content = content

    if "<reasoning>" in content and "</reasoning>" in content:
        try:
            start_idx = content.index("<reasoning>") + 11
            end_idx = content.index("</reasoning>")
            json_str = content[start_idx:end_idx].strip()
            reasoning_frame = json.loads(json_str)
            clean_content = content.split("</reasoning>", 1)[1].strip()
        except Exception as e:
            print(f"Failed to parse reasoning frame in test case generator: {e}")

    ai_msg = AIMessage(
        content=clean_content,
        name="TestCaseGenerator",
        additional_kwargs={"reasoning_frame": reasoning_frame}
    )

    return {
        "messages": [ai_msg],
        "reasoning_frame": reasoning_frame,
        "current_agent": "test_case_generator"
    }
