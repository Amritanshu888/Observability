## LangSmith — What is being done here?

The lecture is using **LangSmith primarily as an observability and tracing UI** for the LangGraph agentic workflow.

The basic architecture is:

```text
User
  ↓
Streamlit App
  ↓
LangGraph Workflow
  ↓
┌──────────────────────────────────────┐
│ Planner                              │
│   ↓                                  │
│ Document Reader                      │
│   ↓                                  │
│ Web Enricher                         │
│   ↓                                  │
│ Synthesizer                          │
│   ↓                                  │
│ Report Writer                        │
└──────────────────────────────────────┘
  ↓
Final Response

        ↓ tracing / observability

     LangSmith UI
```

The lecturer explicitly shows that after asking a question in the Streamlit application, the **entire execution can be inspected as a trace**, including the individual agents/nodes, latency, costs and execution flow. Pasted markdown

---

# 1. Why are we using LangSmith?

The main purpose here is **observability**.

Instead of only seeing:

```text
User Question
      ↓
Final Answer
```

LangSmith allows us to see **what happened internally**:

```text
User Question
      ↓
Planner
      ↓
Document Reader
      ↓
Web Enricher
      ↓
Synthesizer
      ↓
Report Writer
      ↓
Final Answer
```

This is important for an agentic application because the final answer alone doesn't tell us:

- Which agent ran?
- In what order?
- What did each agent do?
- How long did each step take?
- What was the latency?
- What did the LLM generate at each step?
- What was the cost?
- Where did an error/hallucination originate?

The lecturer demonstrates exactly this by opening the trace and seeing the planner, document reader, web enricher, synthesizer and report writer executions. Pasted markdown

---

# 2. First build the Streamlit application

Before getting into the LangSmith UI, the lecture first converts the existing LangGraph workflow into a Streamlit application.

The application generates a **new session ID** whenever the application/session starts.

```python
import uuid

session_id = str(uuid.uuid4())
```

The reason is to distinguish different user/application sessions.

The lecturer demonstrates that refreshing the application results in a different session ID. Pasted markdown

### Why session IDs matter

For example:

```text
User A → Session ID: abc123
User B → Session ID: xyz789
```

This helps associate executions/conversations with a particular session.

---

# 3. Add LangSmith trace access to the Streamlit UI

The Streamlit sidebar contains information about the application and also provides a way for the user to access the traces.

The lecturer says that the sidebar will contain a message telling the user:

> if you want to see the traces go to this endpoint

So the Streamlit application becomes the **user-facing application**, while LangSmith becomes the **developer/observability interface**. Pasted markdown

Conceptually:

```text
                 ┌───────────────┐
                 │ Streamlit UI  │
                 │               │
User ───────────→│ Ask Question  │
                 └───────┬───────┘
                         │
                         ↓
                  LangGraph Agent
                         │
                         ↓
                  Trace generated
                         │
                         ↓
                 ┌───────────────┐
                 │ LangSmith UI  │
                 │               │
                 │ Trace         │
                 │ Tree          │
                 │ Waterfall     │
                 │ Latency       │
                 │ Cost          │
                 └───────────────┘
```

---

# 4. Run a question from the Streamlit application

The user enters a question such as:

```text
Search about latest LLM threats
```

The LangGraph workflow executes.

The important thing is that **the execution is being traced**.

The lecturer then opens the trace UI and can inspect the execution. Pasted markdown

---

# 5. LangSmith shows the complete agent execution

This is probably the **most important part of the lecture**.

The trace shows something like:

```text
Planner
   ↓
Document Reader
   ↓
Web Enricher
   ↓
Synthesizer
   ↓
Report Writer
```

The lecturer specifically explains what each part is doing.

### Planner

The planner takes the original question and refines it.

Example:

```text
Original:
"Search about latest LLM threats"

                ↓

Planner

                ↓

"What are the most recent and significant
security threats with large language models?"
```

So LangSmith allows you to inspect the planner's execution/output rather than treating the planner as a black box. Pasted markdown

---

# 6. Inspect the Document Reader

Next, the trace shows the **Document Reader**.

Its job is to retrieve relevant documents.

Conceptually:

```text
Planner
   ↓
Refined Question
   ↓
Document Reader
   ↓
Relevant Documents
```

The lecturer explicitly points out that the document reader gets the relevant documents. Pasted markdown

---

# 7. Inspect the Web Enricher

Then we have:

```text
Web Enricher
```

This agent retrieves information from the web.

The trace allows us to see this execution separately.

So we can distinguish:

```text
Internal knowledge/documents
          +
Web information
          ↓
       Synthesis
```

