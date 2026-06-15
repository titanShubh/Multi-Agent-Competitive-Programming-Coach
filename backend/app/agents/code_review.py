"""Code Review agent node."""

import json

from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI

from app.agents.prompts.code_review import CODE_REVIEW_PROMPT
from app.agents.state import CoachState


async def code_review_node(state: CoachState) -> dict:
    """Analyze student-submitted code and identify bugs/optimizations without rewriting."""
    from app.config import get_settings
    settings = get_settings()

    model = ChatOpenAI(
        model=settings.llm_model,
        temperature=0.1,
        api_key=settings.openai_api_key,
    )

    user_code = state.get("user_code", "")
    code_lang = state.get("code_language", "C++")
    
    code_context = f"\n\nStudent's Submitted Code ({code_lang}):\n```\n{user_code}\n```"

    messages = [
        {"role": "system", "content": CODE_REVIEW_PROMPT + code_context}
    ] + [
        {"role": msg.role if hasattr(msg, "role") else ("user" if msg.type == "human" else "assistant"), "content": msg.content}
        for msg in state["messages"][-10:]
    ]

    try:
        response = await model.ainvoke(messages)
        content = response.content.strip()
    except Exception as e:
        print(f"Code reviewer invoke failed: {e}")
        content = "Let's review your code snippet and look for bugs or logic flaws."

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
            print(f"Failed to parse reasoning frame in code review: {e}")

    ai_msg = AIMessage(
        content=clean_content,
        name="CodeReview",
        additional_kwargs={"reasoning_frame": reasoning_frame}
    )

    return {
        "messages": [ai_msg],
        "reasoning_frame": reasoning_frame,
        "current_agent": "code_review"
    }
