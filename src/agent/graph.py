from langgraph.graph import StateGraph, END

from agent.state import ConversationState
from agent.nodes import (
    intent_node,
    greeting_node,
    rag_node,
    lead_node,
    fallback_node,
)


def route(state: ConversationState):
    # If we are actively collecting lead details (collecting_lead flag),
    # stay in the lead node until capture completes.
    if not state.get("lead_captured") and state.get("collecting_lead"):
        return "lead"

    intent = state.get("intent")

    if intent == "greeting":
        return "greeting"
    elif intent == "inquiry":
        return "rag"
    elif intent == "high_intent":
        return "lead"
    else:
        return "fallback"



def build_graph():
    graph = StateGraph(ConversationState)

    graph.add_node("intent", intent_node)
    graph.add_node("greeting", greeting_node)
    graph.add_node("rag", rag_node)
    graph.add_node("lead", lead_node)
    graph.add_node("fallback", fallback_node)

    graph.set_entry_point("intent")

    graph.add_conditional_edges(
        "intent",
        route,
        {
            "greeting": "greeting",
            "rag": "rag",
            "lead": "lead",
            "fallback": "fallback",
        },
    )

    graph.add_edge("greeting", END)
    graph.add_edge("rag", END)
    graph.add_edge("lead", END)
    graph.add_edge("fallback", END)

    return graph.compile()