The lecturer explicitly demonstrates the Web Enricher retrieving information from the web. Pasted markdown

---

# 8. Inspect the Synthesizer

After retrieving information:

```text
Document Reader
       +
Web Enricher
       ↓
Synthesizer
```

The **Synthesizer** combines the information.

The lecturer describes it as synthesizing all the retrieved information. Pasted markdown

---

# 9. Inspect the Report Writer

Finally:

```text
Synthesizer
     ↓
Report Writer
     ↓
Final Report
```

The Report Writer creates the final response/report.

The trace lets us inspect this step as well. Pasted markdown

---

# 10. This is the major benefit of LangSmith UI

Without tracing, you might only see:

```text
Question
   ↓
Answer
```

With LangSmith:

```text
Question
   │
   ├── Planner
   │     └── refined question
   │
   ├── Document Reader
   │     └── retrieved documents
   │
   ├── Web Enricher
   │     └── web information
   │
   ├── Synthesizer
   │     └── combined information
   │
   └── Report Writer
         └── final answer
```

This is why the lecturer calls this **observability**.

---

# 11. LangSmith shows latency

The lecture also demonstrates execution timing.

For example, the trace can show something like:

```text
Total latency = 5.78 sec
```

The lecturer specifically points out that the trace displays the execution tree and the latency involved. Pasted markdown

This allows you to identify bottlenecks.

For example:

```text
Planner          → 0.8 sec
Document Reader  → 1.2 sec
Web Enricher     → 2.5 sec  ← bottleneck
Synthesizer      → 0.7 sec
Report Writer    → 0.6 sec
```

So LangSmith isn't just showing **what happened**; it helps you understand **how efficiently it happened**.

---

# 12. LangSmith shows cost

The lecturer also mentions that the trace displays the **cost involved**. Pasted markdown

So you can analyze:

```text
Execution
   ↓
Tokens
   ↓
Model usage
   ↓
Cost
```

This becomes especially useful when an agentic system calls multiple LLMs.

For example:

```text
Planner        → LLM call
Synthesizer    → LLM call
Report Writer  → LLM call
                 ↓
              Total Cost
```

---

# 13. Tree view

The lecture explicitly mentions the **tree** view.

The tree represents the hierarchical execution of the workflow.

Example:

```text
Root Trace
│
├── Planner
│
├── Document Reader
│
├── Web Enricher
│
├── Synthesizer
│
└── Report Writer
```

This is useful for understanding **which operations were executed and how they relate to one another**. Pasted markdown

---

# 14. Waterfall view

The lecture also demonstrates the **waterfall**.

The waterfall represents the execution over time.

Conceptually:

```text
Time →

Planner
████████

Document Reader
      █████████

Web Enricher
           █████████████

Synthesizer
                       ███████

Report Writer
                              █████
```

This makes it easier to understand:

- execution order
- duration of each operation
- slow components
- total latency
- sequential execution

The lecturer explicitly calls this the **entire trace / entire execution** and shows the waterfall representation. Pasted markdown

---

# 15. Inspecting hallucinations / problems

An important practical use shown in the lecture is debugging.

The lecturer observes a **hallucination** in the application's response.

He explains that the workflow is currently straightforward/non-reactive:

```text
Planner
   ↓
Document Reader
   ↓
Web Enricher
   ↓
Synthesizer
   ↓
Report Writer
```

The problem is that the planner doesn't dynamically decide whether document retrieval is actually necessary. Pasted markdown

So LangSmith helps you **observe the problematic execution path**.

---

# 16. The proposed improvement

The lecturer proposes converting the straightforward flow into a **ReAct-style agent flow**.

Instead of:

```text
Planner
   ↓
Read documents
   ↓
Web search
   ↓
Synthesize
   ↓
Report
```

the planner should make a decision:

```text
                 Planner
                    ↓
          Should I read documents?
              /            \
            YES             NO
             ↓               ↓
       Document Reader      End
             ↓
       Web Enricher
             ↓
        Synthesizer
             ↓
        Report Writer
```

The assignment at the end is explicitly to convert the straightforward agentic flow into a ReAct agent flow, where the planner decides whether document reading is required. Pasted markdown

---

# 17. LangGraph Studio vs LangSmith tracing

There is an important distinction in the lecture that you should keep straight.

The lecture uses **two related observability/development interfaces**.

### A. Trace UI

Used to inspect an actual execution:

```text
User Question
      ↓
Actual Run
      ↓
Trace
      ↓
Tree / Waterfall / Latency / Cost
```

For example, the lecturer asks:

> "What is LLM as a judge evaluation?"

and then examines the newly created trace. Pasted markdown

