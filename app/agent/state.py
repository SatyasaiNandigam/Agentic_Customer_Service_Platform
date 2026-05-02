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

CustomerDomain = Literal[
    "need_information",
    "need_assistance",
    "need_advice",
    "escalate",
    "block",
]

# Domain-bounded intent sets — used by classifier to load only the relevant
# intent context after the delegator has determined the customer domain.
INFORMATION_INTENTS: frozenset[IntentType] = frozenset({
    "order_status",
    "shipment_tracking",
    "refund_status",
    "account_info",
    "review_lookup",
    "product_inquiry",
    "product_search",
})

ASSISTANCE_INTENTS: frozenset[IntentType] = frozenset({
    "order_cancel",
    "refund_request",
})

ADVICE_INTENTS: frozenset[IntentType] = frozenset({
    "faq_policy",
    "chitchat",
    "unknown",
})

DOMAIN_INTENT_MAP: dict[str, frozenset[IntentType]] = {
    "need_information": INFORMATION_INTENTS,
    "need_assistance": ASSISTANCE_INTENTS,
    "need_advice": ADVICE_INTENTS,
}

# Kept for backward compatibility with edges/guardrails that still reference them.
TOOL_INTENTS: frozenset[IntentType] = INFORMATION_INTENTS | ASSISTANCE_INTENTS

DIRECT_RESPONSE_INTENTS: frozenset[IntentType] = ADVICE_INTENTS

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
    
    customer_domain: CustomerDomain

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

    retry_count: int
    
    context_summary: str | None

    customer_history: dict | None
    
    
def create_initial_state(
    *,
    user_id: str,
    session_id: str,
    user_role: Role = "customer",
) -> AgentState:
    """Return a fully-initialised AgentState for a new graph invocation."""
    return AgentState(
        # Core
        messages=[],
        user_id=user_id,
        session_id=session_id,
        user_role=user_role,
        # Classification
        customer_domain="need_advice",
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
        retry_count=0,
        # Memory
        context_summary=None,
        customer_history=None,
    )
