from __future__ import annotations

import json
import re

import structlog
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage
from pydantic import BaseModel, Field

from app.agent.state import AgentState
from app.config import get_settings
from app.guardrails.pii_patterns import PIIType, detect_and_redact

logger = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# PII types that must NEVER appear in agent responses
# ---------------------------------------------------------------------------
# Emails and phone numbers are allowed — support agents legitimately include them.
# Credit cards, SSNs, and API keys are always a violation in outbound responses.
_RESPONSE_FORBIDDEN_PII: frozenset[PIIType] = frozenset(
    {PIIType.CREDIT_CARD, PIIType.SSN, PIIType.API_KEY}
)

# ---------------------------------------------------------------------------
# SQL / system leak patterns
# ---------------------------------------------------------------------------

# SQL DML/DDL that would indicate the LLM echoed a database query
_SQL_LEAK_PATTERNS: list[re.Pattern[str]] = [
    re.compile(
        r"\b(SELECT|INSERT|UPDATE|DELETE|DROP|TRUNCATE|ALTER)\b.{0,120}\b(FROM|TABLE|INTO|SET)\b",
        re.IGNORECASE | re.DOTALL,
    ),
    re.compile(r"\bUNION\s+(ALL\s+)?SELECT\b", re.IGNORECASE),
    re.compile(r";\s*(DROP|DELETE|TRUNCATE)\s+", re.IGNORECASE),
]

# Internal database / model field names that should never surface to users
_INTERNAL_FIELD_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\b(password_hash|hashed_password|bcrypt|salt)\b", re.IGNORECASE),
    re.compile(
        r"\b(internal_notes?|admin_flag|is_flagged|risk_score|fraud_score)\b",
        re.IGNORECASE,
    ),
    re.compile(r"\b(secret_key|signing_key|jwt_secret|private_key)\b", re.IGNORECASE),
]

# Hard artefacts that can only appear if the system prompt or internal code was
# echoed verbatim (LangGraph class names, guardrail variable names, etc.)
_SYSTEM_LEAK_PATTERNS: list[re.Pattern[str]] = [
    re.compile(
        r"\b(AgentState|StateGraph|guardrail_violation|tool_call_counts)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(HARD\s+pattern|SOFT\s+pattern|injection_confidence|pii_patterns)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(LangGraph|langgraph|langchain_anthropic|MultiServerMCPClient)\b",
        re.IGNORECASE,
    ),
]

# ---------------------------------------------------------------------------
# Grounding extraction patterns
# ---------------------------------------------------------------------------
# These extract "factual claims" from the AI response that must trace back to
# tool_result.  Only numeric identifiers and amounts are checked — general prose
# is not verifiable and must not trigger false positives.

# Order IDs mentioned as "#12345", "order 12345", "order number 12345", etc.
_ORDER_ID_PATTERN: re.Pattern[str] = re.compile(
    r"(?:#|order\s+(?:number|num|id|#)?\s*)(\d{4,10})\b",
    re.IGNORECASE,
)

# Dollar amounts: "$99.99", "$ 1,234.56", "$0.00"
_DOLLAR_AMOUNT_PATTERN: re.Pattern[str] = re.compile(
    r"\$\s*(\d[\d,]*(?:\.\d{1,2})?)\b"
)

# Standard carrier tracking number formats
# USPS: 2 letters + 9 digits + 2 letters  (e.g. EA123456789US)
# UPS:  1Z + 16 alphanumeric chars
# FedEx: 12 or 15 digits
_TRACKING_NUMBER_PATTERN: re.Pattern[str] = re.compile(
    r"\b(?:[A-Z]{2}\d{9}[A-Z]{2}|1Z[A-Z0-9]{16}|\d{15}|\d{12})\b"
)

# ---------------------------------------------------------------------------
# Grounding LLM schema + system prompt
# ---------------------------------------------------------------------------