### B. LangGraph Studio

The lecture also creates a `langgraph.json` configuration so that the workflow can be executed/visualized in **Studio**.

The lecturer explains that `langgraph.json` is required to expose the workflow to Studio. Pasted markdown

Then:

```bash
langgraph dev
```

is used to launch the development environment.

The lecturer says this opens a new tab where the same workflow can be viewed. Pasted markdown

So don't confuse these two:

| Component | Main purpose |
|---|---|
| **Streamlit** | End-user application UI |
| **LangSmith tracing** | Observe/debug actual executions |
| **LangGraph Studio** | Develop/visualize/test the LangGraph workflow |
| **LangGraph** | Backend agentic workflow |

---

# 18. Complete procedure from the lecture

Here's the **step-by-step workflow you should remember for notes**:

### Step 1 — Build the LangGraph workflow

Create:

```text
Planner
Document Reader
Web Enricher
Synthesizer
Report Writer
```

and connect them into the graph.

---

### Step 2 — Create Streamlit application

Create:

```text
app.py
```

and import the required packages.

The lecture uses:

```python
UUID
Streamlit
dotenv
```

among other application dependencies. Pasted markdown

---

### Step 3 — Generate a session ID

Generate a unique session ID for each session/user.

```python
session_id = str(uuid.uuid4())
```

This changes when a new session starts. Pasted markdown

---

### Step 4 — Cache the graph

Because building the graph takes time, use Streamlit resource caching.

Conceptually:

```python
@st.cache_resource
def get_graph():
    return agent_graph.build_graph()
```

This prevents rebuilding the graph every time Streamlit reruns. Pasted markdown

---

### Step 5 — Create the Streamlit UI

Configure:

- page title
- sidebar
- session ID
- application information
- example questions
- trace endpoint

The sidebar also tells the user where they can inspect traces. Pasted markdown

---

### Step 6 — Maintain chat history

Use Streamlit session state/chat history so that previous messages remain visible.

This is mainly for the **application UI**, not the core LangSmith functionality. Pasted markdown

---

### Step 7 — Take user input

Use a chat input:

```text
Ask anything about LLM production
```

The user's question is passed to the LangGraph workflow. Pasted markdown

---

### Step 8 — Execute the graph

The workflow runs:

```text
Planner
   ↓
Document Reader
   ↓
Web Enricher
   ↓
Synthesizer
   ↓
Report Writer
```

---

### Step 9 — Open the trace UI

Open the trace endpoint/interface.

A new trace is generated for each execution.

---

### Step 10 — Inspect the trace

Look at:

```text
Tree
Waterfall
Latency
Cost
Individual agent execution
Inputs/outputs
Final response
```

The lecture demonstrates all of these aspects while inspecting the generated trace. Pasted markdown

---

### Step 11 — Debug the workflow

Use the trace to identify problems such as:

```text
Hallucination
Wrong agent execution
Unnecessary tool call
Slow node
High cost
Unexpected output
```

The lecture specifically uses the observed hallucination to identify a weakness in the current straightforward workflow. Pasted markdown

---

### Step 12 — Improve the agent

Convert:

```text
Straightforward workflow
```

into:

```text
Reactive / ReAct workflow
```

where the planner can decide dynamically whether a particular tool/document retrieval step is required. Pasted markdown

---

# 19. One-line mental model

If you want to remember the entire LangSmith portion of this lecture for interviews:

> **LangSmith is being used as the observability/debugging layer for the LangGraph application, allowing us to trace individual agent executions, inspect the execution tree and waterfall, and monitor latency and cost.**

And the overall relationship is:

```text
             ┌─────────────────┐
             │   Streamlit     │
             │  User Interface │
             └────────┬────────┘
                      │
                      ↓
             ┌─────────────────┐
             │   LangGraph     │
             │ Agent Workflow  │
             └────────┬────────┘
                      │
             execution / traces
                      │
                      ↓
             ┌─────────────────┐
             │    LangSmith   │
             │  Observability  │
             ├─────────────────┤
             │ • Traces        │
             │ • Tree          │
             │ • Waterfall     │
             │ • Latency       │
             │ • Cost          │
             │ • Debugging     │
             └─────────────────┘
```

**Important:** The transcript does **not** give the detailed LangSmith SDK setup/API code (for example, exact `LANGSMITH_API_KEY`, project/environment configuration, callbacks, etc.). So I would **not add those to your lecture notes as if they were demonstrated here**. What the lecture actually demonstrates is the **LangSmith tracing/observability workflow and UI**, while the `langgraph dev`/`langgraph.json` portion is specifically about **LangGraph Studio**.