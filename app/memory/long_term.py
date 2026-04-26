"""Long-term memory — PostgreSQL persistence for conversation history.

Provides two public functions used by the LangGraph agent:

``load_customer_history(db, user_id)``
    Called at graph entry to hydrate ``state["customer_history"]`` with a
    structured snapshot of the user's recent activity drawn from the agent's
    own conversation tables.  Returns the last 5 conversation summaries so
    the response_generator has context about prior sessions without loading
    the full message history.

``persist_session_to_db(db, session_id, user_id, messages, intent)``
    Called on session end (TTL expiry hook or explicit close) to flush the
    active Redis session into PostgreSQL.  Creates or updates the
    ``conversations`` row, bulk-inserts all messages, and marks the session
    as ``archived``.  After a successful flush the Redis keys are deleted so
    stale data does not persist.

Both functions accept an ``AsyncSession`` injected by the FastAPI dependency
(``get_db`` from ``app.dependencies``), never opening their own connections.

Error policy:  database errors are logged and re-raised so the caller can
decide whether to surface them to the user (e.g. the flush on session end
should not crash the chat endpoint — the caller should catch and warn).
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

import structlog
from langchain_core.messages import BaseMessage, messages_to_dict
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.memory.models import (
    Conversation,
    ConversationStatus,
    ConversationSummary,
    Message,
    MessageRole,
)
from app.memory.short_term import delete_session

logger = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Number of past conversation summaries injected into the system prompt.
_HISTORY_SUMMARY_LIMIT = 5

# Max messages returned per conversation for the history snapshot.
_HISTORY_MESSAGES_PER_CONV = 10


# ---------------------------------------------------------------------------
# load_customer_history
# ---------------------------------------------------------------------------


async def load_customer_history(db: AsyncSession, user_id: str) -> dict | None:
    """Load a structured snapshot of the customer's recent activity.

    Queries the agent's conversation tables to build the ``customer_history``
    dict that is stored in ``AgentState`` and injected into the system prompt
    by the response_generator.

    Args:
        db:      Async SQLAlchemy session (injected, not created here).
        user_id: Authenticated user ID from the JWT.

    Returns:
        Dict with shape::

            {
                "recent_conversations": [
                    {
                        "session_id": "...",
                        "started_at": "ISO timestamp",
                        "primary_intent": "order_status",
                        "turn_count": 3,
                        "latest_summary": "Customer asked about order #1234. ...",
                    },
                    ...
                ],
                "total_conversations": <int>,
                "last_contact": "ISO timestamp or null",
            }

        Returns ``None`` if the user has no prior sessions.
    """
    log = logger.bind(user_id=user_id)

    # Fetch the most recent N archived/escalated conversations for this user
    stmt = (
        select(Conversation)
        .where(
            Conversation.user_id == user_id,
            Conversation.status.in_([
                ConversationStatus.archived,
                ConversationStatus.escalated,
            ]),
        )
        .order_by(desc(Conversation.started_at))
        .limit(_HISTORY_SUMMARY_LIMIT)
    )
    result = await db.execute(stmt)
    conversations: list[Conversation] = list(result.scalars().all())

    if not conversations:
        log.debug("long_term.no_history_found")
        return None

    # For each conversation, fetch the latest summary (if any)
    conv_ids = [c.id for c in conversations]
    summaries_stmt = (
        select(ConversationSummary)
        .where(ConversationSummary.conversation_id.in_(conv_ids))
        .order_by(
            ConversationSummary.conversation_id,
            desc(ConversationSummary.covered_up_to_turn),
        )
    )
    summaries_result = await db.execute(summaries_stmt)
    all_summaries: list[ConversationSummary] = list(summaries_result.scalars().all())

    # Build a lookup: conversation_id → latest summary text
    latest_summary: dict[int, str] = {}
    for s in all_summaries:
        if s.conversation_id not in latest_summary:
            latest_summary[s.conversation_id] = s.summary_text

    # Total conversation count for this user
    total_stmt = select(Conversation).where(Conversation.user_id == user_id)
    total_result = await db.execute(total_stmt)
    total_count = len(total_result.scalars().all())

    recent_convs = [
        {
            "session_id": c.session_id,
            "started_at": c.started_at.isoformat() if c.started_at else None,
            "primary_intent": c.primary_intent,
            "turn_count": c.turn_count,
            "latest_summary": latest_summary.get(c.id),
        }
        for c in conversations
    ]

    last_contact = conversations[0].started_at.isoformat() if conversations[0].started_at else None

    log.info(
        "long_term.history_loaded",
        conversation_count=len(recent_convs),
        total_conversations=total_count,
    )

    return {
        "recent_conversations": recent_convs,
        "total_conversations": total_count,
        "last_contact": last_contact,
    }


# ---------------------------------------------------------------------------
# persist_session_to_db
# ---------------------------------------------------------------------------


async def persist_session_to_db(
    db: AsyncSession,
    session_id: str,
    user_id: int,
    messages: list[BaseMessage],
    intent: str | None = None,
    status: ConversationStatus = ConversationStatus.archived,
) -> Conversation:
    """Flush an active Redis session into PostgreSQL.

    Creates (or retrieves) the :class:`Conversation` row for *session_id*,
    bulk-inserts all *messages* that are not yet stored, then marks the
    conversation as *archived* (or the supplied *status*).

    After a successful DB commit the Redis keys for this session are deleted.

    Args:
        db:         Async SQLAlchemy session (caller commits the transaction).
        session_id: The session identifier from ``state["session_id"]``.
        user_id:    Authenticated user ID.
        messages:   Full ordered message list from the Redis session.
        intent:     Primary intent for analytics (optional).
        status:     Destination status — defaults to ``archived``.

    Returns:
        The upserted :class:`Conversation` ORM object.

    Raises:
        sqlalchemy.exc.SQLAlchemyError: On any database error.  The caller
            should catch and log; do NOT surface raw DB errors to the user.
    """
    log = logger.bind(session_id=session_id, user_id=user_id)

    # -----------------------------------------------------------------------
    # 1. Upsert the Conversation row
    # -----------------------------------------------------------------------
    conv_stmt = select(Conversation).where(Conversation.session_id == session_id)
    conv_result = await db.execute(conv_stmt)
    conversation: Conversation | None = conv_result.scalar_one_or_none()

    if conversation is None:
        conversation = Conversation(
            session_id=session_id,
            user_id=user_id,
            status=status,
            primary_intent=intent,
            turn_count=len([m for m in messages if m.type == "human"]),
            ended_at=datetime.now(tz=timezone.utc),
        )
        db.add(conversation)
        await db.flush()  # populate conversation.id before inserting messages
        log.info("long_term.conversation_created", conversation_id=conversation.id)
    else:
        conversation.status = status
        conversation.ended_at = datetime.now(tz=timezone.utc)
        if intent:
            conversation.primary_intent = intent
        conversation.turn_count = len([m for m in messages if m.type == "human"])
        log.info("long_term.conversation_updated", conversation_id=conversation.id)

    # -----------------------------------------------------------------------
    # 2. Determine which messages are already stored
    # -----------------------------------------------------------------------
    existing_stmt = (
        select(Message.turn_index)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.turn_index)
    )
    existing_result = await db.execute(existing_stmt)
    stored_indices: set[int] = {row[0] for row in existing_result.all()}

    # -----------------------------------------------------------------------
    # 3. Bulk-insert new messages
    # -----------------------------------------------------------------------
    new_messages: list[Message] = []
    for turn_index, msg in enumerate(messages):
        if turn_index in stored_indices:
            continue

        role = _langchain_role_to_enum(msg.type)
        content = _serialise_message_content(msg)

        new_messages.append(
            Message(
                conversation_id=conversation.id,
                role=role,
                content=content,
                turn_index=turn_index,
            )
        )

    if new_messages:
        db.add_all(new_messages)
        log.info("long_term.messages_inserted", count=len(new_messages))

    # -----------------------------------------------------------------------
    # 4. Commit and clean up Redis
    # -----------------------------------------------------------------------
    await db.commit()
    await db.refresh(conversation)

    # Remove Redis keys after a successful DB flush
    await delete_session(session_id)
    log.info("long_term.session_persisted", conversation_id=conversation.id)

    return conversation


# ---------------------------------------------------------------------------
# get_or_create_conversation
# ---------------------------------------------------------------------------


async def get_or_create_conversation(
    db: AsyncSession,
    session_id: str,
    user_id: int,
) -> Conversation:
    """Return the existing :class:`Conversation` for *session_id*, or create one.

    Useful for mid-session writes (e.g. saving a summary) without performing
    a full session flush.

    Args:
        db:         Async SQLAlchemy session.
        session_id: Session identifier.
        user_id:    Authenticated user ID.

    Returns:
        The existing or newly-created :class:`Conversation` ORM object.
    """
    stmt = select(Conversation).where(Conversation.session_id == session_id)
    result = await db.execute(stmt)
    conversation: Conversation | None = result.scalar_one_or_none()

    if conversation is None:
        conversation = Conversation(
            session_id=session_id,
            user_id=user_id,
            status=ConversationStatus.active,
        )
        db.add(conversation)
        await db.flush()

    return conversation


# ---------------------------------------------------------------------------
# save_summary_to_db
# ---------------------------------------------------------------------------


async def save_summary_to_db(
    db: AsyncSession,
    session_id: str,
    user_id: int,
    summary_text: str,
    covered_up_to_turn: int,
    messages_token_count: int | None = None,
    summary_token_count: int | None = None,
) -> ConversationSummary:
    """Persist a rolling summary produced by the summarizer node.

    Args:
        db:                   Async SQLAlchemy session.
        session_id:           Session identifier.
        user_id:              Authenticated user ID.
        summary_text:         Plain-text summary from Claude Haiku.
        covered_up_to_turn:   Highest turn_index included in the summary.
        messages_token_count: Approx tokens of summarised messages.
        summary_token_count:  Tokens in the summary itself.

    Returns:
        The newly created :class:`ConversationSummary` row.
    """
    conversation = await get_or_create_conversation(db, session_id, user_id)

    summary = ConversationSummary(
        conversation_id=conversation.id,
        summary_text=summary_text,
        covered_up_to_turn=covered_up_to_turn,
        messages_token_count=messages_token_count,
        summary_token_count=summary_token_count,
    )
    db.add(summary)
    await db.commit()
    await db.refresh(summary)

    logger.info(
        "long_term.summary_saved",
        session_id=session_id,
        summary_id=summary.id,
        covered_up_to_turn=covered_up_to_turn,
    )
    return summary


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _langchain_role_to_enum(msg_type: str) -> MessageRole:
    """Map a LangChain message type string to :class:`MessageRole`."""
    mapping: dict[str, MessageRole] = {
        "human": MessageRole.human,
        "ai": MessageRole.ai,
        "tool": MessageRole.tool,
        "system": MessageRole.system,
        "chat": MessageRole.ai,           # older alias used by some LangChain versions
        "function": MessageRole.tool,     # function_call alias
    }
    return mapping.get(msg_type, MessageRole.ai)


def _serialise_message_content(msg: BaseMessage) -> str:
    """Serialise message content to a plain string for DB storage.

    - ``str`` content is stored as-is.
    - ``list`` content (multimodal) is JSON-encoded to preserve structure.
    - Tool messages are stored as JSON with ``tool_name`` and ``tool_result``.
    """
    content = msg.content

    if isinstance(content, str):
        return content

    # Multimodal or structured content
    try:
        return json.dumps(messages_to_dict([msg])[0], default=str)
    except (TypeError, ValueError):
        return str(content)
