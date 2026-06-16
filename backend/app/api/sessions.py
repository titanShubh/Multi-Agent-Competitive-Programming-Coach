"""Coaching sessions API endpoints."""

import json
import re
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.graph import get_compiled_graph
from app.db.models import User
from app.dependencies import get_current_user, get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.session import SessionCreate, SessionListResponse, SessionResponse
from app.services import session_service


def strip_reasoning_block(text: str) -> str:
    """Strip the <reasoning>...</reasoning> block from the text."""
    return re.sub(r"<reasoning>.*?</reasoning>", "", text, flags=re.DOTALL).strip()


def parse_reasoning_block(text: str) -> dict | None:
    """Parse reasoning block from text (either XML tags or JSON)."""
    match = re.search(r"<reasoning>(.*?)</reasoning>", text, flags=re.DOTALL)
    if not match:
        return None
    content = match.group(1).strip()
    
    # Try parsing as JSON first
    try:
        return json.loads(content)
    except Exception:
        pass
        
    # If not JSON, parse as XML-like tags
    frame = {}
    tags = [
        "current_understanding",
        "key_observation",
        "why_it_matters",
        "why_not_direct_answer",
        "next_step_for_student",
        "pedagogical_goal",
    ]
    for tag in tags:
        tag_match = re.search(f"<{tag}>(.*?)</{tag}>", content, flags=re.DOTALL)
        if tag_match:
            frame[tag] = tag_match.group(1).strip()
            
    # Parse possible_approaches (which has multiple <approach> tags)
    approaches_match = re.search(r"<possible_approaches>(.*?)</possible_approaches>", content, flags=re.DOTALL)
    if approaches_match:
        approaches_content = approaches_match.group(1)
        approaches = re.findall(r"<approach>(.*?)</approach>", approaches_content, flags=re.DOTALL)
        frame["possible_approaches"] = [a.strip() for a in approaches]
        
    return frame


class StreamingFilter:
    def __init__(self):
        self.buffer = ""
        self.inside_reasoning = False
        self.reasoning_content = ""
        self.done_reasoning = False

    def feed(self, chunk: str) -> tuple[str, dict | None]:
        """
        Feed a token chunk. Returns (clean_chunk, reasoning_frame_dict).
        """
        if self.done_reasoning:
            return chunk, None

        self.buffer += chunk

        if not self.inside_reasoning:
            if "<reasoning>" in self.buffer:
                parts = self.buffer.split("<reasoning>", 1)
                clean_before = parts[0]
                self.inside_reasoning = True
                self.buffer = parts[1]
                return clean_before, None
            else:
                prefix_candidate = "<reasoning>"
                is_prefix = False
                stripped_buf = self.buffer.lstrip()
                if not stripped_buf:
                    return "", None
                for i in range(1, len(prefix_candidate) + 1):
                    if prefix_candidate[:i].startswith(stripped_buf):
                        is_prefix = True
                        break
                
                if is_prefix:
                    return "", None
                else:
                    released = self.buffer
                    self.buffer = ""
                    self.done_reasoning = True
                    return released, None

        if self.inside_reasoning:
            if "</reasoning>" in self.buffer:
                parts = self.buffer.split("</reasoning>", 1)
                self.reasoning_content += parts[0]
                self.inside_reasoning = False
                self.done_reasoning = True
                self.buffer = ""
                
                reasoning_frame = {}
                try:
                    reasoning_frame = json.loads(self.reasoning_content.strip())
                except Exception as e:
                    print(f"StreamingFilter: failed to parse JSON reasoning content: {e}")
                    try:
                        content_str = self.reasoning_content.strip()
                        if "{" in content_str:
                            json_str = content_str[content_str.index("{"):content_str.rindex("}") + 1]
                            reasoning_frame = json.loads(json_str)
                    except Exception:
                        pass
                
                clean_after = parts[1].lstrip()
                return clean_after, reasoning_frame
            else:
                safe_len = len("</reasoning>")
                if len(self.buffer) > safe_len:
                    keep_len = safe_len
                    move_len = len(self.buffer) - keep_len
                    self.reasoning_content += self.buffer[:move_len]
                    self.buffer = self.buffer[move_len:]
                return "", None

    def flush(self) -> tuple[str, dict | None]:
        """
        Flush any remaining buffer at the end of the stream.
        """
        if self.done_reasoning:
            return "", None
            
        released = ""
        reasoning_frame = None
        
        if self.inside_reasoning:
            self.inside_reasoning = False
            self.done_reasoning = True
            try:
                content_str = (self.reasoning_content + self.buffer).strip()
                if "{" in content_str:
                    json_str = content_str[content_str.index("{"):content_str.rindex("}") + 1]
                    reasoning_frame = json.loads(json_str)
            except Exception:
                pass
        else:
            released = self.buffer
            self.done_reasoning = True
            
        self.buffer = ""
        return released, reasoning_frame


router = APIRouter()


