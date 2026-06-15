"""Learning Memory agent node."""

import json

from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from app.agents.prompts.learning_memory import LEARNING_MEMORY_PROMPT
from app.agents.state import CoachState


class TopicProficiencyEntry(BaseModel):
    score: float = Field(description="Proficiency score from 0.0 to 1.0")
    problems_attempted: int = Field(default=1, description="Problems attempted in this topic")
    problems_solved: int = Field(default=0, description="Problems solved in this topic")


class CommonMistakeEntry(BaseModel):
    mistake: str = Field(description="Mistake category / name")
    count: int = Field(default=1, description="Number of times this mistake occurred")


class LearningProfileUpdateSchema(BaseModel):
    topic_proficiency: dict[str, TopicProficiencyEntry] = Field(description="Dictionary mapping topic names to stats")
    weak_topics: list[str] = Field(description="List of weak topics identified")
    strong_topics: list[str] = Field(description="List of strong topics identified")
    common_mistakes: list[CommonMistakeEntry] = Field(description="List of common mistakes committed")
    summary: str = Field(description="Socratic summary of learning progress in this session")


async def learning_memory_node(state: CoachState) -> dict:
    """Analyze conversation and generate structured learning updates."""
    from app.config import get_settings
    settings = get_settings()

    model = ChatOpenAI(
        model=settings.llm_model,
        temperature=0,
        api_key=settings.openai_api_key,
    ).with_structured_output(LearningProfileUpdateSchema)

    # Compile the full transcript of messages
    history = "\n".join([
        f"{'User' if msg.type == 'human' else 'Coach'}: {msg.content}"
        for msg in state["messages"]
    ])

    try:
        profile_update = await model.ainvoke(f"{LEARNING_MEMORY_PROMPT}\n\nCoaching History:\n{history}")
        update_dict = profile_update.model_dump()
    except Exception as e:
        print(f"Learning memory structured output failed: {e}")
        fallback_model = ChatOpenAI(
            model=settings.llm_model,
            temperature=0,
            api_key=settings.openai_api_key,
        )
        response_msg = await fallback_model.ainvoke(f"{LEARNING_MEMORY_PROMPT}\n\nCoaching History:\n{history}")
        content_str = response_msg.content.strip()
        try:
            if "{" in content_str:
                json_str = content_str[content_str.index("{"):content_str.rindex("}") + 1]
                update_dict = json.loads(json_str)
            else:
                raise ValueError("No JSON found")
        except Exception:
            update_dict = {
                "topic_proficiency": {},
                "weak_topics": [],
                "strong_topics": [],
                "common_mistakes": [],
                "summary": "Coaching session completed."
            }

    ai_msg = AIMessage(
        content=f"Coaching stats updated: {update_dict.get('summary')}",
        name="LearningMemory"
    )

    return {
        "user_profile": update_dict,
        "messages": [ai_msg],
        "current_agent": "learning_memory"
    }
