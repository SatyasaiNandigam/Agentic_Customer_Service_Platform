"""Provider-agnostic token capture for eval runners.

Usage in a runner:
    from eval.callback_handler import capture_tokens, attach_token_capture

    llm = ChatOpenAI(...)
    attach_token_capture(llm)               # once at setup time

    with capture_tokens() as cb:
        output = await node(state)
    # cb.prompt_tokens, cb.completion_tokens available here

Works with any LangChain provider (OpenAI, Groq, Anthropic, etc.) because it
hooks into the generic on_llm_end callback rather than provider-specific APIs.
Safe for concurrent asyncio tasks — each task sees its own handler via ContextVar.
"""

from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult

_token_handler_var: ContextVar[TokenCaptureHandler | None] = ContextVar(
    "_token_handler", default=None
)


class TokenCaptureHandler(BaseCallbackHandler):
    """Accumulates prompt and completion tokens from any LangChain LLM provider."""

    def __init__(self) -> None:
        super().__init__()
        self.prompt_tokens: int = 0
        self.completion_tokens: int = 0

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        if not response.llm_output:
            return
        usage: dict = (
            response.llm_output.get("token_usage")  # OpenAI / Groq
            or response.llm_output.get("usage")      # Anthropic
            or {}
        )
        self.prompt_tokens += usage.get("prompt_tokens") or usage.get("input_tokens", 0)
        self.completion_tokens += usage.get("completion_tokens") or usage.get("output_tokens", 0)


class _ContextVarCallbackProxy(BaseCallbackHandler):
    """Registered once on the LLM instance; forwards on_llm_end to whichever
    TokenCaptureHandler is active in the current async task's context."""

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        handler = _token_handler_var.get()
        if handler is not None:
            handler.on_llm_end(response, **kwargs)


def attach_token_capture(llm: Any) -> None:
    """Add the ContextVar proxy to the LLM's callback list. Call once at setup."""
    existing = list(llm.callbacks or [])
    if not any(isinstance(cb, _ContextVarCallbackProxy) for cb in existing):
        llm.callbacks = existing + [_ContextVarCallbackProxy()]


@contextmanager
def capture_tokens():
    """Context manager that activates token capture for the current async task.

    Sets a ContextVar so the proxy on the LLM routes on_llm_end events to a
    fresh TokenCaptureHandler scoped to this context. Safe for concurrent tasks.
    """
    handler = TokenCaptureHandler()
    token = _token_handler_var.set(handler)
    try:
        yield handler
    finally:
        _token_handler_var.reset(token)
