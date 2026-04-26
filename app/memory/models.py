"""Agent-only ORM models — conversations, messages, and rolling summaries.

These tables are owned entirely by the agent service.  The ecommerce business
tables (orders, products, users, etc.) live in ``tools_mcp/db/models.py`` and
are never imported here.

Schema design:
- ``conversations``          — one row per session; links a session to a user.
- ``messages``               — individual turns within a conversation.
- ``conversation_summaries`` — rolling summaries written by the summarizer node
                               when the active context window grows too large.

All timestamps are stored as ``DateTime(timezone=True)`` so the DB always
holds UTC values regardless of the server locale.

Usage::

    from app.memory.models import Base, Conversation, Message, ConversationSummary
    # Then use with the shared async engine from app.db.session
"""

from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Text,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


# ---------------------------------------------------------------------------
# Declarative base (agent-only; separate from tools_mcp models)
# ---------------------------------------------------------------------------


class Base(DeclarativeBase):
    """Shared base for all agent-side ORM models."""


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class MessageRole(str, enum.Enum):
    """Sender role of a stored conversation message."""

    human = "human"
    ai = "ai"
    tool = "tool"
    system = "system"


class ConversationStatus(str, enum.Enum):
    """Lifecycle state of a conversation session."""

    active = "active"       # session currently in Redis hot storage
    archived = "archived"   # flushed to PostgreSQL; Redis TTL has expired
    escalated = "escalated" # handed off to a live support agent


# ---------------------------------------------------------------------------
# Conversation
# ---------------------------------------------------------------------------


class Conversation(Base):
    """One row per customer chat session.

    A session maps a ``session_id`` (Redis key prefix) to a ``user_id`` (from
    the JWT) and tracks the conversation lifecycle.

    Relationships:
        messages  (one-to-many → Message)
        summaries (one-to-many → ConversationSummary)
    """

    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(Text, nullable=False, unique=True, index=True)
    """Redis session key prefix — matches ``state["session_id"]``."""

    user_id: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    """Authenticated user ID from the JWT (UUID string).  Indexed for per-user history queries."""

    status: Mapped[ConversationStatus] = mapped_column(
        Enum(ConversationStatus, name="conversation_status"),
        nullable=False,
        default=ConversationStatus.active,
        server_default="active",
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Denormalised intent of the final resolved turn — useful for analytics
    primary_intent: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Number of turns in this session (incremented by the graph on each turn)
    turn_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")

    # Relationships
    messages: Mapped[list[Message]] = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at",
        lazy="select",
    )
    summaries: Mapped[list[ConversationSummary]] = relationship(
        "ConversationSummary",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="ConversationSummary.created_at",
        lazy="select",
    )

    __table_args__ = (
        Index("ix_conversations_user_started", "user_id", "started_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<Conversation id={self.id} session={self.session_id!r} "
            f"user={self.user_id} status={self.status.value!r}>"
        )


# ---------------------------------------------------------------------------
# Message
# ---------------------------------------------------------------------------


class Message(Base):
    """Individual turn stored within a :class:`Conversation`.

    One row per message regardless of role (human / ai / tool / system).
    ``turn_index`` preserves the ordering within the session so messages can
    be reconstructed in the correct sequence after being flushed from Redis.

    The ``content`` column holds raw text for human/ai messages and a JSON
    string for tool messages (tool name + arguments + result).
    """

    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    conversation_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True
    )

    role: Mapped[MessageRole] = mapped_column(
        Enum(MessageRole, name="message_role"), nullable=False
    )

    content: Mapped[str] = mapped_column(Text, nullable=False)
    """Raw text content.  For tool messages this is a JSON-encoded dict
    containing ``tool_name``, ``tool_input``, and ``tool_result``."""

    turn_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Zero-based position of this message within the conversation turn sequence.",
    )

    # Token count — populated by the summarizer to track context budget usage
    token_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # Relationships
    conversation: Mapped[Conversation] = relationship("Conversation", back_populates="messages")

    __table_args__ = (
        Index("ix_messages_conv_turn", "conversation_id", "turn_index"),
    )

    def __repr__(self) -> str:
        return (
            f"<Message id={self.id} conv={self.conversation_id} "
            f"role={self.role.value!r} turn={self.turn_index}>"
        )


# ---------------------------------------------------------------------------
# ConversationSummary
# ---------------------------------------------------------------------------


class ConversationSummary(Base):
    """Rolling summary of a batch of messages within a conversation.

    Written by the summarizer node when the active Redis context exceeds the
    token budget.  The summarizer condenses the *older* half of messages into
    a single summary row, keeps the *recent* half verbatim, and stores the
    summary here for injection into future system prompts.

    ``covered_up_to_turn`` tracks which turn_index was the last to be covered
    by this summary, so the long-term loader can skip loading messages that
    are already summarised.
    """

    __tablename__ = "conversation_summaries"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    conversation_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True
    )

    summary_text: Mapped[str] = mapped_column(Text, nullable=False)
    """Plain-text summary produced by Claude Haiku for cost efficiency."""

    covered_up_to_turn: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="The highest turn_index included in this summary.",
    )

    # Token counts for budget tracking
    messages_token_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        doc="Approximate total tokens of the messages that were summarised.",
    )
    summary_token_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        doc="Token count of the summary itself.",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # Relationships
    conversation: Mapped[Conversation] = relationship(
        "Conversation", back_populates="summaries"
    )

    __table_args__ = (
        Index("ix_summaries_conv_turn", "conversation_id", "covered_up_to_turn"),
    )

    def __repr__(self) -> str:
        return (
            f"<ConversationSummary id={self.id} conv={self.conversation_id} "
            f"up_to_turn={self.covered_up_to_turn}>"
        )
