"""Teaching Agent node."""

import json
import re

from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI

from app.agents.prompts.teaching import (
    BASE_TEACHING_INSTRUCTIONS,
    LEARNING_MODE_RULES,
    CONTEST_MODE_RULES,
    DEBRIEF_MODE_RULES,
    FINAL_CHECKLIST,
    TOPIC_REGISTRY
)
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

    # Extract the user's latest query
    latest_query = ""
    for msg in reversed(state.get("messages", [])):
        if msg.type == "human" or (hasattr(msg, "role") and msg.role == "user"):
            latest_query = msg.content
            break

    # 1. Dynamic Topic Extraction & Socratic Steps Mapping
    categories = []
    if analysis and isinstance(analysis, dict):
        categories = analysis.get("categories", [])
    
    text_to_search = (latest_query.lower() + " " + " ".join([str(c).lower() for c in categories]))
    
    matched_topic_steps = []
    selected_few_shots = [TOPIC_REGISTRY["general"]["prompt"]]
    
    for topic_key, topic_data in TOPIC_REGISTRY.items():
        if topic_key in ("general", "code"):
            continue
        keywords = topic_data.get("keywords", [])
        if any(kw in text_to_search for kw in keywords):
            matched_topic_steps.append(
                f"--- [Active Socratic Steps for {topic_key.upper()}] ---\n{topic_data['socratic_steps']}"
            )
            selected_few_shots.append(topic_data["prompt"])

    # Load code generation examples if user code is active and hint level is high
    if user_code and hint_lvl >= 4 and "code" in TOPIC_REGISTRY:
        selected_few_shots.append(TOPIC_REGISTRY["code"]["prompt"])

    # 2. Dynamic Persona style guide lookup/synthesis
    persona_instructions = ""
    mentor_keywords = ["act like", "mentor", "teach like", "explain like", "coach", "persona", "behave like"]
    query_lower = latest_query.lower()
    
    if any(kw in query_lower for kw in mentor_keywords):
        predefined_mentors = {
            "vivek gupta": (
                "Name: Vivek Gupta (AlgoZenith Founder / World Finalist)\n"
                "Tone: Extremely energetic, structured, and intuition-first. Uses encouraging phrases like 'Are you guys with me?' and 'Constraint is the king!'.\n"
                "Pedagogy: Stresses defining the state variables and base cases before writing any transitions. Speaks enthusiastically, highlighting edge cases."
            ),
            "errichto": (
                "Name: Errichto (Kamil Debowski)\n"
                "Tone: Calm, clear, and highly visual. Uses simple analogies and avoids over-complicated math jargon.\n"
                "Pedagogy: Leads the student to draw-and-simulate manual examples on small inputs. Hates copy-pasting template code."
            ),
            "colin galen": (
                "Name: Colin Galen\n"
                "Tone: Highly encouraging, friendly, and structured. Focuses on breaking tasks into sub-tasks (Task 1, Task 2).\n"
                "Pedagogy: Addresses developer anxiety and focus. Guide the student to identify common traps and avoid panicking during contests."
            ),
            "william lin": (
                "Name: William Lin\n"
                "Tone: Direct, fast-paced, and highly optimization-focused.\n"
                "Pedagogy: Nudges the student toward mathematical shortcuts, clean code, and runtime performance."
            )
        }
        
        matched_mentor = None
        for mentor in predefined_mentors:
            if mentor in query_lower:
                matched_mentor = mentor
                break
                
        if matched_mentor:
            persona_instructions = f"\n# TUTOR PERSONA ADAPTATION\nYou must adopt the following persona:\n{predefined_mentors[matched_mentor]}\n"
        else:
            # Dynamically extract persona from LLM knowledge base (YouTube/Codeforces blogs)
            match = re.search(r"(?:act|explain|teach|coach|behave)\s+like\s+([a-zA-Z\s]+)", query_lower)
            if match:
                name = match.group(1).strip()
                try:
                    temp_model = ChatOpenAI(
                        model=settings.llm_model,
                        temperature=0.0,
                        api_key=settings.openai_api_key,
                    )
                    persona_query = (
                        f"Based on YouTube videos, tutorials, and Codeforces blogs, summarize the competitive programming coaching style, tone, and teaching methods of '{name}'. "
                        f"Provide a 2-sentence summary of their style for an AI tutor to adopt."
                    )
                    res = await temp_model.ainvoke(persona_query)
                    summary = res.content.strip()
                    persona_instructions = f"\n# TUTOR PERSONA ADAPTATION\nYou must adopt the following persona:\nName: {name.title()}\nStyle/Tone: {summary}\n"
                except Exception as e:
                    print(f"Error compiling dynamic persona: {e}")

    # 3. Assemble Dynamic Prompts
    prompt_parts = [BASE_TEACHING_INSTRUCTIONS]
    session_mode = state.get("session_mode", "learning")

    if session_mode == "contest":
        prompt_parts.append(CONTEST_MODE_RULES)
    else:
        prompt_parts.append(LEARNING_MODE_RULES)
        
        # Inject active topic steps
        if matched_topic_steps:
            prompt_parts.append("\n# ACTIVE SOCRATIC METHOD STEPS\nFollow these steps to guide the student:\n" + "\n".join(matched_topic_steps))
            
        # Inject tutor persona details
        if persona_instructions:
            prompt_parts.append(persona_instructions)
            
        # Inject Socratic few-shots
        few_shot_block = "\n--- \n\n# SCRIPTED SOCRATIC EXAMPLES\n" + "\n".join(selected_few_shots)
        prompt_parts.append(few_shot_block)
        
    prompt_parts.append(FINAL_CHECKLIST)
    system_prompt = "\n".join(prompt_parts)

    messages = [
        {"role": "system", "content": f"{system_prompt}\n\n{context}"}
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
