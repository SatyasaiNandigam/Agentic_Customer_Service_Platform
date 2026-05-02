"""Redis helpers — reserved for rate limiting and query caching.

Session message history and session listing are handled by the LangGraph
``AsyncPostgresSaver`` checkpointer.  This module will be extended with:

- Sliding-window rate limiting  (config: ``rate_limit_messages_per_minute``)
- Query-result caching          (``cache_aside`` pattern used by tools/)
"""
