import structlog
from langchain_core.messages import AIMessage
from langgraph.graph import END, START, StateGraph

from app.agent.edges import (
    MAX_OUTPUT_RETRIES,
    MAX_TOOL_RETRIES,
    NODE_CLASSIFIER,
    NODE_GUARDRAILS_IN,
    NODE_GUARDRAILS_OUT,
    NODE_HUMAN_HANDOFF,
    NODE_RESPONSE_GENERATOR,
    NODE_TOOL_EXECUTOR,
    NODE_TOOL_PLANNER,
    route_after_classifier,
    route_after_guardrails_in,
    route_after_guardrails_out,
    route_after_tool_executor,
)

from app.agent.nodes import (
    classifier_node,
    response_generator_node,
    tool_executor_node,
    tool_planner_node,
)

from app.guardrails import guardrails_in_node , guardrails_out_node

from app.agent.state import AgentState

logger = structlog.get_logger(__name__)




async def _stub_human_handoff(state: AgentState) -> dict:
    """Human escalation stub — returns a canned escalation message.  # STUB — TODO(Phase 4)

    Real node will:
    - Create a support ticket in the ticketing system.
    - Post to the live-agent queue with customer context attached.
    - Return a confirmation AIMessage with the ticket reference number.
    - Set a Redis flag so subsequent turns in this session are routed to
      the live-agent channel rather than re-entering the AI graph.
    """
    logger.info(
        "stub.human_handoff",
        session_id=state.get("session_id"),
        user_id=state.get("user_id"),
        intent=state.get("intent"),
    )
    return {
        "messages": [
            AIMessage(
                content=(
                    "I understand your concern and I want to make sure you receive "
                    "the best possible help. I'm connecting you with a member of our "
                    "support team now. A human agent will be with you shortly — "
                    "thank you for your patience."
                )
            )
        ],
        "needs_escalation": True,
    }
    
    
def build_graph(checkpointer=None):
    """Build and compile the LangGraph StateGraph.

    Constructs the full agent workflow: registers every node (real + stubs),
    wires all conditional routing edges, and compiles to a ``CompiledStateGraph``.

    Separation from module-level instantiation makes the factory directly
    testable — tests can call ``build_graph()`` to get a fresh graph with a
    custom checkpointer or mocked nodes without affecting the production singleton.

    Returns:
        A compiled ``CompiledStateGraph`` that exposes:
        - ``await graph.ainvoke(state, config)``     — single-turn invocation
        - ``graph.astream_events(state, config)``    — async event stream
          used by the WebSocket endpoint for streaming token-by-token output
    """
    workflow = StateGraph(AgentState)

    workflow.add_node(NODE_CLASSIFIER, classifier_node)
    workflow.add_node(NODE_RESPONSE_GENERATOR, response_generator_node)
    
    workflow.add_node(NODE_TOOL_PLANNER, tool_planner_node)
    workflow.add_node(NODE_TOOL_EXECUTOR, tool_executor_node)
    
    workflow.add_node(NODE_GUARDRAILS_IN, guardrails_in_node)       
    workflow.add_node(NODE_GUARDRAILS_OUT, guardrails_out_node)
    workflow.add_node(NODE_HUMAN_HANDOFF, _stub_human_handoff)
    
    # Every invocation enters at guardrails_in
    workflow.add_edge(START, NODE_GUARDRAILS_IN)
    
    
    workflow.add_conditional_edges(
        NODE_GUARDRAILS_IN,
        route_after_guardrails_in,
        {
            NODE_CLASSIFIER: NODE_CLASSIFIER,
            END: END,
        },
    )
    
    
    workflow.add_conditional_edges(
        NODE_CLASSIFIER,
        route_after_classifier,
        {
            NODE_TOOL_PLANNER: NODE_TOOL_PLANNER,
            NODE_RESPONSE_GENERATOR: NODE_RESPONSE_GENERATOR,
            NODE_HUMAN_HANDOFF: NODE_HUMAN_HANDOFF,
        },
    )
    
 
    workflow.add_edge(NODE_TOOL_PLANNER, NODE_TOOL_EXECUTOR)
    
    
    workflow.add_conditional_edges(
        NODE_TOOL_EXECUTOR,
        route_after_tool_executor,
        {
            NODE_TOOL_PLANNER: NODE_TOOL_PLANNER,
            NODE_RESPONSE_GENERATOR: NODE_RESPONSE_GENERATOR,
        },
    )
    
    
    workflow.add_edge(NODE_RESPONSE_GENERATOR, NODE_GUARDRAILS_OUT)


    workflow.add_conditional_edges(
        NODE_GUARDRAILS_OUT,
        route_after_guardrails_out,
        {
            END: END,
            NODE_RESPONSE_GENERATOR: NODE_RESPONSE_GENERATOR,
        },
    )

   
    workflow.add_edge(NODE_HUMAN_HANDOFF, END)
    
    compiled = workflow.compile(checkpointer=checkpointer)

    logger.info(
        "graph.compiled",
        max_tool_retries=MAX_TOOL_RETRIES,
        max_output_retries=MAX_OUTPUT_RETRIES,
        real_nodes=[
            NODE_GUARDRAILS_IN,
            NODE_CLASSIFIER,
            NODE_RESPONSE_GENERATOR,
            NODE_TOOL_PLANNER,
            NODE_TOOL_EXECUTOR,
            NODE_GUARDRAILS_OUT,
        ],
        stub_nodes=[
            NODE_HUMAN_HANDOFF,
        ],
    )

    return compiled

