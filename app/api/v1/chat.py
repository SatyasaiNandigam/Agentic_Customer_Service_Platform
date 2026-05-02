"""Chat endpoints — POST (sync), POST/stream (SSE), WebSocket (streaming).

Endpoint summary
----------------
POST   /api/v1/chat
    Single-turn synchronous request/response.  Blocks until the full agent
    response is ready.  Use for REST clients that don't need token streaming.

POST   /api/v1/chat/stream
    Single-turn Server-Sent Events stream.  Tokens are emitted as they arrive
    from the LLM.  The connection closes automatically after the ``done`` event.
    Appears in Swagger UI; use this for browser/curl streaming without WebSocket.

WebSocket  /api/v1/chat/ws
    Streaming chat session via LangGraph's ``astream_events()``.  Tokens are
    emitted as they arrive from the LLM so the UI can render progressively.
    The connection stays open for multiple turns — the client sends one message
    per turn and receives a stream of events until ``{"type": "done"}`` signals
    the end of that turn.

GET    /api/v1/chat/history/{session_id}
    Returns the last N messages from the Redis session for the authenticated
    user.  Used to rebuild conversation context in the UI on page reload.

Auth
----
HTTP endpoints: ``Authorization: Bearer <jwt>``
WebSocket:      ``?token=<jwt>`` query parameter

Session management
------------------
A ``session_id`` is a UUID string that acts as the Redis key prefix for a
conversation.  Clients supply it to resume a prior session; if omitted the
server generates a new one and returns it in the response.

WebSocket streaming protocol
-----------------------------
The server sends JSON frames of the following types:

    {"type": "connected", "session_id": "<uuid>"}        — sent on first connect
    {"type": "token", "content": "<text>"}               — partial LLM token
    {"type": "tool_start", "tool": "<tool_name>"}        — tool execution began
    {"type": "tool_end",   "tool": "<tool_name>"}        — tool execution finished
    {"type": "done",  "message": "...", "session_id": "...",
     "intent": "...", "run_id": "..."}                   — turn complete
    {"type": "error", "detail": "..."}                   — non-fatal per-turn error

The client sends one of:
    - Plain text:     the user's message for that turn
    - JSON object:    ``{"message": "<text>", "session_id": "<optional override>"}``
"""

from __future__ import annotations

import json
import uuid
from collections.abc import AsyncGenerator
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, Request, WebSocket, WebSocketDisconnect, status
from fastapi.responses import StreamingResponse
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables.config import RunnableConfig
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.edges import NODE_RESPONSE_GENERATOR, NODE_TOOL_EXECUTOR
from app.auth.middleware import CurrentUser, get_current_user_ws
from app.auth.service import TokenData
from app.config import get_settings
from app.db.session import get_db, get_db_context
from app.dependencies import AgentGraph, RateLimitedUser
from app.guardrails.rate_limiter import peek_message_rate_limit
from app.memory.long_term import load_customer_history

logger = structlog.get_logger(__name__)
router = APIRouter()
settings = get_settings()


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------


class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        description="The user's message. Maximum 4,000 characters.",
    )
    session_id: str | None = Field(
        default=None,
        description=(
            "Provide to continue an existing conversation. "
            "Omit to start a new session — the server will generate a UUID."
        ),
    )


class ChatResponse(BaseModel):
    message: str = Field(..., description="The agent's full response text.")
    session_id: str = Field(
        ...,
        description="Session ID — pass back in subsequent requests to continue this conversation.",
    )
    intent: str = Field(
        ...,
        description="Classified intent for this turn (e.g. 'order_status', 'chitchat').",
    )
    run_id: str | None = Field(
        default=None,
        description="LangSmith run ID — pass to POST /feedback to attach a satisfaction rating.",
    )


class MessageItem(BaseModel):
    role: str = Field(..., description="Message role: 'human', 'ai', 'tool', or 'system'.")
    content: str = Field(..., description="Message content as a plain string.")


class HistoryResponse(BaseModel):
    session_id: str
    messages: list[MessageItem]
    count: int


class SessionItem(BaseModel):
    session_id: str = Field(..., description="Chat session UUID.")
    updated_at: str | None = Field(None, description="ISO timestamp of last activity.")
    last_intent: str = Field(..., description="Intent classified in the last turn.")
    message_count: int = Field(..., description="Number of messages stored in this session.")


