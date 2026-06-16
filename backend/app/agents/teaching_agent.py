"""Teaching Agent node."""

import json

from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI

from app.agents.prompts.teaching import TEACHING_PROMPT
from app.agents.state import CoachState
from app.agents.utils import parse_and_strip_reasoning



async def teaching_agent_node(state: CoachState) -> dict:
    """Core Socratic coaching node that generates responses and Reasoning Frames."""
    from app.config import get_settings
    settings = get_settings()
    
    model = ChatOpenAI(
        model=settings.llm_model,
        temperature=settings.llm_temperature,
        api_key=settings.openai_api_key,
    )

    # Provide context
    analysis = state.get("problem_analysis")
    profile = state.get("user_profile")
    hint_lvl = state.get("hint_level", 0)
    user_code = state.get("user_code")
    code_lang = state.get("code_language", "C++")
    
    code_context = f"\n- Student's Current Code ({code_lang}):\n```\n{user_code}\n```" if user_code else ""

    context = f"""Coaching Session Context:
- Problem Analysis: {analysis}
- User Profile: {profile}
- Current Hint Level: {hint_lvl}
- Session Mode: {state.get('session_mode', 'learning')}{code_context}
"""

    messages = [
        {"role": "system", "content": f"{TEACHING_PROMPT}\n\n{context}"}
    ] + [
        {"role": msg.role if hasattr(msg, "role") else ("user" if msg.type == "human" else "assistant"), "content": msg.content}
        for msg in state["messages"][-15:]
    ]

    try:
        response = await model.ainvoke(messages)
        content = response.content.strip()
    except Exception as e:
        print(f"Teaching agent invoke failed: {e}")
        content = "Could you explain what you're thinking about the constraints?"

    clean_content, reasoning_frame = parse_and_strip_reasoning(content)

    ai_msg = AIMessage(
        content=clean_content,
        name="TeachingAgent",
        additional_kwargs={"reasoning_frame": reasoning_frame}
    )

    return {
        "messages": [ai_msg],
        "reasoning_frame": reasoning_frame,
        "current_agent": "teaching_agent"
    }
