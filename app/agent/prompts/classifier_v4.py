import json

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from app.agent.state import (
    ADVICE_INTENTS,
    ASSISTANCE_INTENTS,
    INFORMATION_INTENTS,
    INTENT_REGISTRY,
    CustomerDomain,
    IntentType,
)

# Static registry: each domain maps to its bounded intent set and few-shot examples.
# The prompt builder injects ONLY the relevant domain's data at call time so the
# classifier LLM never sees intents outside its current scope.

DOMAIN_INTENTS: dict[str, list[str]] = {
    "need_information": sorted(INFORMATION_INTENTS),
    "need_assistance": sorted(ASSISTANCE_INTENTS),
    "need_advice": sorted(ADVICE_INTENTS),
}

_DOMAIN_EXAMPLES: dict[str, list[tuple[str, dict]]] = {
    "need_information": [
        ("Where is my order #78432?", {"intent": "order_status", "confidence": 0.98}),
        ("It's been 6 days since I ordered — has it shipped?", {"intent": "order_status", "confidence": 0.95}),
        ("Track my package please.", {"intent": "shipment_tracking", "confidence": 0.97}),
        ("When will my delivery arrive?", {"intent": "shipment_tracking", "confidence": 0.96}),
        ("Has my refund been processed yet?", {"intent": "refund_status", "confidence": 0.97}),
        ("How long does a refund usually take?", {"intent": "refund_status", "confidence": 0.90}),
        ("What delivery address do you have on my account?", {"intent": "account_info", "confidence": 0.96}),
        ("Show me my account details.", {"intent": "account_info", "confidence": 0.95}),
        ("What are customers saying about the Kindle Paperwhite?", {"intent": "review_lookup", "confidence": 0.94}),
        ("Can I see reviews for that product?", {"intent": "review_lookup", "confidence": 0.91}),
        ("Does the Sony WH-1000XM5 support multipoint Bluetooth?", {"intent": "product_inquiry", "confidence": 0.95}),
        ("Tell me more about that laptop.", {"intent": "product_inquiry", "confidence": 0.92}),
        ("Do you have wireless headphones under $80?", {"intent": "product_search", "confidence": 0.96}),
        ("Find me a waterproof running jacket in size M.", {"intent": "product_search", "confidence": 0.95}),
    ],
    "need_assistance": [
        ("Please cancel my order. I placed it by mistake.", {"intent": "order_cancel", "confidence": 0.98}),
        ("Cancel order #12345 for me.", {"intent": "order_cancel", "confidence": 0.99}),
        ("I want to cancel — I ordered the wrong size.", {"intent": "order_cancel", "confidence": 0.97}),
        ("The shirt I received is the wrong colour. I want a refund.", {"intent": "refund_request", "confidence": 0.97}),
        ("I'd like to request a refund for my last order.", {"intent": "refund_request", "confidence": 0.98}),
        ("This item arrived broken — please process a refund.", {"intent": "refund_request", "confidence": 0.97}),
    ],
    "need_advice": [
        ("What is your return policy for electronics?", {"intent": "faq_policy", "confidence": 0.96}),
        ("How do I cancel an order?", {"intent": "faq_policy", "confidence": 0.95}),
        ("How do I get a refund for a damaged item?", {"intent": "faq_policy", "confidence": 0.95}),
        ("Do you offer free shipping?", {"intent": "faq_policy", "confidence": 0.94}),
        ("What payment methods do you accept?", {"intent": "faq_policy", "confidence": 0.95}),
        ("Hi! How are you?", {"intent": "chitchat", "confidence": 0.99}),
        ("Thank you, that's all I needed!", {"intent": "chitchat", "confidence": 0.98}),
        ("What can you help me with?", {"intent": "chitchat", "confidence": 0.96}),
        ("Sounds good.", {"intent": "unknown", "confidence": 0.70}),
        ("I'm not sure what I need.", {"intent": "unknown", "confidence": 0.72}),
    ],
}

_SYSTEM_TEMPLATE = """\
You are an intent classifier for an ecommerce customer service chatbot.

The customer has already been categorised as: **{domain_label}**

Your job: classify the customer's message into one of the following intents.
Output a single JSON object. No explanation, no markdown fences.

If a "## Recent conversation context" section is present:
1. Identify the specific topic the customer was discussing in the prior turn.
2. Use that topic to resolve any pronouns or references ("it", "that", "the same one")
   in the current message.
3. Classify based on what aspect of that topic the customer is now asking about — a
   follow-up asking about location, delivery progress, or dispatch is shipment_tracking
   even when the prior turn established a general order context.

## Valid intents for this domain
{intent_list}

## Rules
1. Only output one of the intents listed above — no other values are valid.
2. Set confidence honestly in [0.0, 1.0]. Use < 0.5 only when genuinely ambiguous.
3. When ambiguous, prefer the most specific intent over "unknown".

## Output format (JSON only, no other text)
{{"intent": "<intent>", "confidence": <0.0–1.0>}}
"""

_DOMAIN_LABELS: dict[str, str] = {
    "need_information": "needs information (data retrieval)",
    "need_assistance": "needs assistance (action required)",
    "need_advice": "needs advice (guidance or general chat)",
}


def _format_intent(name: str) -> str:
    defn = INTENT_REGISTRY.get(name)
    if defn and defn.context_signals:
        signals = "; ".join(defn.context_signals)
        return f"- {name}: {signals}"
    return f"- {name}"


def build_domain_classifier_messages(
    user_message: str,
    domain: CustomerDomain,
    history: list | None = None,
) -> list:
    """Build the message list for the domain-aware intent classifier LLM call.

    Injects only the intents and examples for the given domain so the LLM
    context stays small and focused — the bounded-context guarantee.

    Args:
        user_message: The raw customer message to classify.
        domain: The customer domain determined by the delegator node.
                Must be one of: need_information, need_assistance, need_advice.
        history: Optional list of recent BaseMessage objects (up to 4) for
                 resolving follow-up references.

    Returns:
        List of [SystemMessage, few-shot pairs, HumanMessage].
    """
    intents = DOMAIN_INTENTS[domain]
    examples = _DOMAIN_EXAMPLES[domain]
    domain_label = _DOMAIN_LABELS[domain]

    intent_list = "\n".join(_format_intent(i) for i in intents)
    system_content = _SYSTEM_TEMPLATE.format(
        domain_label=domain_label,
        intent_list=intent_list,
    )

    if history:
        lines = ["\n## Recent conversation context"]
        for msg in history:
            role = "Customer" if isinstance(msg, HumanMessage) else "Assistant"
            content = msg.content if isinstance(msg.content, str) else str(msg.content)
            lines.append(f"{role}: {content[:300]}")
        system_content += "\n".join(lines)

    messages: list = [SystemMessage(content=system_content)]

    for customer_text, expected_output in examples:
        messages.append(HumanMessage(content=customer_text))
        messages.append(AIMessage(content=json.dumps(expected_output)))

    messages.append(HumanMessage(content=user_message))
    return messages
