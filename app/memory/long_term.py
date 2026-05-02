"""Long-term memory — PostgreSQL persistence for conversation history.

``load_customer_history(db, user_id)``
    Called at graph entry to hydrate ``state["customer_history"]`` with a
    structured snapshot of the user's recent activity drawn from the agent's
    own conversation tables.  Returns the last 5 conversation summaries so
    the response_generator has context about prior sessions without loading
    the full message history.

Session and message persistence is handled automatically by the LangGraph
``AsyncPostgresSaver`` checkpointer.  The ``conversations`` / ``messages`` /
``conversation_summaries`` tables are available for analytics or manual
backfill but are not written to during normal agent operation.

Both functions accept an ``AsyncSession`` injected by the FastAPI dependency
(``get_db`` from ``app.dependencies``), never opening their own connections.
"""

from __future__ import annotations

import structlog
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.memory.models import (
    Conversation,
    ConversationStatus,
    ConversationSummary,
)

logger = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Number of past conversation summaries injected into the system prompt.
_HISTORY_SUMMARY_LIMIT = 5


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