class GroundingCheckResult(BaseModel):
    """Structured output from the Claude Haiku grounding classifier."""

    is_grounded: bool = Field(
        description=(
            "True if every factual claim in the AI response (order IDs, prices, "
            "tracking numbers, dates, amounts) is directly supported by the "
            "provided tool output.  False if any claim appears to be fabricated "
            "or absent from the tool output."
        )
    )
    ungrounded_claims: list[str] = Field(
        default_factory=list,
        description=(
            "Specific claims in the response that could not be found in the tool "
            "output.  Empty list when is_grounded=True."
        ),
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence in the grounding assessment (0.0 – 1.0).",
    )


_GROUNDING_SYSTEM_PROMPT: str = (
    "You are a factual grounding checker for an ecommerce customer service AI.\n\n"
    "Task: given the structured tool output (JSON from the database) and the AI's "
    "response to a customer, determine whether every specific factual claim in the "
    "response is directly supported by the tool output.\n\n"
    "Factual claims that require grounding:\n"
    "  - Order IDs / reference numbers\n"
    "  - Prices and monetary amounts\n"
    "  - Tracking numbers\n"
    "  - Specific dates and times\n"
    "  - Product names, SKUs, quantities\n"
    "  - Refund amounts and statuses\n\n"
    "General statements ('I can help you', 'please allow 3-5 business days') "
    "do NOT require grounding.\n\n"
    "A response is GROUNDED when all specific values came from the tool output.\n"
    "A response is NOT GROUNDED when it contains values absent from the tool output "
    "(hallucinated IDs, invented amounts, fabricated tracking codes, etc.).\n\n"
    "Respond ONLY with the structured fields — no prose."
)

# ---------------------------------------------------------------------------
# Lazy-initialised LLM client (shared across requests)
# ---------------------------------------------------------------------------

_grounding_llm: ChatOpenAI | None = None


def _get_grounding_llm() -> ChatOpenAI:
    """Return the cached LLM grounding client, creating it on first call."""
    global _grounding_llm
    if _grounding_llm is None:
        settings = get_settings()
        base_llm = ChatOpenAI(
            model=settings.classifier_model,
            temperature=0,
            max_tokens=512,
        )
        _grounding_llm = base_llm.with_structured_output(GroundingCheckResult)  # type: ignore[assignment]
    return _grounding_llm


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _extract_response_text(state: AgentState) -> str | None:
    """Return the text content of the most recent AIMessage, or None.

    Handles both plain-string content and multimodal content lists
    (concatenates all text blocks).
    """
    for msg in reversed(state["messages"]):
        if isinstance(msg, AIMessage):
            content = msg.content
            if isinstance(content, str):
                return content.strip() or None
            if isinstance(content, list):
                parts = [
                    block["text"]
                    for block in content
                    if isinstance(block, dict) and block.get("type") == "text"
                ]
                combined = " ".join(parts).strip()
                return combined or None
    return None


def _check_pii_leak(text: str) -> str | None:
    """Return a violation label if the response contains forbidden PII, else None.

    Only credit cards, SSNs, and API keys are treated as violations.
    Email and phone are permitted in responses (support contact details).

    Args:
        text: AI response text to scan.

    Returns:
        Short violation string like ``"response_pii_leak: CREDIT_CARD"`` or None.
    """
    result = detect_and_redact(text)
    if not result.has_pii:
        return None
    forbidden = result.pii_types_found & _RESPONSE_FORBIDDEN_PII
    if forbidden:
        labels = ", ".join(sorted(t.value for t in forbidden))
        return f"response_pii_leak: {labels}"
    return None


def _check_sql_and_system_leak(text: str) -> tuple[str | None, str]:
    """Return ``(violation_label, check_name)`` if a leak pattern matched, else ``(None, "")``.

    Checks SQL DML/DDL, internal field names, and hard system-leak artefacts
    in that order (all regex, zero cost).

    Args:
        text: AI response text to scan.

    Returns:
        Tuple of ``(violation_label, check_name)`` where both are empty strings
        when the response is clean.
    """
    for pattern in _SQL_LEAK_PATTERNS:
        if pattern.search(text):
            return (
                f"sql_leak: matched pattern '{pattern.pattern[:60]}'",
                "sql_leak",
            )

    for pattern in _INTERNAL_FIELD_PATTERNS:
        if pattern.search(text):
            return (
                f"internal_field_leak: matched pattern '{pattern.pattern[:60]}'",
                "internal_field_leak",
            )

    for pattern in _SYSTEM_LEAK_PATTERNS:
        if pattern.search(text):
            return (
                f"system_prompt_leak: matched pattern '{pattern.pattern[:60]}'",
                "system_prompt_leak",
            )

    return None, ""


