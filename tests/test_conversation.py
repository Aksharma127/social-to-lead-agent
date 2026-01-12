from langchain_core.messages import HumanMessage

from agent.graph import build_graph


def test_high_intent_lead_capture_flow():
    graph = build_graph()

    state = {
        "session_id": "test-session",
        "messages": [],
        "intent": None,
        "confidence": None,
        "user_details": {},
        "context": None,
        "lead_captured": False,
        "last_action": None,
    }

    # Turn 1: High intent
    state["messages"].append(HumanMessage(content="I want a demo"))
    state = graph.invoke(state)

    assert state["lead_captured"] is False
    assert "email" not in state["user_details"]

    # Turn 2: Provide email
    state["messages"] = [HumanMessage(content="test@example.com")]
    state = graph.invoke(state)

    assert "email" in state["user_details"]

    # Turn 3: Provide name
    state["messages"] = [HumanMessage(content="Akshit")]
    state = graph.invoke(state)

    assert state["lead_captured"] is True
