import structlog
from langgraph.graph import END

from app.agent.state import AgentState


logger = structlog.get_logger(__name__)


NODE_GUARDRAILS_IN: str = "guardrails_in"
NODE_CLASSIFIER: str = "classifier"
NODE_TOOL_PLANNER: str = "tool_planner"
NODE_TOOL_EXECUTOR: str = "tool_executor"
NODE_RESPONSE_GENERATOR: str = "response_generator"
NODE_GUARDRAILS_OUT: str = "guardrails_out"
NODE_HUMAN_HANDOFF: str = "human_handoff"

# Maximum number of times the tool_planner->tool_executor loop may retry after
# a tool error within a single user turn.  Matches the docstring on
# AgentState.retry_count.  Set to 2 so a transient DB failure gets one
# genuine retry before the response_generator handles it gracefully.
MAX_TOOL_RETRIES: int = 2


# Maximum number of times the response_generator may be asked to rewrite its
# output after guardrails_out detects a violation (hallucination, PII leak).
# After this many rewrites the graph falls through to END with a safe fallback
# message already placed by response_generator's error handling.
MAX_OUTPUT_RETRIES: int = 2


def route_after_guardrails_in(state: AgentState) -> str:
    """Decide whether to proceed to the classifier or terminate immediately.

    Two termination conditions are checked:

    1. **Input blocked** (``input_safe=False``): the guardrail detected a
       prompt-injection attempt, PII, or rate-limit exceeded.  Terminate with
       END — the guardrail node is responsible for appending a rejection
       AIMessage before returning, so the caller always receives a response.

    2. **Turn limit reached** (``turn_count >= max_turns``): the conversation
       has hit the hard safety cap.  Terminate to prevent unbounded loops.
       The chat endpoint should surface this to the user (e.g. "session limit
       reached — start a new conversation").

    Args:
        state: Current AgentState.

    Returns:
        ``NODE_CLASSIFIER`` when safe to proceed, ``END`` otherwise.
    """
    log = logger.bind(
        user_id=state.get("user_id"),
        session_id=state.get("session_id"),
    )

    if not state["input_safe"]:
        log.info(
            "edge.guardrails_in->END",
            reason="input_blocked",
            violation=state.get("guardrail_violation"),
        )
        return END  # type: ignore[return-value]

    if state["turn_count"] >= state["max_turns"]:
        log.warning(
            "edge.guardrails_in->END",
            reason="turn_limit_reached",
            turn_count=state["turn_count"],
            max_turns=state["max_turns"],
        )
        return END  # type: ignore[return-value]

    log.debug("edge.guardrails_in->classifier")
    return NODE_CLASSIFIER


def route_after_classifier(state: AgentState) -> str:
    """Route based on the intent and flags set by the classifier node.

    Priority order (highest to lowest):
    1. ``needs_escalation=True`` -> human_handoff regardless of intent.
    2. ``requires_tool=True``    -> tool_planner to fetch live DB data.
    3. Everything else          -> response_generator for direct synthesis.

    Args:
        state: Current AgentState with ``intent``, ``requires_tool``, and
               ``needs_escalation`` set by the classifier node.

    Returns:
        Name of the next node to execute.
    """
    log = logger.bind(
        user_id=state.get("user_id"),
        session_id=state.get("session_id"),
        intent=state.get("intent"),
        confidence=state.get("confidence"),
    )

    if state["needs_escalation"]:
        log.info(
            "edge.classifier->human_handoff",
            intent=state["intent"],
        )
        return NODE_HUMAN_HANDOFF

    if state["requires_tool"]:
        log.info(
            "edge.classifier->tool_planner",
            intent=state["intent"],
        )
        return NODE_TOOL_PLANNER

    # chitchat / faq_policy / unknown -> direct conversational response
    log.info(
        "edge.classifier->response_generator",
        intent=state["intent"],
        reason="direct_response",
    )
    return NODE_RESPONSE_GENERATOR


