"""Problem Analyzer agent node."""

import json
from typing import Optional

from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from app.agents.prompts.problem_analyzer import PROBLEM_ANALYZER_PROMPT
from app.agents.state import CoachState
from app.config import get_settings


class ConstraintsSchema(BaseModel):
    time_limit: str = Field(description="Time limit (e.g. 1.0s, 2.0s)")
    memory_limit: str = Field(description="Memory limit (e.g. 256MB, 512MB)")
    N: Optional[str] = Field(None, description="Constraints on input size N (e.g. N <= 10^5)")
    other: Optional[str] = Field(None, description="Other constraints if any")


class ProblemAnalysisSchema(BaseModel):
    """Structured CP problem analysis representation."""
    title: str = Field(description="Title of the problem")
    summary: str = Field(description="Brief summary of the problem")
    categories: list[str] = Field(description="Algorithm categories (e.g. DP, Graphs)")
    difficulty: str = Field(description="Difficulty rating (Easy, Medium, Hard, Expert)")
    estimated_rating: int = Field(description="Estimated Codeforces rating (800-3500)")
    constraints: ConstraintsSchema = Field(description="Constraints including time and memory limits")
    key_observations: list[str] = Field(description="Crucial direct observations")
    hidden_observations: list[str] = Field(description="Hidden or deep mathematical observations")
    expected_complexity: str = Field(description="Optimal expected complexity")
    brute_force_complexity: str = Field(description="Brute-force approach complexity")
    similar_problems: list[str] = Field(description="List of similar classic problems")


async def problem_analyzer_node(state: CoachState) -> dict:
    """Analyze the competitive programming problem statement."""
    print("--- [Problem Analyzer] Starting problem analysis ---")
    settings = get_settings()

    
    # We use a structured model here to guarantee parsing stability
    model = ChatOpenAI(
        model=settings.llm_model,
        temperature=0,
        api_key=settings.openai_api_key,
    ).with_structured_output(ProblemAnalysisSchema)

    problem_stmt = state.get("problem_statement", "")
    prompt = f"{PROBLEM_ANALYZER_PROMPT}\n\nProblem Statement:\n{problem_stmt}"

    try:
        structured_analysis = await model.ainvoke(prompt)
        analysis_dict = structured_analysis.model_dump()
    except Exception as e:
        print(f"Structured analysis failed, falling back to unstructured prompt: {e}")
        # Fallback if structured output fails
        fallback_model = ChatOpenAI(
            model=settings.llm_model,
            temperature=0,
            api_key=settings.openai_api_key,
        )
        response = await fallback_model.ainvoke(f"{PROBLEM_ANALYZER_PROMPT}\n\nProblem Statement:\n{problem_stmt}")
        # Parse fallback content
        try:
            content = response.content.strip()
            if "{" in content:
                json_str = content[content.index("{"):content.rindex("}") + 1]
                analysis_dict = json.loads(json_str)
            else:
                raise ValueError("No JSON block found in fallback response")
        except Exception as fallback_err:
            print(f"Fallback parsing failed: {fallback_err}")
            analysis_dict = {
                "title": "Problem Analysis",
                "summary": "Failed to parse problem statement.",
                "categories": ["General"],
                "difficulty": "Unknown",
                "estimated_rating": 0,
                "constraints": {},
                "key_observations": [],
                "hidden_observations": [],
                "expected_complexity": "O(N)",
                "brute_force_complexity": "O(2^N)",
                "similar_problems": []
            }

    # Generate an initial Socratic greeting message introducing the problem analysis
    categories_str = ", ".join(analysis_dict.get("categories", []))
    greeting = (
        f"I've analyzed the problem: **{analysis_dict.get('title')}**.\n\n"
        f"It looks like a **{analysis_dict.get('difficulty')}** problem (Rating: ~{analysis_dict.get('estimated_rating')}) "
        f"involving **{categories_str}**.\n\n"
        f"Let's break this down together. What do you think is the naive/brute-force approach first?"
    )

    ai_message = AIMessage(
        content=greeting,
        name="ProblemAnalyzer"
    )

    return {
        "problem_analysis": analysis_dict,
        "messages": [ai_message],
        "current_agent": "problem_analyzer",
    }
