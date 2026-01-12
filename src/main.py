from langchain_core.messages import HumanMessage
from agent.graph import build_graph
from utils.logger import get_logger

logger = get_logger()


def main():
    logger.info("Social-to-Lead Agent starting...")
    graph = build_graph()

    state = {
        "session_id": "demo-session",
        "messages": [],
        "intent": None,
        "confidence": None,
        "user_details": {},
        "context": None,
        "lead_captured": False,
        "last_action": None,
    }

    while not state["lead_captured"]:
        user_input = input("User: ")
        state["messages"].append(HumanMessage(content=user_input))
        state = graph.invoke(state)

        for msg in state["messages"]:
            if msg.type == "ai":
                print(f"Agent: {msg.content}")
        state["messages"] = []


if __name__ == "__main__":
    main()
