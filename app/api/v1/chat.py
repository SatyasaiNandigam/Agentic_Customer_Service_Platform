"""Chat endpoints — POST (sync) and WebSocket (streaming) interfaces to the agent.

Endpoint summary
----------------
POST   /api/v1/chat
    Single-turn synchronous request/response.  Blocks until the full agent
    response is ready.  Use for REST clients that don't need token streaming.

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
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect, status
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables.config import RunnableConfig
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.edges import NODE_RESPONSE_GENERATOR, NODE_TOOL_EXECUTOR
from app.agent.graph import graph
from app.agent.state import create_initial_state
from app.auth.middleware import CurrentUser, get_current_user_ws
from app.auth.service import TokenData
from app.config import get_settings
from app.db.session import get_db, get_db_context
from app.memory.long_term import load_customer_history
from app.memory.short_term import (
    append_messages,
    get_session_messages,
    save_session_context,
)

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


async def _load_history(db: AsyncSession, user_id: int, session_id: str) -> tuple:
    """Load prior messages (Redis) and customer history (PostgreSQL).

    Returns:
        (prior_messages, customer_history) — customer_history may be None.
    """
    prior_messages = await get_session_messages(session_id, limit=20)
    try:
        customer_history = await load_customer_history(db, user_id)
    except Exception as exc:
        logger.warning(
            "chat.history_load_failed",
            user_id=user_id,
            session_id=session_id,
            error=str(exc),
        )
        customer_history = None
    return prior_messages, customer_history


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
    user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
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

    # -- Load context --
    prior_messages, customer_history = await _load_history(db, user.user_id, session_id)

    # -- Build state --
    state = create_initial_state(
        user_id=user.user_id,
        session_id=session_id,
        user_role=user.role,
        max_turns=settings.agent_max_turns,
    )
    state["messages"] = prior_messages + [HumanMessage(content=body.message)]
    state["customer_history"] = customer_history

    config = RunnableConfig(
        run_id=run_id,
        tags=["production", "http"],
        metadata={
            "customer_id": str(user.user_id),
            "session_id": session_id,
        },
    )

    # -- Invoke agent --
    try:
        result = await graph.ainvoke(state, config=config)
    except Exception as exc:
        log.error("chat.graph_invocation_failed", error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request. Please try again.",
        ) from exc

    # -- Extract response fields --
    ai_response = _extract_ai_response(result)
    intent: str = result.get("intent", "unknown")

    # -- Persist turn to Redis --
    await append_messages(
        session_id,
        [HumanMessage(content=body.message), AIMessage(content=ai_response)],
    )
    await save_session_context(
        session_id,
        user_id=user.user_id,
        intent=intent,
    )

    log.info("chat.response_sent", intent=intent, response_length=len(ai_response))

    return ChatResponse(
        message=ai_response,
        session_id=session_id,
        intent=intent,
        run_id=str(run_id),
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
    user: CurrentUser,
    limit: Annotated[int, Query(ge=1, le=50, description="Max messages to return.")] = 20,
) -> HistoryResponse:
    """Return recent messages for a session from Redis."""
    log = logger.bind(user_id=user.user_id, session_id=session_id)

    messages = await get_session_messages(session_id, limit=limit)
    items = _messages_to_items(messages)

    log.info("chat.history_retrieved", count=len(items))

    return HistoryResponse(
        session_id=session_id,
        messages=items,
        count=len(items),
    )


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

            # ---- Load context (new DB session per turn) ----
            async with get_db_context() as db:
                prior_messages, customer_history = await _load_history(
                    db, user.user_id, session_id
                )

            # ---- Build state ----
            state = create_initial_state(
                user_id=user.user_id,
                session_id=session_id,
                user_role=user.role,
                max_turns=settings.agent_max_turns,
            )
            state["messages"] = prior_messages + [HumanMessage(content=user_message)]
            state["customer_history"] = customer_history

            config = RunnableConfig(
                run_id=run_id,
                tags=["production", "websocket"],
                metadata={
                    "customer_id": str(user.user_id),
                    "session_id": session_id,
                },
            )

            # ---- Stream events ----
            streamed_tokens: list[str] = []
            final_intent: str = "unknown"
            final_state: dict = {}

            try:
                async for event in graph.astream_events(state, config=config, version="v2"):
                    event_type: str = event.get("event", "")
                    event_name: str = event.get("name", "")
                    metadata: dict = event.get("metadata", {})
                    node: str = metadata.get("langgraph_node", "")

                    # -- Streaming tokens from the response generator --
                    if (
                        event_type == "on_chat_model_stream"
                        and node == NODE_RESPONSE_GENERATOR
                    ):
                        chunk = event.get("data", {}).get("chunk")
                        if chunk is not None:
                            token_text = _extract_chunk_text(chunk)
                            if token_text:
                                streamed_tokens.append(token_text)
                                await websocket.send_json(
                                    {"type": "token", "content": token_text}
                                )

                    # -- Tool execution lifecycle events --
                    elif event_type == "on_chain_start" and node == NODE_TOOL_EXECUTOR:
                        tool_name = _get_tool_name_from_state(event)
                        await websocket.send_json(
                            {"type": "tool_start", "tool": tool_name}
                        )

                    elif event_type == "on_chain_end" and node == NODE_TOOL_EXECUTOR:
                        tool_name = _get_tool_name_from_state(event)
                        await websocket.send_json(
                            {"type": "tool_end", "tool": tool_name}
                        )

                    # -- Capture final graph output --
                    elif event_type == "on_chain_end" and event_name == "LangGraph":
                        output = event.get("data", {}).get("output", {})
                        if isinstance(output, dict):
                            final_state = output
                            final_intent = output.get("intent", "unknown")

            except WebSocketDisconnect:
                log.info("ws.client_disconnected_during_stream")
                break
            except Exception as exc:
                log.error("ws.graph_stream_error", error=str(exc))
                await websocket.send_json(
                    {"type": "error", "detail": "An error occurred. Please try again."}
                )
                continue

            # ---- Assemble final response ----
            if streamed_tokens:
                # Happy path: tokens were streamed — join them
                ai_response = "".join(streamed_tokens).strip()
            elif final_state:
                # Non-streaming path: guardrail block, direct route, etc.
                ai_response = _extract_ai_response(final_state)
            else:
                ai_response = "I'm sorry, I couldn't generate a response. Please try again."

            # ---- Persist to Redis ----
            await append_messages(
                session_id,
                [HumanMessage(content=user_message), AIMessage(content=ai_response)],
            )
            await save_session_context(
                session_id,
                user_id=user.user_id,
                intent=final_intent,
            )

            # ---- Signal turn complete ----
            await websocket.send_json({
                "type": "done",
                "message": ai_response,
                "session_id": session_id,
                "intent": final_intent,
                "run_id": str(run_id),
            })

            log.info(
                "ws.turn_complete",
                intent=final_intent,
                response_length=len(ai_response),
                streamed=bool(streamed_tokens),
            )

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
