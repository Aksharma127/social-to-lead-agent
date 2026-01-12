from intent.classifier import classify_intent

def test_greeting_intent():
    result = classify_intent("Hi there!")
    assert result.intent == "greeting"
    assert result.confidence > 0.5

def test_high_intent():
    result = classify_intent("I want a demo and pricing details")
    assert result.intent == "high_intent"

def test_ambiguous_input():
    result = classify_intent("???")
    assert result.intent == "clarification"
