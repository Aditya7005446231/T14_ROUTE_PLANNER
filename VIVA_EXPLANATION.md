# 🎓 Viva & Project Defense Guide: T14 Multi-Stop Route Planner

This document is your complete cheat sheet for explaining the **T14 Multi-Stop Route Planner** project during your viva examination or project presentation.

---

## 🚀 1. The 1-Minute Elevator Pitch (Opening Statement)

> *"Good morning/afternoon. My project is **T14 Multi-Stop Route Planner**, an autonomous AI travel agent built using **LangChain**, **LangGraph**, and **Groq (Qwen 2.7B / Llama 3.3)**.*
> 
> *Instead of using static algorithms or hardcoded menus, our agent uses the **ReAct (Reasoning + Acting) design pattern**. When a user specifies cities to visit (e.g., Delhi, Agra, Jaipur), the LLM autonomously calls custom python tools (`get_distance`) to look up road distances, evaluates permutations in its reasoning step to find the shortest route, and commits the optimal itinerary into application state (`order_stops`).*
> 
> *Furthermore, it incorporates **LangGraph MemorySaver** for multi-turn conversational memory—allowing users to add new stops across conversation turns without re-stating their previous trip details."*

---

## 🏗️ 2. System Architecture & Tech Stack

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        User Interface / Notebook                        │
│                           (agent_demo.ipynb)                            │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │ User Prompt (Multi-turn)
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    LangGraph ReAct Agent Framework                      │
│                                                                         │
│   ┌───────────────────────┐             ┌───────────────────────────┐   │
│   │ MemorySaver (RAM)     │             │ Groq Chat LLM             │   │
│   │ Checkpointer          │◄───────────►│ (qwen/qwen3.6-27b)        │   │
│   │ (thread_id state)     │             │ (Reasoning Engine)        │   │
│   └───────────────────────┘             └─────────────┬─────────────┘   │
└───────────────────────────────────────────────────────┼─────────────────┘
                                                        │ Invokes Tools
                                                        ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           tools.py (Backend)                            │
