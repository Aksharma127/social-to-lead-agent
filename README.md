# Architecture Overview (Social-to-Lead Agent)

This document explains **how the system is designed**, **why certain decisions were made**, and **how different components work together** to fulfill the assignment requirements.

The goal of this architecture is **clarity, robustness, and production-readiness**, not feature overload.

---

## 1. High-Level System View

At a high level, the system is a **state-driven conversational agent** that converts social interactions into qualified leads.

The flow looks like this:

1. User sends a message (simulated via CLI)
2. The agent understands **intent**
3. Based on intent, the agent:

   * Greets the user
   * Answers product questions (via RAG)
   * Or enters a lead capture flow
4. For high-intent users, a backend action (mock lead capture) is triggered
5. State is preserved across turns

Everything is orchestrated through a **central agent graph**.

---
project/
├── src/
│ ├── agent/
│ │ ├── graph.py # LangGraph workflow & routing
│ │ ├── nodes.py # Agent nodes (intent, RAG, lead flow)
│ │ └── state.py # Typed conversation state
│ ├── intent/
│ │ └── classifier.py # Intent detection logic
│ ├── rag/
│ │ ├── knowledge_base.py # RAG setup & retrieval
│ │ └── data/
│ │ └── autostream_kb.json
│ ├── tools/
│ │ └── lead_capture.py # Mock backend lead capture tool
│ ├── utils/
│ │ ├── config.py # Central configuration
│ │ └── logger.py # Logging setup
│ └── main.py # CLI entry point
├── tests/
│ ├── test_intent.py
│ ├── test_rag.py
│ └── test_conversation.py
├── docs/
│ └── architecture.md
├── .env.example
├── .gitignore
├── requirements.txt
├── pyproject.toml
└── README.md
---
## 2. Core Architectural Principles

Before going into components, it’s important to understand the principles guiding the design.

### 2.1 Platform-Agnostic Core

The agent core does **not** depend on WhatsApp, Instagram, or any specific platform.

Messages are treated as plain text inputs.
This makes the system:

* Easy to test
* Easy to evaluate
* Easy to later integrate with real social platforms

---

### 2.2 Explicit State Management

All conversation data lives inside a **typed state object** (`ConversationState`).

This avoids:

* Hidden globals
* Implicit memory
* Hard-to-debug side effects

Every node in the agent graph:

* Reads from state
* Writes back to state
* Produces predictable transitions

---

### 2.3 Clear Separation of Responsibilities

Each part of the system has **one clear job**:

* Intent classifier → understand what the user wants
* RAG module → answer product questions
* Lead flow → collect and validate details
* Tool → simulate backend action

This keeps the system easy to reason about.

---

## 3. Component-Level Breakdown

---

### 3.1 Entry Point (`main.py`)

`main.py` is intentionally simple.

Its responsibilities are:

* Initialize the agent graph
* Maintain the conversation loop
* Pass user input into the system
* Display agent responses

It does **not** contain business logic.

This mirrors how real systems work, where:

* Entry points handle I/O
* Core logic lives elsewhere

---

### 3.2 Conversation State (`ConversationState`)

The entire system revolves around a shared state object.

Key fields include:

* `messages`: conversation messages
* `intent`: detected user intent
* `confidence`: intent confidence score
* `user_details`: collected lead information
* `context`: retrieved RAG context
* `lead_captured`: completion flag
* `last_action`: debugging and observability aid

This makes the agent:

* Deterministic
* Inspectable
* Easy to extend

---

### 3.3 Intent Classification Module

The intent classifier is the **decision brain** of the agent.

It classifies messages into:

* `greeting`
* `inquiry`
* `high_intent`
* `clarification`

Design choices:

* LLM-based classification (Gemini)
* Strict JSON output
* Confidence scoring
* Deterministic fallback on failure

Why this matters:

* Avoids brittle keyword matching
* Handles natural language variation
* Prevents crashes due to malformed output

---

### 3.4 RAG (Retrieval-Augmented Generation) Module

The RAG module is responsible for **accurate product question answering**.

How it works:

1. Product knowledge is stored as documents
2. Documents are embedded and persisted in a vector store (ChromaDB)
3. User queries are embedded at runtime
4. Semantic similarity search retrieves relevant content
5. Retrieved context is used to generate grounded responses

Key design choices:

* Persistent local vector store (no external infra)
* Small, focused knowledge base
* Clear separation between ingestion and retrieval

This reduces hallucination and improves answer reliability.

---

### 3.5 Agent Graph (LangGraph Workflow)

LangGraph is used to orchestrate the agent’s behavior.

The graph consists of:

* **Nodes** (units of work)
* **Router** (decision logic)
* **Edges** (state transitions)

Key nodes:

* Intent node
* Greeting node
* RAG node
* Lead node
* Fallback node

The router decides which node to execute based on:

* Detected intent
* Current conversation state

This makes agent behavior:

* Explicit
* Traceable
* Easy to debug

---

### 3.6 Lead Qualification & Capture Flow

When high intent is detected, the agent enters a **dedicated lead flow**.

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

This mirrors real-world conversational lead capture.

---

### 3.7 Backend Tool (Mock Lead Capture)

Backend actions are represented via a **tool interface**.

In this project:

* Lead capture is mocked
* Inputs are validated using Pydantic
* Execution is logged

Why a mock tool?

* Keeps the assignment self-contained
* Demonstrates side effects
* Makes integration points explicit

In production, this tool could be replaced with:

* CRM APIs
* Ticketing systems
* Demo scheduling services

---

## 4. Error Handling & Robustness

The system is designed to **fail gracefully**.

Examples:

* If intent classification fails → fallback intent is used
* If user input is unclear → clarification is requested
* If details are missing → the agent asks again
* No step crashes the entire conversation

This is critical for real conversational systems.

---

## 5. Testing Strategy

Testing focuses on **behavior**, not implementation details.

Included tests:

* Intent classification tests
* RAG retrieval tests
* End-to-end conversation flow test

The end-to-end test proves:

* Correct routing
* State persistence
* Successful lead capture

This ensures confidence in the full system, not just isolated functions.

---

## 6. Why This Architecture Fits the Assignment

This design directly supports the assignment goals:

* Understand user intent → intent classifier
* Answer product questions → RAG
* Identify high-intent users → routing logic
* Trigger backend actions → lead capture tool

At the same time, it avoids:

* Overengineering
* Unnecessary infrastructure
* Platform-specific complexity

---

## 7. Extensibility Notes

The architecture is intentionally extensible.

Possible future additions:

* WhatsApp / Instagram adapters
* Redis-backed state persistence
* CRM integration
* Analytics and monitoring
* Human handoff

These were documented rather than implemented to keep the submission focused and evaluable.
