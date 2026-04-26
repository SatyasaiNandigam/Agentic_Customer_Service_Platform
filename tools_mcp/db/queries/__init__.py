"""Async query functions for the ecommerce domain.

Each sub-module exposes pure async functions that take an AsyncSession and return
plain JSON-serializable dicts.  ORM objects never escape these modules — callers
(MCP tool implementations) always receive dicts they can pass directly to
cache or return to the agent.
"""

import uuid
from datetime import datetime
from decimal import Decimal


def serialize(obj: object) -> object:
    """Recursively convert non-JSON-native types inside a dict / list."""
    if isinstance(obj, dict):
        return {k: serialize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [serialize(v) for v in obj]
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, uuid.UUID):
        return str(obj)
    return obj
