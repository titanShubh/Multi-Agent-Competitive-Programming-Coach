"""Main graph assembly and compilation."""

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from app.agents.algorithm_expert import algorithm_expert_node
from app.agents.code_review import code_review_node
from app.agents.complexity_analyzer import complexity_analyzer_node
from app.agents.learning_memory import learning_memory_node
from app.agents.problem_analyzer import problem_analyzer_node
from app.agents.state import CoachState
from app.agents.supervisor import supervisor_node
from app.agents.teaching_agent import teaching_agent_node
from app.agents.test_case_generator import test_case_generator_node

# Single persistent memory checkpointer shared across requests
_global_memory_checkpointer = MemorySaver()


def route_from_supervisor(state: CoachState) -> str:
    """Determine the next step dynamically based on supervisor routing decision."""
    next_agent = state.get("next_agent", "teaching_agent")
    if next_agent == "FINISH":
        return END
    return next_agent


def build_graph() -> StateGraph:
    """Assemble all nodes and edges for the coach supervisor graph."""
    graph = StateGraph(CoachState)
    
    # Add nodes
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("problem_analyzer", problem_analyzer_node)
    graph.add_node("teaching_agent", teaching_agent_node)
    graph.add_node("algorithm_expert", algorithm_expert_node)
    graph.add_node("complexity_analyzer", complexity_analyzer_node)
    graph.add_node("test_case_generator", test_case_generator_node)
    graph.add_node("code_review", code_review_node)
    graph.add_node("learning_memory", learning_memory_node)
    
    # Configure edges
    graph.add_edge(START, "supervisor")
    graph.add_conditional_edges(
        "supervisor",
        route_from_supervisor,
        {
            "problem_analyzer": "problem_analyzer",
            "teaching_agent": "teaching_agent",
            "algorithm_expert": "algorithm_expert",
            "complexity_analyzer": "complexity_analyzer",
            "test_case_generator": "test_case_generator",
            "code_review": "code_review",
            "learning_memory": "learning_memory",
            END: END,
        }
    )
    
    # Every agent loops back to supervisor to determine next step
    for agent in [
        "problem_analyzer", "teaching_agent", "algorithm_expert",
        "complexity_analyzer", "test_case_generator", "code_review",
        "learning_memory"
    ]:
        graph.add_edge(agent, "supervisor")
    
    return graph


def get_compiled_graph(checkpointer=None):
    """Compile graph with default memory checkpointer for conversation memory."""
    graph = build_graph()
    if checkpointer is None:
        checkpointer = _global_memory_checkpointer
    return graph.compile(checkpointer=checkpointer)