class SessionListResponse(BaseModel):
    sessions: list[SessionItem]
    count: int


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _resolve_session_id(
    request_session_id: str | None,
    token_session_id: str | None,
) -> str:
    """Return the session ID to use for this turn.

    Priority:
    1. Explicitly supplied in the request body / query param.
    2. Embedded in the JWT (from a prior session).
    3. Generate a new UUID (first message in a brand-new conversation).
    """
    return request_session_id or token_session_id or str(uuid.uuid4())


def _extract_ai_response(final_state: dict) -> str:
    """Pull the last AIMessage text from the completed graph state.

    Handles both plain-string content and multimodal content lists.
    Tool-use blocks are skipped so only the human-readable text is returned.
    Falls back to a safe error message if no AIMessage is found.
    """
    messages = final_state.get("messages", [])
    for msg in reversed(messages):
        if not isinstance(msg, AIMessage):
            continue

        content = msg.content
        if isinstance(content, str):
            return content

        if isinstance(content, list):
            text_parts = []
            for block in content:
                if isinstance(block, dict):
                    if block.get("type") == "text":
                        text_parts.append(block.get("text", ""))
                    # Skip tool_use blocks
                else:
                    text_parts.append(str(block))
            assembled = " ".join(text_parts).strip()
            if assembled:
                return assembled

    return "I'm sorry, I couldn't generate a response. Please try again."


def _messages_to_items(messages: list) -> list[MessageItem]:
    """Convert LangChain BaseMessage objects to JSON-serialisable MessageItems."""
    items: list[MessageItem] = []
    for msg in messages:
        content = msg.content
        if isinstance(content, list):
            # Flatten multimodal content to plain text
            content = " ".join(
                block.get("text", str(block)) if isinstance(block, dict) else str(block)
                for block in content
            )
        items.append(MessageItem(role=msg.type, content=str(content)))
    return items


async def _load_customer_history(db: AsyncSession, user_id: int, session_id: str) -> dict | None:
    """Load customer history from PostgreSQL. Messages now managed by LangGraph checkpointer."""
    try:
        return await load_customer_history(db, user_id)
    except Exception as exc:
        logger.warning(
            "chat.history_load_failed",
            user_id=user_id,
            session_id=session_id,
            error=str(exc),
        )
        return None


# Fields that must be reset at the start of every turn. The checkpointer carries
# these from the prior turn; stale values would misroute the new turn.
_TURN_RESET: dict = {
    "intent": "unknown",
    "confidence": 0.0,
    "requires_tool": False,
    "needs_escalation": False,
    "selected_tool": None,
    "tool_input": None,
    "tool_result": None,
    "tool_error": None,
    "tool_call_counts": {},
    "input_safe": True,
    "output_safe": True,
    "guardrail_violation": None,
    "tool_retry_count": 0,
    "output_retry_count": 0,
}


def _build_turn_input(
    *,
    user_id: str | int,
    session_id: str,
    user_role,
    user_message: str,
    customer_history: dict | None,
    run_id: uuid.UUID,
    tags: list[str],
) -> tuple[dict, RunnableConfig]:
    """Build the graph input dict and RunnableConfig for one agent turn.

    Centralises the three repeated constructions that existed across the sync,
    SSE, and WebSocket endpoints.  Adding or renaming a state field now requires
    a change in exactly one place.
    """
    graph_input = {
        "messages": [HumanMessage(content=user_message)],
        "user_id": str(user_id),
        "session_id": session_id,
        "user_role": user_role,
        "customer_history": customer_history,
        **_TURN_RESET,
    }
    config = RunnableConfig(
        run_id=run_id,
        tags=tags,
        metadata={"customer_id": str(user_id), "session_id": session_id},
        configurable={"thread_id": session_id},
    )
    return graph_input, config


def _assemble_response_text(streamed_tokens: list[str], final_state: dict) -> str:
    """Assemble the final AI response from streamed tokens or completed graph state."""
    if streamed_tokens:
        return "".join(streamed_tokens).strip()
    if final_state:
        return _extract_ai_response(final_state)
    return "I'm sorry, I couldn't generate a response. Please try again."


