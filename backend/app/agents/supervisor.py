"""Supervisor agent node that routes to specialized agents."""

import json

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.agents.prompts.supervisor import SUPERVISOR_PROMPT
from app.agents.state import CoachState
from app.config import get_settings


async def supervisor_node(state: CoachState) -> dict:
    """Decide which agent to route to next."""
    current_agent = state.get("current_agent", "none")
    
    # If a responder agent just ran, terminate the graph turn to return control to the user
    if current_agent in [
        "problem_analyzer", "teaching_agent", "algorithm_expert",
        "complexity_analyzer", "test_case_generator", "code_review",
        "learning_memory"
    ]:
        print(f"--- [Supervisor] {current_agent} just completed. Routing to: FINISH ---")
        return {"next_agent": "FINISH", "current_agent": "supervisor"}

    settings = get_settings()
    model = ChatOpenAI(
        model=settings.llm_model,
        temperature=0,
        api_key=settings.openai_api_key,
    )

    # Build context for routing decision
    problem_analyzed = state.get("problem_analysis") is not None
    user_code_submitted = state.get("user_code") is not None
    user_profile_available = state.get("user_profile") is not None


    context = f"""Current State:
- Session Mode: {state.get('session_mode', 'learning')}
- Hint Level: {state.get('hint_level', 0)}
- Current Agent: {state.get('current_agent', 'none')}
- Problem Analyzed: {problem_analyzed}
- User Code Submitted: {user_code_submitted}
- User Profile Available: {user_profile_available}
"""

    messages = [
        SystemMessage(content=SUPERVISOR_PROMPT),
        HumanMessage(content=context),
    ] + state["messages"][-10:]  # Last 10 messages for context

    try:
        response = await model.ainvoke(messages)
        content = response.content.strip()
        
        # Parse JSON
        if "{" in content:
            json_str = content[content.index("{"):content.rindex("}") + 1]
            decision = json.loads(json_str)
            next_agent = decision.get("next_agent", "teaching_agent")
        else:
            next_agent = "teaching_agent"
    except Exception as e:
        print(f"Supervisor parsing error: {e}")
        next_agent = "teaching_agent"

    # Validate agent name
    valid_agents = [
        "problem_analyzer", "teaching_agent", "algorithm_expert",
        "complexity_analyzer", "test_case_generator", "code_review",
        "learning_memory", "FINISH"
    ]
    if next_agent not in valid_agents:
        next_agent = "teaching_agent"

    print(f"--- [Supervisor] routing context: Problem Analyzed={problem_analyzed}, routing to: {next_agent} ---")
    return {"next_agent": next_agent, "current_agent": "supervisor"}

