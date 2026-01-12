import re 
from tools.lead_capture import Lead, mock_lead_capture
from langchain_core.messages import AIMessage, HumanMessage

from intent.classifier import classify_intent
from rag.knowledge_base import retrieve_context
from utils.logger import get_logger

logger = get_logger()


def intent_node(state):
    # If we're in the middle of lead collection (or we just prompted for it), skip intent classification
    if (state.get("collecting_lead") or state.get("last_action") == "lead_prompted") and not state.get("lead_captured"):
        return state

    # get the most recent human message (ignore AI messages)
    last_user_msg = ""
    for m in reversed(state.get("messages", [])):
        if isinstance(m, HumanMessage):
            last_user_msg = m.content
            break

    # Normal path: classify intent
    result = classify_intent(last_user_msg)

    state["intent"] = result.intent
    state["confidence"] = result.confidence
    state["last_action"] = "intent_classified"

    logger.info(f"Intent detected: {result.intent} ({result.confidence})")

    return state


def greeting_node(state):
    response = "Hello! How can I help you today?"

    state["messages"].append(AIMessage(content=response))
    state["last_action"] = "greeting_response"

    return state


def rag_node(state):
    query = state["messages"][-1].content
    context = retrieve_context(query)

    response = f"Here’s some relevant information:\n{context}"

    state["context"] = context
    state["messages"].append(AIMessage(content=response))
    state["last_action"] = "rag_response"

    return state


def lead_node(state):
    # find most recent human message
    last_user_msg = ""
    for m in reversed(state.get("messages", [])):
        if isinstance(m, HumanMessage):
            last_user_msg = m.content
            break

    details = state.get("user_details", {})

    if not details.get("email"):
        email = extract_email(last_user_msg)
        if email:
            details["email"] = email
        else:
            state["messages"].append(
                AIMessage(content="Please share your email address to proceed.")
            )
            state["last_action"] = "lead_prompted"
            state["collecting_lead"] = True
            state["user_details"] = details
            return state

    if not details.get("name"):
        # If the last human message is not an email, treat it as the name.
        if last_user_msg and not extract_email(last_user_msg):
            details["name"] = last_user_msg.strip()
        else:
            state["messages"].append(
                AIMessage(content="Thanks! Could you also share your name?")
            )
            state["last_action"] = "lead_prompted"
            state["collecting_lead"] = True
            state["user_details"] = details
            return state

    lead = Lead(
        name=details["name"],
        email=details["email"],
        platform=details.get("platform", "unknown"),
    )

    success = mock_lead_capture(lead)

    if success:
        state["lead_captured"] = True
        state["messages"].append(
            AIMessage(content="You're all set! Our team will contact you shortly.")
        )
    # lead capture complete
    state["last_action"] = "lead_captured"
    state["collecting_lead"] = False
    return state



def fallback_node(state):
    response = "Could you please clarify your request?"

    state["messages"].append(AIMessage(content=response))
    state["last_action"] = "clarification_requested"

    return state

def extract_email(text: str):
    match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
    return match.group(0) if match else None