│                                                                         │
│  • get_distance(a, b) ──► CITY_DISTANCES Dict (Mock Lookup Dataset)    │
│  • order_stops(route) ──► SAVED_ROUTES = [] (Session State Storage)     │
└─────────────────────────────────────────────────────────────────────────┘
```

| Technology | Role / Purpose |
| :--- | :--- |
| **LangChain (`langchain-core`, `langchain-groq`)** | Standardized tool decorator (`@tool`), message abstractions (`HumanMessage`, `AIMessage`, `ToolMessage`), and LLM integration. |
| **LangGraph (`langgraph`)** | Agent orchestration (`create_react_agent`) and state checkpointer (`MemorySaver`). |
| **Groq API (`qwen/qwen3.6-27b`)** | Ultra-fast LLM inference engine supporting native Tool Calling / Function Calling. |
| **Python (`tools.py`)** | Custom domain tools (`get_distance`, `order_stops`) and mock dataset dictionary. |

---

## 🛠️ 3. Deep Dive into Code & Component Responsibilities

### A. `tools.py` — The Backend Capabilities

1. **`CITY_DISTANCES` Dictionary**:
   * Stores symmetric driving distances in kilometers between 5 major Indian tourist cities: Delhi, Agra, Jaipur, Chandigarh, and Amritsar.
2. **`get_distance(a, b)`**:
   * Decorated with `@tool`.
   * Accepts two city names and looks up distance.
   * Returns a clean string output (e.g., *"Driving distance between Delhi and Agra is 233 km"*).
3. **`order_stops(route)`**:
   * Decorated with `@tool`.
   * Commits the optimized city sequence into the global array `SAVED_ROUTES`.
   * **Resilience Feature**: Uses `Union[List[str], str]` and string parsing so that if the LLM passes `"Delhi -> Agra -> Jaipur"` instead of a list `['Delhi', 'Agra', 'Jaipur']`, it doesn't crash!
4. **`SAVED_ROUTES`**:
   * In-memory array storing committed itineraries across session state.

### B. `agent_demo.ipynb` — The Agent & Execution Driver

1. **Cell 1 & 2**: Loads environment variables (`GROQ_API_KEY`, `GROQ_MODEL`) using `dotenv`.
2. **Cell 3**: Initializes `ChatGroq(model="qwen/qwen3.6-27b", temperature=0)`.
3. **Cell 4**: Initializes `MemorySaver()` checkpointer and constructs the `ReAct` agent via `create_react_agent`.
4. **Cell 5 (`run_agent_turn`)**: Helper function that streams execution traces to display:
   * `[AGENT THOUGHT / TOOL CALL]`
   * `[TOOL OUTPUT]`
   * `[FINAL AGENT RESPONSE]`
5. **Demo Turns**:
   * **Turn 1**: Plans initial route (Delhi -> Agra -> Jaipur).
   * **Turn 2**: Adds Chandigarh, demonstrating memory retention.
   * **Turn 3**: Summarizes final saved state.

---

## 🧠 4. Key Agentic Concepts to Explain in Viva

### 1. ReAct Design Pattern (Reasoning + Acting)
* **What it is**: ReAct combines **Reasoning** (chain-of-thought planning) with **Acting** (invoking external tools).
* **Execution Loop**:
  $$\text{Thought} \longrightarrow \text{Action (Tool Call)} \longrightarrow \text{Observation (Tool Output)} \longrightarrow \text{Thought} \longrightarrow \text{Final Answer}$$

### 2. Conversational Memory vs Application State
* **Conversational Memory (`MemorySaver`)**:
  * Retains chat history in RAM indexed by `thread_id`.
  * Enables the LLM to remember previous prompts and tool outputs across multi-turn interactions.
* **Application State (`SAVED_ROUTES`)**:
  * Stores structured application data (`['Delhi', 'Agra', 'Jaipur']`) created when `order_stops` is executed.
  * Decouples raw conversation text from application state data.

### 3. Temperature = 0
* Setting `temperature=0` ensures **deterministic**, consistent tool parameters and mathematical logic, eliminating random creative hallucination during route selection.

---

## ❓ 5. Top 10 Viva Questions & Winning Answers

#### Q1: Why did you use an Agentic AI approach instead of traditional Python Dijkstra/TSP code?
> **Answer**: *"A traditional Travelling Salesperson Problem (TSP) algorithm requires strict structured input and cannot understand natural language or user preferences (e.g. 'I want to visit Agra first, then add Chandigarh'). An Agentic approach bridges natural language processing with tool execution, allowing users to interact conversationally while the agent handles query parsing, data fetching, and state updates dynamically."*

#### Q2: Is distance calculation done by the LLM or Python?
> **Answer**: *"Python tools provide the raw pairwise distance data via `get_distance(a, b)`. The LLM receives these values, performs the arithmetic addition and permutation comparison in its reasoning step, and selects the route order with the minimal total distance."*

#### Q3: What happens if the LLM outputs a string like `"Delhi -> Agra -> Jaipur"` instead of a Python list?
> **Answer**: *"We designed `order_stops` with input resilience using `Union[List[str], str]`. If the LLM passes a string separated by arrows or commas, our python code parses it into a normalized list `['Delhi', 'Agra', 'Jaipur']` before appending to state, preventing tool validation failure."*

#### Q4: Where is `MemorySaver` stored? Is it persistent after restarting Python?
> **Answer**: *"In our demo, `MemorySaver` stores state in RAM (Application Memory). It is fast and lightweight for interactive sessions. For persistent storage across server restarts, `MemorySaver` can be replaced with `SqliteSaver` or `PostgresSaver` without changing the agent logic."*

#### Q5: Why did you select Groq (`qwen/qwen3.6-27b`)?
> **Answer**: *"Groq provides LPU (Language Processing Unit) hardware acceleration delivering near-instant inference speeds. `qwen/qwen3.6-27b` has native Tool-Calling (Function Calling) support, making tool parameter extraction 100% accurate."*

#### Q6: How does the agent distinguish between different users' chat sessions?
> **Answer**: *"LangGraph checkpointer uses a `configurable` dictionary containing a `thread_id` (e.g. `{"configurable": {"thread_id": "session_1"}}`). Each unique `thread_id` maintains its own isolated conversation history."*

#### Q7: What are `@tool` decorators in LangChain?
> **Answer**: *"The `@tool` decorator inspects a Python function's signature and docstring, converting it into a Pydantic JSON Schema. This schema is passed to the LLM API so the model knows the tool's name, description, and required arguments."*

#### Q8: What happens if a user asks for a city not in `CITY_DISTANCES` (e.g., 'Mumbai')?
> **Answer**: *"The `get_distance` function checks the dictionary and gracefully returns an error message: `'Distance lookup failed: Unknown distance between Delhi and Mumbai. Available cities: Delhi, Agra, Jaipur, Chandigarh, Amritsar.'` The LLM reads this observation and politely informs the user."*

#### Q9: What is the difference between `langchain` and `langgraph`?
> **Answer**: *"LangChain provides primitives like LLM wrappers, prompts, and tool abstractions. LangGraph provides cyclic state-graph orchestration, managing the ReAct execution loop, state transitions, and memory checkpointing."*

#### Q10: How would you scale this project to a real-world enterprise app?
> **Answer**: *"To scale this:
> 1. Replace the mock `CITY_DISTANCES` dictionary with the live **Google Maps Distance Matrix API**.
> 2. Replace `MemorySaver` with **`SqliteSaver` / PostgreSQL** for persistent user history.
> 3. Build a React/Streamlit Web UI consuming the LangGraph agent endpoint."*

---

## 📌 Summary Checklist for Demo Day

- [x] `.env` file configured with `GROQ_API_KEY` & `GROQ_MODEL=qwen/qwen3.6-27b`.
- [x] Kernel selected: `Python 3.14`.
- [x] Run All executed in `agent_demo.ipynb`.
- [x] State verified in final output cell showing committed routes.