async def _process_graph_turn(
    agent_graph,
    graph_input: dict,
    config: RunnableConfig,
    session_id: str,
    run_id: uuid.UUID,
    log,
) -> AsyncGenerator[dict, None]:
    """Shared async generator for one agent turn — protocol-agnostic.

    Streams events from ``astream_events``, yielding plain dicts that callers
    convert to SSE lines or WebSocket frames.  Handles error recovery internally
    so callers only need to forward the yielded dicts and handle
    ``WebSocketDisconnect`` from their own send calls.

    Yields:
        ``{"type": "token",      "content": "..."}``
        ``{"type": "tool_start", "tool": "..."}``
        ``{"type": "tool_end",   "tool": "..."}``
        ``{"type": "error",      "detail": "..."}``   — generator stops after this
        ``{"type": "done",       "message": "...", "session_id": "...",
           "intent": "...", "run_id": "..."}``         — always the last event
    """
    streamed_tokens: list[str] = []
    final_intent: str = "unknown"
    final_state: dict = {}

    try:
        async for event in agent_graph.astream_events(graph_input, config=config, version="v2"):
            event_type: str = event.get("event", "")
            event_name: str = event.get("name", "")
            node: str = event.get("metadata", {}).get("langgraph_node", "")

            if event_type == "on_chat_model_stream" and node == NODE_RESPONSE_GENERATOR:
                chunk = event.get("data", {}).get("chunk")
                if chunk is not None:
                    token_text = _extract_chunk_text(chunk)
                    if token_text:
                        streamed_tokens.append(token_text)
                        yield {"type": "token", "content": token_text}

            elif event_type == "on_chain_start" and node == NODE_TOOL_EXECUTOR and event_name == NODE_TOOL_EXECUTOR:
                yield {"type": "tool_start", "tool": _get_tool_name_from_state(event)}

            elif event_type == "on_chain_end" and node == NODE_TOOL_EXECUTOR and event_name == NODE_TOOL_EXECUTOR:
                yield {"type": "tool_end", "tool": _get_tool_name_from_state(event)}

            elif event_type == "on_chain_end" and event_name == "LangGraph":
                output = event.get("data", {}).get("output", {})
                if isinstance(output, dict):
                    final_state = output
                    final_intent = output.get("intent", "unknown")

    except Exception as exc:
        log.error("graph.stream_error", error=str(exc))
        yield {"type": "error", "detail": "An error occurred. Please try again."}
        return

    ai_response = _assemble_response_text(streamed_tokens, final_state)

    yield {
        "type": "done",
        "message": ai_response,
        "session_id": session_id,
        "intent": final_intent,
        "run_id": str(run_id),
    }
    log.info("graph.turn_complete", intent=final_intent, response_length=len(ai_response))


# ---------------------------------------------------------------------------
# POST /chat  — synchronous single-turn endpoint
# ---------------------------------------------------------------------------


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Synchronous chat turn",
    description=(
        "Send a single user message and receive the agent's complete response. "
        "Blocks until the entire response is ready. "
        "Use the WebSocket endpoint for streaming token-by-token output."
    ),
)
async def post_chat(
    body: ChatRequest,
    user: RateLimitedUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    agent_graph: AgentGraph,
) -> ChatResponse:
    """Handle one synchronous chat turn.

    Flow:
    1. Resolve (or generate) the session_id.
    2. Load prior messages from Redis + customer history from PostgreSQL.
    3. Build the initial AgentState and append the new HumanMessage.
    4. Invoke the LangGraph agent (blocking call).
    5. Extract the last AIMessage from the resulting state.
    6. Persist the new message pair to Redis.
    7. Return the response with session_id, intent, and LangSmith run_id.
    """
    session_id = _resolve_session_id(body.session_id, user.session_id)
    run_id = uuid.uuid4()

    log = logger.bind(
        user_id=user.user_id,
        session_id=session_id,
        run_id=str(run_id),
    )
    log.info("chat.request_received", message_length=len(body.message))

    # -- Load customer context --
    customer_history = await _load_customer_history(db, user.user_id, session_id)

    # -- Build turn input (checkpointer auto-loads prior messages + context_summary) --
    graph_input, config = _build_turn_input(
        user_id=user.user_id,
        session_id=session_id,
        user_role=user.role,
        user_message=body.message,
        customer_history=customer_history,
        run_id=run_id,
        tags=["production", "http"],
    )

    # -- Invoke agent --
    try:
        result = await agent_graph.ainvoke(graph_input, config=config)
    except Exception as exc:
        log.error("chat.graph_invocation_failed", error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request. Please try again.",
        ) from exc

    # -- Extract response fields --
    ai_response = _extract_ai_response(result)
    intent: str = result.get("intent", "unknown")

    log.info("chat.response_sent", intent=intent, response_length=len(ai_response))

    return ChatResponse(
        message=ai_response,
        session_id=session_id,
        intent=intent,
        run_id=str(run_id),
    )


