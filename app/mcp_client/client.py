from __future__ import annotations

import structlog
from contextlib import asynccontextmanager
from typing import AsyncIterator

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.tools import BaseTool

from app.config import get_settings

logger = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def build_mcp_client_config(user_id: str, user_role: str) -> dict:
    """Return the server-config dict accepted by ``MultiServerMCPClient``.

    Separating the config from the client construction makes it easy to
    override the URL in tests (e.g. point at a local dev server).

    Args:
        user_id:   Authenticated user's primary key (from JWT — never from LLM).
        user_role: One of ``"customer"``, ``"support_agent"``, ``"admin"``.

    Returns:
        Dict keyed by server name, suitable for ``MultiServerMCPClient(config)``.
    """
    settings = get_settings()
    return {
        "ecommerce-tools": {
            "url": settings.mcp_tools_url,
            "transport": "sse",
            "headers": {
                # The MCP server reads identity exclusively from these headers.
                # They are set here from the verified JWT — not from LLM output.
                "X-User-Id": str(user_id),
                "X-User-Role": user_role,
            },
            # Surface-level timeout; langchain-mcp-adapters passes this to
            # the underlying httpx SSE client.
            "timeout": settings.mcp_tools_timeout,
        }
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

@asynccontextmanager
async def mcp_client_for_user(
    user_id: str,
    user_role: str,
) -> AsyncIterator[MultiServerMCPClient]:
    """Async context manager: open SSE connection → yield client → close.

    Opens a fresh ``MultiServerMCPClient`` scoped to *one* authenticated user.
    The SSE connection is torn down on exit regardless of success or failure.

    Args:
        user_id:   Authenticated user PK from the verified JWT.
        user_role: ``"customer"`` | ``"support_agent"`` | ``"admin"``.

    Yields:
        A connected ``MultiServerMCPClient`` ready for ``get_tools()`` calls.

    Raises:
        RuntimeError: If the MCP tools service is unreachable on startup.
    """
    config = build_mcp_client_config(user_id=user_id, user_role=user_role)
    log = logger.bind(user_id=user_id, user_role=user_role)

    log.debug("mcp_client.connecting", url=get_settings().mcp_tools_url)
    try:
        client = MultiServerMCPClient(config)
        log.debug("mcp_client.connected")
        yield client
    except Exception as exc:
        log.error(
            "mcp_client.connection_error",
            error=str(exc),
            url=get_settings().mcp_tools_url,
        )
        raise RuntimeError(
            f"Failed to connect to MCP tools service at "
            f"{get_settings().mcp_tools_url}: {exc}"
        ) from exc
    finally:
        log.debug("mcp_client.disconnected")


async def get_tools_for_user(
    user_id: str,
    user_role: str,
) -> list[BaseTool]:
    """Fetch the live tool list from the MCP server for this user.

    Opens a short-lived connection, retrieves all available tools as
    LangChain ``BaseTool`` objects, then closes.  The returned tools are
    safe to pass directly to ``llm.bind_tools(tools)``.

    Args:
        user_id:   Authenticated user PK.
        user_role: Role string — controls which tools the MCP server exposes.

    Returns:
        List of LangChain-compatible tool objects with names, descriptions,
        and input schemas populated from the MCP server's tool registry.
    """
    async with mcp_client_for_user(user_id=user_id, user_role=user_role) as client:
        tools: list[BaseTool] = await client.get_tools()
        logger.debug(
            "mcp_client.tools_fetched",
            user_id=user_id,
            count=len(tools),
            tool_names=[t.name for t in tools],
        )
        return tools