def _extract_factual_claims(text: str) -> dict[str, list[str]]:
    """Extract verifiable numeric values from the response text.

    Returns a mapping of claim category → list of extracted string values.
    Only categories with at least one match are included.

    Args:
        text: AI response text to scan.
    """
    claims: dict[str, list[str]] = {}

    order_ids = [m.group(1) for m in _ORDER_ID_PATTERN.finditer(text)]
    if order_ids:
        claims["order_ids"] = order_ids

    amounts = [
        m.group(1).replace(",", "")
        for m in _DOLLAR_AMOUNT_PATTERN.finditer(text)
    ]
    if amounts:
        claims["amounts"] = amounts

    tracking_ids = [m.group() for m in _TRACKING_NUMBER_PATTERN.finditer(text)]
    if tracking_ids:
        claims["tracking_ids"] = tracking_ids

    return claims


def _fast_grounding_check(
    text: str,
    tool_result: dict,
) -> tuple[bool, list[str]]:
    """Check grounding via simple string containment (no LLM cost).

    Serialises ``tool_result`` to a lowercase JSON string and checks whether
    each extracted claim value appears anywhere in it.  Numeric separators
    (commas, spaces) are stripped before comparison so ``$1,234.56`` matches
    the ``1234.56`` in the JSON.

    Returns:
        ``(all_grounded, unverifiable)`` — when ``all_grounded`` is ``True``
        every extracted value was found.  ``unverifiable`` lists the values
        that could not be located (e.g. ``["order_ids:99999"]``).
    """
    tool_str = json.dumps(tool_result, default=str).lower()
    claims = _extract_factual_claims(text)

    if not claims:
        # No numeric claims in the response — nothing to verify
        return True, []

    unverifiable: list[str] = []
    for category, values in claims.items():
        for value in values:
            # Normalise: strip separators for comparison (handles "$1,234" vs "1234")
            normalised = re.sub(r"[,\s]", "", value.lower())
            if normalised not in tool_str:
                unverifiable.append(f"{category}:{value}")

    return len(unverifiable) == 0, unverifiable


async def _llm_grounding_check(
    response_text: str,
    tool_result: dict,
) -> GroundingCheckResult:
    """Call Claude Haiku to verify grounding of the response against tool_result.

    Only invoked when the fast path finds at least one unverifiable value.
    Fails open on transient API errors — availability issues should not block
    legitimate customers.

    Args:
        response_text: AI response to validate.
        tool_result:   Structured data returned by the tool call.

    Returns:
        :class:`GroundingCheckResult`.  On error, returns ``is_grounded=True``
        so the response passes and the customer is not blocked.
    """
    try:
        tool_result_str = json.dumps(tool_result, default=str, indent=2)
        # Truncate oversized tool results to avoid context overflow
        if len(tool_result_str) > 3000:
            tool_result_str = tool_result_str[:3000] + "\n... (truncated)"

        llm = _get_grounding_llm()
        result: GroundingCheckResult = await llm.ainvoke(  # type: ignore[assignment]
            [
                {"role": "system", "content": _GROUNDING_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"Tool output:\n```json\n{tool_result_str}\n```\n\n"
                        f"AI response:\n{response_text}"
                    ),
                },
            ]
        )
        return result

    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "guardrails_out.grounding_llm_error",
            error=str(exc),
            error_type=type(exc).__name__,
        )
        # Fail open — transient API error is not a grounding signal
        return GroundingCheckResult(is_grounded=True, ungrounded_claims=[], confidence=0.0)


# ---------------------------------------------------------------------------
# LangGraph node
# ---------------------------------------------------------------------------