# ---------------------------------------------------------------------------
# POST /chat/stream  — SSE single-turn streaming endpoint
# ---------------------------------------------------------------------------


async def _stream_agent_response(
    agent_graph,
    user_id: str | int,
    user_role,
    session_id: str,
    user_message: str,
    run_id: uuid.UUID,
) -> AsyncGenerator[str, None]:
    """Async generator that yields SSE lines (``data: <json>\\n\\n``) for one turn."""
    log = logger.bind(user_id=user_id, session_id=session_id, run_id=str(run_id))

    async with get_db_context() as db:
        customer_history = await _load_customer_history(db, user_id, session_id)

    graph_input, config = _build_turn_input(
        user_id=user_id,
        session_id=session_id,
        user_role=user_role,
        user_message=user_message,
        customer_history=customer_history,
        run_id=run_id,
        tags=["production", "sse"],
    )

    async for event_dict in _process_graph_turn(
        agent_graph, graph_input, config, session_id, run_id, log
    ):
        yield f"data: {json.dumps(event_dict)}\n\n"


@router.post(
    "/chat/stream",
    summary="Chat (streaming — SSE)",
    description=(
        "Send a single user message and receive the agent's response as a "
        "Server-Sent Events stream. Each ``data:`` line is a JSON object. "
        "The stream ends automatically after the ``done`` event.\n\n"
        "**Event types:**\n"
        "- ``token`` — partial LLM token (render progressively)\n"
        "- ``tool_start`` / ``tool_end`` — tool lifecycle (show/hide spinner)\n"
        "- ``done`` — turn complete with full message + metadata\n"
        "- ``error`` — non-fatal error (stream closes after this)"
    ),
    response_class=StreamingResponse,
    responses={
        200: {
            "content": {
                "text/event-stream": {
                    "schema": {"type": "string"},
                    "example": (
                        'data: {"type":"tool_start","tool":"get_order_status"}\n\n'
                        'data: {"type":"tool_end","tool":"get_order_status"}\n\n'
                        'data: {"type":"token","content":"Your order is"}\n\n'
                        'data: {"type":"done","message":"Your order is on the way.",'
                        '"session_id":"<uuid>","intent":"order_status","run_id":"<uuid>"}\n\n'
                    ),
                }
            },
            "description": "SSE stream of token / tool / done events.",
        }
    },
)
async def post_chat_stream(
    body: ChatRequest,
    user: RateLimitedUser,
    agent_graph: AgentGraph,
) -> StreamingResponse:
    """Stream a single chat turn as Server-Sent Events."""
    session_id = _resolve_session_id(body.session_id, user.session_id)
    run_id = uuid.uuid4()

    logger.bind(
        user_id=user.user_id, session_id=session_id, run_id=str(run_id)
    ).info("sse.request_received", message_length=len(body.message))

    return StreamingResponse(
        _stream_agent_response(
            agent_graph=agent_graph,
            user_id=user.user_id,
            user_role=user.role,
            session_id=session_id,
            user_message=body.message,
            run_id=run_id,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


# ---------------------------------------------------------------------------
# GET /chat/history/{session_id}
# ---------------------------------------------------------------------------


@router.get(
    "/chat/history/{session_id}",
    response_model=HistoryResponse,
    summary="Conversation history",
    description=(
        "Return up to *limit* recent messages for a session from Redis. "
        "Used to rebuild conversation context in the UI on page reload."
    ),
)
async def get_chat_history(
    session_id: str,
    request: Request,
    user: CurrentUser,
    limit: Annotated[int, Query(ge=1, le=50, description="Max messages to return.")] = 20,
) -> HistoryResponse:
    """Return recent messages for a session from the LangGraph checkpoint."""
    log = logger.bind(user_id=user.user_id, session_id=session_id)

    agent_graph = request.app.state.graph
    snapshot = await agent_graph.aget_state({"configurable": {"thread_id": session_id}})
    all_messages = (snapshot.values.get("messages") or []) if snapshot else []
    items = _messages_to_items(all_messages[-limit:])

    log.info("chat.history_retrieved", count=len(items))

    return HistoryResponse(
        session_id=session_id,
        messages=items,
        count=len(items),
    )


# ---------------------------------------------------------------------------
# GET /chat/sessions  — list user's sessions
# ---------------------------------------------------------------------------


@router.get(
    "/chat/sessions",
    response_model=SessionListResponse,
    summary="List user's chat sessions",
    description=(
        "Return up to *limit* recent chat sessions for the authenticated user, "
        "sorted by most-recently-active first. Each item includes the session ID, "
        "last activity timestamp, last classified intent, and message count. "
        "Pass the ``session_id`` to ``POST /chat`` or the WebSocket endpoint to "
        "resume a previous conversation."
    ),
)
async def get_chat_sessions(
    request: Request,
    user: CurrentUser,
    limit: Annotated[int, Query(ge=1, le=50, description="Max sessions to return.")] = 20,
) -> SessionListResponse:
    """List sessions by querying the LangGraph checkpointer directly.

    Uses ``alist`` (filtered by ``customer_id`` metadata) to discover distinct
    thread IDs, then ``aget_state`` to read the current state of each thread.
    Ordering is newest-first as returned by the checkpointer.
    """
    graph = request.app.state.graph
    log = logger.bind(user_id=user.user_id)

    # Step 1: Collect distinct thread_ids for this user, newest-first.
    # alist returns checkpoints across all threads in reverse-chronological order;
    # the first occurrence of each thread_id is its latest checkpoint.
    seen_threads: list[str] = []
    try:
        async for tup in graph.checkpointer.alist(
            config=None,
            filter={"customer_id": str(user.user_id)},
        ):
            thread_id: str = tup.config["configurable"]["thread_id"]
            if thread_id not in seen_threads:
                seen_threads.append(thread_id)
            if len(seen_threads) >= limit:
                break
    except Exception as exc:
        log.warning("chat.sessions_list_error", error=str(exc))

    # Step 2: Fetch the current (latest) state for each thread.
    items: list[SessionItem] = []
    for thread_id in seen_threads:
        try:
            snapshot = await graph.aget_state({"configurable": {"thread_id": thread_id}})
        except Exception as exc:
            log.warning("chat.session_state_error", thread_id=thread_id, error=str(exc))
            continue
        if not snapshot:
            continue

        values = snapshot.values
        messages = values.get("messages", [])
        human_count = sum(1 for m in messages if getattr(m, "type", None) == "human")

        items.append(SessionItem(
            session_id=thread_id,
            updated_at=snapshot.created_at,
            last_intent=values.get("intent") or "unknown",
            message_count=human_count,
        ))

    log.info("chat.sessions_listed", count=len(items))
    return SessionListResponse(sessions=items, count=len(items))


# ---------------------------------------------------------------------------
# WebSocket /chat/ws  — streaming multi-turn endpoint
# ---------------------------------------------------------------------------


@router.websocket("/chat/ws")
async def websocket_chat(
    websocket: WebSocket,
    user: Annotated[TokenData, Depends(get_current_user_ws)],
    session_id_param: Annotated[str | None, Query(alias="session_id")] = None,
) -> None:
    """Stream chat turns over a persistent WebSocket connection.

    Protocol
    --------
    After accepting the connection the server sends::

        {"type": "connected", "session_id": "<uuid>"}

    For each turn the client sends one of:
    - Plain text — treated directly as the user message.
    - JSON object — ``{"message": "...", "session_id": "..."}`` (optional override).

    The server responds with a sequence of events:

    =====================  ==============================================================
    ``token``              Partial LLM token (stream to the UI as it arrives).
    ``tool_start``         Tool execution started (show spinner).
    ``tool_end``           Tool execution finished (hide spinner).
    ``done``               Turn complete; contains the full message + metadata.
    ``error``              Non-fatal per-turn error; the connection stays open.
    =====================  ==============================================================

    The connection remains open until the client disconnects or a fatal server
    error occurs.
    """
    await websocket.accept()

    session_id = _resolve_session_id(session_id_param, user.session_id)
    log = logger.bind(user_id=user.user_id, session_id=session_id)
    log.info("ws.connected")

    # Inform the client of their session_id so they can resume if needed
    await websocket.send_json({"type": "connected", "session_id": session_id})

    try:
        while True:
            # ---- Wait for next user message ----
            try:
                raw = await websocket.receive_text()
            except WebSocketDisconnect:
                log.info("ws.client_disconnected")
                break

            # Parse — accept plain text or JSON
            try:
                payload = json.loads(raw)
                user_message: str = payload.get("message", "")
                # Allow client to switch sessions mid-connection (e.g. opening a past chat)
                if payload.get("session_id"):
                    session_id = payload["session_id"]
                    log = logger.bind(user_id=user.user_id, session_id=session_id)
            except (json.JSONDecodeError, AttributeError):
                user_message = raw

            user_message = user_message.strip()
            if not user_message:
                await websocket.send_json({"type": "error", "detail": "Empty message received."})
                continue

            run_id = uuid.uuid4()
            log = log.bind(run_id=str(run_id))
            log.info("ws.turn_started", message_length=len(user_message))

            # ---- Rate limit check (per-turn) ----
            count = await peek_message_rate_limit(user.user_id)
            if count >= settings.rate_limit_messages_per_minute:
                log.warning(
                    "ws.rate_limit_exceeded",
                    count=count,
                    limit=settings.rate_limit_messages_per_minute,
                )
                await websocket.send_json({
                    "type": "error",
                    "detail": (
                        f"Rate limit exceeded: {count}/{settings.rate_limit_messages_per_minute} "
                        "messages in the last 60 seconds. Please wait before sending another message."
                    ),
                    "retry_after": 60,
                })
                continue

            # ---- Load customer context (new DB session per turn) ----
            async with get_db_context() as db:
                customer_history = await _load_customer_history(
                    db, user.user_id, session_id
                )

            # ---- Build turn input ----
            graph_input, config = _build_turn_input(
                user_id=user.user_id,
                session_id=session_id,
                user_role=user.role,
                user_message=user_message,
                customer_history=customer_history,
                run_id=run_id,
                tags=["production", "websocket"],
            )

            # ---- Stream events ----
            agent_graph = websocket.app.state.graph

            try:
                async for event_dict in _process_graph_turn(
                    agent_graph, graph_input, config, session_id, run_id, log
                ):
                    await websocket.send_json(event_dict)
            except WebSocketDisconnect:
                log.info("ws.client_disconnected_during_stream")
                break
            except Exception as exc:
                log.error("ws.send_error", error=str(exc))
                await websocket.send_json(
                    {"type": "error", "detail": "An error occurred. Please try again."}
                )
                continue

    except WebSocketDisconnect:
        log.info("ws.disconnected")
    except Exception as exc:
        log.error("ws.fatal_error", error=str(exc))
        try:
            await websocket.send_json({"type": "error", "detail": "Unexpected server error."})
            await websocket.close(code=1011)
        except Exception:
            pass
    finally:
        log.info("ws.connection_closed")


# ---------------------------------------------------------------------------
# Token / tool-name extraction helpers (keep out of the hot loop above)
# ---------------------------------------------------------------------------


def _extract_chunk_text(chunk) -> str:
    """Extract plain text from a LangChain streaming chunk (AIMessageChunk).

    Handles:
    - ``chunk.content`` as a plain string.
    - ``chunk.content`` as a list of content blocks (text + tool_use blocks).
      Tool-use blocks are skipped; only ``{"type": "text", "text": "..."}``
      blocks contribute to the output.
    """
    content = getattr(chunk, "content", None)
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            block.get("text", "")
            for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        )
    return ""


def _get_tool_name_from_state(event: dict) -> str:
    """Extract the tool name from a tool_executor chain event.

    The tool name is stored in ``state["selected_tool"]`` which appears in
    the event's input data.  Falls back to ``"unknown_tool"`` if not present.
    """
    data = event.get("data", {})
    # The chain input is the AgentState dict passed to the node
    state_input = data.get("input", {})
    if isinstance(state_input, dict):
        return state_input.get("selected_tool") or "unknown_tool"
    return "unknown_tool"