def route_after_tool_executor(state: AgentState) -> str:
    """Route to a retry, or to response_generator when the tool loop is done.

    Two paths:

    * **Retry** — ``tool_error`` is set AND ``retry_count`` is below the cap.
      Routes back to ``tool_planner`` so the LLM can try a different approach
      (different args, different tool, or a clarifying response).

    * **Proceed** — success (``tool_error`` is None) OR retries exhausted.
      Routes to ``response_generator``, which handles both the "here is the
      data" case and the "I couldn't retrieve the data" case gracefully.

    Args:
        state: Current AgentState.  Relevant fields: ``tool_error``,
               ``retry_count``.

    Returns:
        ``NODE_TOOL_PLANNER`` for retry, ``NODE_RESPONSE_GENERATOR`` otherwise.
    """
    log = logger.bind(
        user_id=state.get("user_id"),
        session_id=state.get("session_id"),
        intent=state.get("intent"),
        selected_tool=state.get("selected_tool"),
        retry_count=state.get("retry_count", 0),
    )

    tool_error = state.get("tool_error")
    retry_count: int = state.get("retry_count", 0)

    if tool_error is not None:
        if retry_count < MAX_TOOL_RETRIES:
            log.info(
                "edge.tool_executor->tool_planner",
                reason="retry",
                retry_count=retry_count,
                max_retries=MAX_TOOL_RETRIES,
                error_preview=str(tool_error)[:120],
            )
            return NODE_TOOL_PLANNER

        # Retries exhausted — response_generator will acknowledge the failure
        log.warning(
            "edge.tool_executor->response_generator",
            reason="retries_exhausted",
            retry_count=retry_count,
            error_preview=str(tool_error)[:120],
        )
        return NODE_RESPONSE_GENERATOR

    log.info(
        "edge.tool_executor->response_generator",
        reason="tool_success",
    )
    return NODE_RESPONSE_GENERATOR


def route_after_guardrails_out(state: AgentState) -> str:
    """Route to END when the response is safe, or trigger a rewrite loop.

    When ``output_safe=True`` the response passed all checks — terminate.

    When ``output_safe=False`` a violation was detected (hallucinated data,
    PII leak, system-prompt exposure).  The rewrite loop routes back to
    ``response_generator`` with the violation recorded in
    ``state["guardrail_violation"]`` so the LLM can try again.

    Rewrite attempts are tracked via ``state["retry_count"]``.  After
    ``MAX_OUTPUT_RETRIES`` rewrites the loop terminates unconditionally — the
    response_generator's safe fallback message is already in state["messages"]
    so the caller always receives something sensible.

    Note: ``retry_count`` is shared with the tool-retry loop.  By the time
    ``guardrails_out`` is reached the tool loop is complete, so reusing the
    counter is safe within a single turn.  A dedicated ``output_retry_count``
    field can replace this if the two loops ever need to coexist.

    Args:
        state: Current AgentState.  Relevant fields: ``output_safe``,
               ``retry_count``, ``guardrail_violation``.

    Returns:
        ``END`` when safe or retries exhausted, ``NODE_RESPONSE_GENERATOR``
        to trigger a rewrite.
    """
    log = logger.bind(
        user_id=state.get("user_id"),
        session_id=state.get("session_id"),
        intent=state.get("intent"),
        retry_count=state.get("retry_count", 0),
    )

    if state["output_safe"]:
        log.info("edge.guardrails_out->END", reason="output_safe")
        return END  # type: ignore[return-value]

    # Output guardrail failed — attempt a rewrite if budget allows
    retry_count: int = state.get("retry_count", 0)

    if retry_count < MAX_OUTPUT_RETRIES:
        log.warning(
            "edge.guardrails_out->response_generator",
            reason="rewrite",
            retry_count=retry_count,
            max_retries=MAX_OUTPUT_RETRIES,
            violation=state.get("guardrail_violation"),
        )
        return NODE_RESPONSE_GENERATOR

    # Rewrite budget exhausted — terminate; safe fallback is already in messages
    log.error(
        "edge.guardrails_out->END",
        reason="rewrite_budget_exhausted",
        retry_count=retry_count,
        violation=state.get("guardrail_violation"),
    )
    return END  # type: ignore[return-value]