async def guardrails_out_node(state: AgentState) -> dict:
    """Output guardrail node — validate the AI response before it reaches the user.

    Runs after ``response_generator`` and before graph termination.  Checks
    for PII leakage, SQL/system leakage, and hallucination against tool output.

    When a violation is found, increments ``retry_count`` so
    ``route_after_guardrails_out`` can cap rewrites at ``MAX_OUTPUT_RETRIES``.

    The node never raises — all failures return a partial state dict with
    ``output_safe=False`` and a machine-readable ``guardrail_violation`` label.
    ``response_generator`` uses this label on the next pass to avoid the same
    mistake.

    Args:
        state: Full AgentState after response_generator has appended its AIMessage.

    Returns:
        Partial AgentState dict — see module docstring for exact shape.
    """
    user_id: int = state.get("user_id", 0)
    session_id: str = state.get("session_id", "")
    tool_result: dict | None = state.get("tool_result")
    retry_count: int = state.get("retry_count", 0)

    log = logger.bind(
        user_id=user_id,
        session_id=session_id,
        retry_count=retry_count,
        intent=state.get("intent"),
    )
    log.info("guardrails_out.started")

    # ------------------------------------------------------------------
    # Extract the AI response to check
    # ------------------------------------------------------------------
    response_text = _extract_response_text(state)

    if not response_text:
        log.warning("guardrails_out.no_ai_message")
        # Nothing to guard — pass through
        return {"output_safe": True, "guardrail_violation": None}

    log.debug("guardrails_out.response_preview", preview=response_text[:100])

    # ------------------------------------------------------------------
    # Check 1: PII leak
    # ------------------------------------------------------------------
    pii_violation = _check_pii_leak(response_text)
    if pii_violation:
        log.warning(
            "guardrails_out.blocked",
            reason=pii_violation,
            check="pii_leak",
        )
        return {
            "output_safe": False,
            "guardrail_violation": pii_violation,
            "retry_count": retry_count + 1,
        }

    # ------------------------------------------------------------------
    # Check 2: SQL / system leak
    # ------------------------------------------------------------------
    system_violation, check_name = _check_sql_and_system_leak(response_text)
    if system_violation:
        log.warning(
            "guardrails_out.blocked",
            reason=system_violation,
            check=check_name,
        )
        return {
            "output_safe": False,
            "guardrail_violation": system_violation,
            "retry_count": retry_count + 1,
        }

    # ------------------------------------------------------------------
    # Check 3: Grounding (only when tool_result exists)
    # ------------------------------------------------------------------
    if tool_result is not None:
        is_grounded, unverifiable = _fast_grounding_check(response_text, tool_result)

        if not is_grounded:
            log.info(
                "guardrails_out.grounding_fast_miss",
                unverifiable_count=len(unverifiable),
                samples=unverifiable[:3],
            )
            # Escalate to LLM for final determination
            grounding_result = await _llm_grounding_check(response_text, tool_result)

            log.debug(
                "guardrails_out.grounding_llm_result",
                is_grounded=grounding_result.is_grounded,
                confidence=grounding_result.confidence,
                ungrounded=grounding_result.ungrounded_claims[:3],
            )

            settings = get_settings()
            if (
                not grounding_result.is_grounded
                and grounding_result.confidence >= settings.guardrail_injection_confidence_threshold
            ):
                # Reuse the same confidence threshold setting (0.7 by default)
                violation = (
                    "response_not_grounded: "
                    + ", ".join(grounding_result.ungrounded_claims[:3])
                )
                log.warning(
                    "guardrails_out.blocked",
                    reason=violation,
                    check="grounding",
                    confidence=grounding_result.confidence,
                )
                return {
                    "output_safe": False,
                    "guardrail_violation": violation,
                    "retry_count": retry_count + 1,
                }
        else:
            log.debug("guardrails_out.grounding_fast_passed")

    # ------------------------------------------------------------------
    # All checks passed
    # ------------------------------------------------------------------
    log.info(
        "guardrails_out.passed",
        had_tool_result=tool_result is not None,
        retry_count=retry_count,
    )
    return {
        "output_safe": True,
        "guardrail_violation": None,
    }
