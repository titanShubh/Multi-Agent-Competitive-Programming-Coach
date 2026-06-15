"""Algorithm Expert agent node."""

import json

from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI

from app.agents.prompts.algorithm_expert import ALGORITHM_EXPERT_PROMPT
from app.agents.state import CoachState


async def algorithm_expert_node(state: CoachState) -> dict:
    """Pedagogical explanation of competitive programming algorithms."""
    from app.config import get_settings
    settings = get_settings()

    model = ChatOpenAI(
        model=settings.llm_model,
        temperature=0.3,
        api_key=settings.openai_api_key,
    )

    user_code = state.get("user_code")
    code_lang = state.get("code_language", "C++")
    code_context = f"\n\nStudent's Current Code ({code_lang}):\n```\n{user_code}\n```" if user_code else ""

    messages = [
        {"role": "system", "content": ALGORITHM_EXPERT_PROMPT + code_context}
    ] + [
        {"role": msg.role if hasattr(msg, "role") else ("user" if msg.type == "human" else "assistant"), "content": msg.content}
        for msg in state["messages"][-10:]
    ]

    try:
        response = await model.ainvoke(messages)
        content = response.content.strip()
    except Exception as e:
        print(f"Algorithm expert invoke failed: {e}")
        content = "Let's explore the conceptual steps of this algorithm together."

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
            print(f"Failed to parse reasoning frame in algorithm expert: {e}")

    ai_msg = AIMessage(
        content=clean_content,
        name="AlgorithmExpert",
        additional_kwargs={"reasoning_frame": reasoning_frame}
    )

    return {
        "messages": [ai_msg],
        "reasoning_frame": reasoning_frame,
        "current_agent": "algorithm_expert"
    }
