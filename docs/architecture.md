# Architecture Documentation

**Social-to-Lead Agentic Workflow**

---

## 1. Purpose of This Architecture

This document explains **how the system is structured**, **how data flows through it**, and **why specific design decisions were made**.

The goal of the architecture is to build a **clear, extensible, and production-style conversational agent** that can:

* Understand user intent
* Answer product questions accurately
* Detect high-intent users
* Trigger backend actions (lead capture)

The focus is on **correct abstractions and agent reasoning**, not platform-specific integrations.

---

## 2. High-Level Architecture Overview

At a high level, the system is composed of four layers:

1. **Input Layer** – User messages (CLI-simulated social input)
2. **Agent Core** – Intent detection, routing, and state management
3. **Knowledge Layer** – Retrieval-Augmented Generation (RAG)
4. **Action Layer** – Backend tool execution (lead capture)

All layers are coordinated using a **state-driven agent graph**.
---
## 3. Architectural Principles

### 3.1 Platform-Agnostic Design

The agent core is **not coupled** to any specific social platform (WhatsApp, Instagram, etc.).

Messages are treated as plain text inputs.
This keeps the system:

* Easy to test
* Easy to evaluate
* Easy to integrate later

---

### 3.2 Explicit State Management

All conversational data is stored in a single, typed state object (`ConversationState`).

This avoids:

* Hidden memory
* Implicit side effects
* Hard-to-debug flows

Every node:

* Reads from state
* Writes back to state
* Produces predictable transitions

---

### 3.3 Separation of Concerns

Each module has a **single, clear responsibility**:

* Intent classifier → understands what the user wants
* RAG module → answers product questions
* Agent graph → controls flow and decisions
* Lead tool → simulates backend action

This keeps the system easy to reason about and extend.

---

## 4. Core Components

---

### 4.1 Entry Point (`main.py`)

The entry point is intentionally lightweight.

Responsibilities:

* Initialize the agent graph
* Maintain the conversation loop
* Pass user input into the agent
* Display agent responses

It does **not** contain business logic.
This mirrors real-world systems where I/O and logic are separated.

---

### 4.2 Conversation State (`ConversationState`)

The `ConversationState` object represents the **entire conversation context**.

Key fields:

* `session_id` – conversation identifier
* `messages` – conversation messages
* `intent` – detected intent
* `confidence` – intent confidence score
* `user_details` – collected lead information
* `context` – retrieved RAG content
* `lead_captured` – completion flag
* `last_action` – observability and debugging

This makes the agent deterministic and debuggable.

---

### 4.3 Intent Classification

Intent classification is the **decision driver** of the system.

Supported intents:

* `greeting`
* `inquiry`
* `high_intent`
* `clarification`

Design decisions:

* LLM-based classification (Gemini)
* Strict JSON output
* Confidence scoring
* Deterministic fallback on failure

This avoids brittle keyword matching and improves robustness.

---

### 4.4 RAG (Retrieval-Augmented Generation)

The RAG module handles **accurate product question answering**.

Flow:

1. Product knowledge is stored as documents
2. Documents are embedded and persisted in a vector store (ChromaDB)
3. User queries are embedded at runtime
4. Semantic similarity search retrieves relevant content
5. Retrieved context is used to generate grounded responses

Key benefits:

* Reduced hallucination
* More accurate answers
* Clear knowledge grounding

---

### 4.5 Agent Graph (LangGraph)

The agent workflow is implemented using **LangGraph**.

The graph consists of:

* Nodes (units of logic)
* A router (decision logic)
* Explicit edges (state transitions)

Main nodes:

* Intent node
* Greeting node
* RAG node
* Lead node
* Fallback node

Routing decisions are made based on:

* Detected intent
* Current conversation state

This makes agent behavior explicit and traceable.

---

### 4.6 Lead Qualification Flow

When high intent is detected, the agent enters a **dedicated lead capture flow**.

Important behavior:

* Intent re-classification is paused
* The agent stays in lead mode until completion
* Details are collected across multiple turns

Steps:

1. Ask for email
2. Validate email format
3. Ask for name
4. Trigger backend action
5. Confirm success

This reflects real-world conversational lead capture behavior.

---

### 4.7 Backend Tool (Mock Lead Capture)

Backend actions are represented via a **tool abstraction**.

In this project:

* Lead capture is mocked
* Inputs are validated using Pydantic
* Execution is logged

This clearly demonstrates:

* Tool boundaries
* Side effects
* Integration points

In production, this tool could connect to a CRM or sales system.

---

## 5. Error Handling & Robustness

The system is designed to fail gracefully.

Examples:

* If intent classification fails → fallback intent is used
* If input is unclear → clarification is requested
* If details are missing → the agent asks again
* No failure crashes the entire conversation

This is essential for real-world conversational systems.

---

## 6. Testing Strategy

Testing focuses on **system behavior**, not internal implementation.

Included tests:

* Intent classification tests
* RAG retrieval tests
* End-to-end conversation flow test

The end-to-end test validates:

* Correct routing
* State persistence
* Successful lead capture

This ensures confidence in the full workflow.

---

## 7. Extensibility

The architecture is intentionally extensible.

Possible future extensions:

* WhatsApp / Instagram adapters
* Redis-backed state persistence
* CRM integration
* Demo scheduling
* Human handoff

These are documented but not implemented to keep the submission focused and evaluable.

---

## 8. Architectural Summary

This architecture prioritizes:

* Clear state-driven design
* Explicit agent reasoning
* Robust error handling
* Production-style abstractions

