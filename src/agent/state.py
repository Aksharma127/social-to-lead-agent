from typing import List, Dict, Optional, TypedDict
from langchain_core.messages import BaseMessage

class ConversationState(TypedDict):
    session_id: str
    messages: List[BaseMessage]
    intent: Optional[str]
    confidence: Optional[float]
    user_details: Dict[str, Optional[str]]
    context: Optional[str]
    lead_captured: bool
    last_action: Optional[str]
 