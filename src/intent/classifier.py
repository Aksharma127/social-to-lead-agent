"""Intent classifier.

This module provides a small IntentResult model and a classify_intent
function. If a LLM (langchain_openai) is available it would be used,
otherwise a deterministic rule-based fallback is used so tests and local
development work without external dependencies.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Optional

try:
    # Optional imports for LLM-based classification (may not be installed in dev)
    from langchain_openai import ChatOpenAI  # type: ignore
    from langchain_core.messages import HumanMessage  # type: ignore
    _HAS_LLM = True
except Exception:
    _HAS_LLM = False

from pydantic import BaseModel, ValidationError

from utils.config import settings
from utils.logger import get_logger

logger = get_logger()


class IntentResult(BaseModel):
    intent: str
    confidence: float

"""
Gemini-first intent classifier. Uses Google Gemini via
`langchain_google_genai.ChatGoogleGenerativeAI` when available and falls
back to a deterministic rule-based classifier if Gemini isn't available
or fails at runtime.
"""
from pydantic import BaseModel, Field, ValidationError
import re

from utils.config import settings
from utils.logger import get_logger

logger = get_logger()


class IntentResult(BaseModel):
    intent: str = Field(...)
    confidence: float = Field(..., ge=0.0, le=1.0)


INTENT_PROMPT = """
You are an intent classification engine.

Classify the user's message into ONE of:
- greeting
- inquiry
- high_intent
- clarification

Return ONLY valid JSON:
{
  "intent": "<intent>",
  "confidence": <float between 0 and 1>
}

If unsure, use "clarification".
"""

try:
    from langchain_google_genai import ChatGoogleGenerativeAI  # type: ignore
    _HAS_GEMINI = True
except Exception:
    _HAS_GEMINI = False


def _rule_based_classify(message: str) -> IntentResult:
    text = (message or "").lower().strip()
    if not text or re.match(r'^[^a-zA-Z0-9]+$', text):
        return IntentResult(intent="clarification", confidence=0.5)

    if re.search(r'\b(hi|hello|hey|good morning|good afternoon)\b', text):
        return IntentResult(intent="greeting", confidence=0.9)

    if re.search(r'\b(demo|pricing|price|buy|subscribe|plan|purchase)\b', text):
        return IntentResult(intent="high_intent", confidence=0.95)

    if re.search(r'\b(what|how|which|where|when|why|details|features)\b', text):
        return IntentResult(intent="inquiry", confidence=0.8)

    return IntentResult(intent="clarification", confidence=0.4)


def classify_intent(message: str) -> IntentResult:
    if _HAS_GEMINI:
        try:
            llm = ChatGoogleGenerativeAI(
                model=getattr(settings, "MODEL_NAME", "gemini-1.5-flash"),
                temperature=getattr(settings, "TEMPERATURE", 0.1),
                max_output_tokens=getattr(settings, "MAX_TOKENS", 256),
                google_api_key=getattr(settings, "GOOGLE_API_KEY", None),
            )

            response = llm.invoke(INTENT_PROMPT + "\nUser message:\n" + (message or ""))
            text = (response.content or "").strip()
            text = text.replace("```json", "").replace("```", "").strip()
            return IntentResult.model_validate_json(text)

        except (ValidationError, Exception) as e:
            logger.warning(f"Gemini intent classification failed: {e}")

    return _rule_based_classify(message)
    # Deterministic fallback