@router.post("/", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_coaching_session(
    data: SessionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new coaching session and analyze the problem statement."""
    session = await session_service.create_session(db, current_user.id, data)
    
    # Compile the LangGraph graph
    graph = get_compiled_graph()
    
    # Initial state setup: we send a startup trigger message to trigger analysis
    initial_input = {
        "problem_statement": data.problem_statement,
        "session_mode": data.session_mode,
        "hint_level": 0,
        "messages": [{"role": "user", "content": "Analyze this problem statement."}],
        "session_id": str(session.id),
        "user_id": str(current_user.id),
    }

    config = {"configurable": {"thread_id": str(session.id)}}
    
    try:
        # Run graph synchronously for first initialization analysis
        state = await graph.ainvoke(initial_input, config)
        
        # Capture analysis and initial message
        analysis = state.get("problem_analysis")
        messages = state.get("messages", [])
        
        # Save initial welcome message
        welcome_content = "Welcome to the session! Let's break this down Socratic style."
        welcome_reasoning = None
        if messages:
            raw_welcome = messages[-1].content
            welcome_reasoning = parse_reasoning_block(raw_welcome)
            welcome_content = strip_reasoning_block(raw_welcome)
            
        await session_service.save_message(
            db,
            session.id,
            role="assistant",
            content=welcome_content,
            agent_name="ProblemAnalyzer",
            metadata={
                "problem_analysis": analysis,
                "reasoning_frame": welcome_reasoning
            }
        )
        
        # Update session with problem analysis
        session = await session_service.update_session(
            db,
            session.id,
            current_user.id,
            {"problem_analysis": analysis}
        )
    except Exception as e:
        print(f"Initial session graph compilation/invoke failed: {e}")
        # Save placeholder message if API is down
        await session_service.save_message(
            db,
            session.id,
            role="assistant",
            content="Welcome! Please share your ideas or ask a question to get started.",
            agent_name="System"
        )

    return session


@router.get("/", response_model=SessionListResponse)
async def list_coaching_sessions(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve lists of coaching sessions with pagination."""
    sessions, total = await session_service.list_sessions(db, current_user.id, skip, limit)
    return {"sessions": sessions, "total": total}


@router.get("/{session_id}", response_model=SessionResponse)
async def get_coaching_session(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve coaching session details."""
    session = await session_service.get_session(db, session_id, current_user.id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    return session


@router.get("/{session_id}/messages")
async def get_session_messages(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve all messages for a specific coaching session."""
    session = await session_service.get_session(db, session_id, current_user.id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    messages = await session_service.get_messages(db, session_id)
    return messages



async def ensure_graph_state_seeded(db, session, graph, config, current_user):
    """Seed the LangGraph checkpointer state from DB if it is empty (e.g. after server restart)."""
    state = await graph.aget_state(config)
    if not state.values:
        db_messages = await session_service.get_messages(db, session.id)
        
        from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
        history = []
        
        # We seed the checkpointer state with all messages EXCEPT the last one
        # because the last one is the active user message which will be passed in input_data
        messages_to_seed = db_messages[:-1] if db_messages else []
        
        for m in messages_to_seed:
            if m.role == "user":
                history.append(HumanMessage(content=m.content))
            elif m.role == "assistant":
                additional_kwargs = {}
                if m.message_metadata and "reasoning_frame" in m.message_metadata:
                    additional_kwargs["reasoning_frame"] = m.message_metadata["reasoning_frame"]
                history.append(AIMessage(content=m.content, additional_kwargs=additional_kwargs))
            elif m.role == "system":
                history.append(SystemMessage(content=m.content))
        
        await graph.aupdate_state(
            config,
            {
                "problem_statement": session.problem_statement,
                "session_mode": session.session_mode,
                "hint_level": session.hint_level,
                "max_hint_used": session.max_hint_used,
                "problem_analysis": session.problem_analysis,
                "session_id": str(session.id),
                "user_id": str(current_user.id),
                "messages": history,
            }
        )


@router.post("/{session_id}/chat/stream")
async def stream_chat(
    session_id: UUID,
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Server-Sent Events streaming chat endpoint for interactive Socratic sessions."""
    session = await session_service.get_session(db, session_id, current_user.id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    # Save user message
    await session_service.save_message(db, session_id, role="user", content=request.message)

    async def event_generator():
        graph = get_compiled_graph()
        config = {"configurable": {"thread_id": str(session_id)}}

        # Seed state from DB if checkpointer is empty
        await ensure_graph_state_seeded(db, session, graph, config, current_user)

        input_data = {
            "messages": [{"role": "user", "content": request.message}],
            "problem_statement": session.problem_statement,
            "session_mode": session.session_mode,
            "hint_level": session.hint_level,
            "max_hint_used": session.max_hint_used,
            "session_id": str(session_id),
            "user_id": str(current_user.id),
        }

        if request.include_code:
            input_data["user_code"] = request.include_code
            input_data["code_language"] = request.language or "C++"

        assistant_message_accumulated = ""
        last_reasoning_frame = None
        active_agent = "teaching_agent"
        
        stream_filter = StreamingFilter()
        current_streaming_node = None
        conversational_agents = {
            "teaching_agent",
            "algorithm_expert",
            "complexity_analyzer",
            "test_case_generator",
            "code_review"
        }

        try:
            # Stream graph events
            async for event in graph.astream_events(input_data, config, version="v2"):
                event_type = event.get("event")
                
                # Model token streaming
                if event_type == "on_chat_model_stream":
                    node_name = event.get("metadata", {}).get("langgraph_node")
                    if node_name in conversational_agents:
                        if node_name != current_streaming_node:
                            current_streaming_node = node_name
                            stream_filter = StreamingFilter()
                            active_agent = node_name

                        token = event["data"]["chunk"].content
                        if token:
                            clean_chunk, reasoning_frame = stream_filter.feed(token)
                            if reasoning_frame:
                                last_reasoning_frame = reasoning_frame
                                yield f"data: {json.dumps({'type': 'reasoning_frame', 'reasoning_frame': last_reasoning_frame})}\n\n"
                            if clean_chunk:
                                assistant_message_accumulated += clean_chunk
                                yield f"data: {json.dumps({'type': 'token', 'content': clean_chunk, 'agent': active_agent})}\n\n"
                
                # Node transition starting
                elif event_type == "on_chain_start" and event.get("name") == "supervisor":
                    yield f"data: {json.dumps({'type': 'agent_start', 'agent': 'supervisor'})}\n\n"
                    
                # Node transition complete, capturing outputs
                elif event_type == "on_chain_end":
                    # Capture reasoning frame details from output state if available
                    output = event.get("data", {}).get("output", {})
                    if isinstance(output, dict):
                        if "reasoning_frame" in output and output["reasoning_frame"]:
                            last_reasoning_frame = output["reasoning_frame"]
                            yield f"data: {json.dumps({'type': 'reasoning_frame', 'reasoning_frame': last_reasoning_frame})}\n\n"
                        if "current_agent" in output:
                            active_agent = output["current_agent"]
                            yield f"data: {json.dumps({'type': 'agent_end', 'agent': active_agent})}\n\n"

            # Flush filter at the end
            clean_chunk, reasoning_frame = stream_filter.flush()
            if reasoning_frame:
                last_reasoning_frame = reasoning_frame
                yield f"data: {json.dumps({'type': 'reasoning_frame', 'reasoning_frame': last_reasoning_frame})}\n\n"
            if clean_chunk:
                assistant_message_accumulated += clean_chunk
                yield f"data: {json.dumps({'type': 'token', 'content': clean_chunk, 'agent': active_agent})}\n\n"

            # Save completed assistant response
            if assistant_message_accumulated:
                await session_service.save_message(
                    db,
                    session_id,
                    role="assistant",
                    content=assistant_message_accumulated,
                    agent_name=active_agent,
                    metadata={"reasoning_frame": last_reasoning_frame}
                )

        except Exception as e:
            print(f"Streaming error occurred: {e}")
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
            
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.post("/{session_id}/submit-code", response_model=ChatResponse)
async def submit_code(
    session_id: UUID,
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit solution code to route directly to code review agent."""
    session = await session_service.get_session(db, session_id, current_user.id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    if not request.include_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Code snippet is required"
        )

    # Save user message
    user_msg_content = f"Submitting code for review: \n```\n{request.include_code}\n```"
    await session_service.save_message(db, session_id, role="user", content=user_msg_content)

    graph = get_compiled_graph()
    config = {"configurable": {"thread_id": str(session_id)}}

    # Seed state from DB if checkpointer is empty
    await ensure_graph_state_seeded(db, session, graph, config, current_user)

    input_data = {
        "messages": [{"role": "user", "content": request.message}],
        "problem_statement": session.problem_statement,
        "session_mode": session.session_mode,
        "hint_level": session.hint_level,
        "max_hint_used": session.max_hint_used,
        "user_code": request.include_code,
        "code_language": request.language or "C++",
        "session_id": str(session_id),
        "user_id": str(current_user.id),
        "next_agent": "code_review"  # Force routing directly to code review
    }

    try:
        state = await graph.ainvoke(input_data, config)
        messages = state.get("messages", [])
        
        content = "I've reviewed your code. Let's look at it."
        reasoning = state.get("reasoning_frame", {})
        
        if messages:
            raw_content = messages[-1].content
            parsed_reasoning = parse_reasoning_block(raw_content)
            if parsed_reasoning:
                reasoning = parsed_reasoning
            content = strip_reasoning_block(raw_content)
            
        # Save assistant message
        await session_service.save_message(
            db,
            session_id,
            role="assistant",
            content=content,
            agent_name="CodeReview",
            metadata={"reasoning_frame": reasoning}
        )

        return {
            "content": content,
            "agent_name": "CodeReview",
            "reasoning_frame": reasoning,
            "hint_level": session.hint_level,
            "session_mode": session.session_mode
        }
    except Exception as e:
        print(f"Code review invocation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Code review failed: {str(e)}"
        )


@router.patch("/{session_id}", response_model=SessionResponse)
async def update_session_status(
    session_id: UUID,
    updates: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update coaching session parameters or change its state/status."""
    session = await session_service.update_session(db, session_id, current_user.id, updates)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    return session
