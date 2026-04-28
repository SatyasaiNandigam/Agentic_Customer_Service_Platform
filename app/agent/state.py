from typing import Annotated, Literal, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

from app.auth.rbac import Role

IntentType = Literal[
    "order_status",
    "order_cancel",
    "shipment_tracking",
    "refund_request",
    "refund_status",
    "product_inquiry",
    "product_search",
    "account_info",
    "review_lookup",
    "faq_policy",
    "chitchat",
    "complaint",
    "unknown",
]

TOOL_INTENTS: frozenset[IntentType] = frozenset(
    {
        "order_status",
        "order_cancel",
        "shipment_tracking",
        "refund_request",
        "refund_status",
        "product_inquiry",
        "product_search",
        "account_info",
        "review_lookup",
    }
)


DIRECT_RESPONSE_INTENTS: frozenset[IntentType] = frozenset(
    {
        "chitchat",
        "faq_policy",
        "unknown",
    }
)

ESCALATION_INTENTS: frozenset[IntentType] = frozenset({"complaint"})


class AgentState(TypedDict):
    """Shared state passed between every node in the LangGraph StateGraph.

    Field groups:
        Core      — identity fields set once at graph entry, never mutated.
        Messages  — full conversation history; merged via add_messages reducer.
        Classification — output of the classifier node.
        Tool      — lifecycle of a single tool call (plan → execute → result).
        Guardrails — safety flags from input/output guard nodes.
        Control   — turn / retry counters that drive loop termination edges.
        Memory    — summarised history injected into the system prompt.
    """
    
    
    messages: Annotated[list[BaseMessage], add_messages]
    
    user_id: str

    session_id: str
    
    user_role: Role
    
    intent: IntentType
    
    confidence: float
    
    requires_tool: bool
    
    needs_escalation: bool
    
    selected_tool: str | None
    
    tool_input: dict | None
    
    tool_result: dict | None
    
    tool_error: str | None
    
    tool_call_counts: dict[str,int]
    
    input_safe: bool
    
    output_safe: bool
    
    guardrail_violation: str | None
    
    turn_count: int
    
    max_turns: int
    
    retry_count: int
    
    context_summary: str | None

    customer_history: dict | None
    
    
def create_initial_state(
    *,
    user_id: str,
    session_id: str,
    user_role: Role = "customer",
    max_turns: int = 5,
) -> AgentState:
    """Return a fully-initialised AgentState for a new graph invocation.

    All mutable fields are set to their safe defaults so nodes never have to
    handle missing keys — TypedDict doesn't enforce defaults at runtime, but
    callers that forget a field get a KeyError rather than a silent AttributeError.

    Args:
        user_id:    Authenticated user ID from the JWT (required).
        session_id: Redis session key prefix (required).
        user_role:  Role from JWT, defaults to "customer" (least privilege).
        max_turns:  Hard turn limit; defaults to settings value (5).

    Returns:
        Populated AgentState dict ready for ``graph.invoke(state)``.
    """
    return AgentState(
        # Core
        messages=[],
        user_id=user_id,
        session_id=session_id,
        user_role=user_role,
        # Classification
        intent="unknown",
        confidence=0.0,
        requires_tool=False,
        needs_escalation=False,
        # Tool execution
        selected_tool=None,
        tool_input=None,
        tool_result=None,
        tool_error=None,
        tool_call_counts={},
        # Guardrails
        input_safe=True,
        output_safe=True,
        guardrail_violation=None,
        # Control
        turn_count=0,
        max_turns=max_turns,
        retry_count=0,
        # Memory
        context_summary=None,
        customer_history=None,
    )
