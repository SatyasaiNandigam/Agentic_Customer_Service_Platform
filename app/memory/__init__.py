"""Memory package — short-term (Redis) and long-term (PostgreSQL) conversation storage."""

from app.memory.long_term import (
    load_customer_history,
    persist_session_to_db,
)
from app.memory.short_term import (
    append_message,
    get_session_messages,
    load_session_context,
    save_session_context,
)
from app.memory.summarizer import maybe_summarize

__all__ = [
    # Short-term (Redis)
    "get_session_messages",
    "append_message",
    "load_session_context",
    "save_session_context",
    # Long-term (PostgreSQL)
    "load_customer_history",
    "persist_session_to_db",
    # Summarizer
    "maybe_summarize",
]
