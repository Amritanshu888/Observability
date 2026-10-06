#!/usr/bin/env python
# coding: utf-8

# # 🔭 Pydantic Logfire — Production LLM Observability
# 
# **Instructor: Divesh | Production-Grade LLM Engineering**
# 
# ---
# 
# ## What You'll Build
# 
# In this notebook we go from **zero observability** to a **fully traced RAG pipeline** step by step.
# 
# | Part | What We Cover |
# |------|--------------|
# | **Part 1** | Why Logfire, first spans, structured logging |
# | **Part 2** | Auto-instrument Groq + Gemini — tokens, latency, model name for free |
# | **Part 3** | Full RAG tracing — embed → retrieve → generate waterfall |
# 
# **Stack:**
# - `Logfire` — Python-native observability (built on OpenTelemetry)
# - `Groq (llama-3.3-70b)` + `Gemini (gemini-2.5-flash-lite)` — two providers, one dashboard
# - `FAISS` + `Gemini text-embedding (gemini-embedding-2-preview)` — API-based vector search
# - `LangChain` + `LangGraph` — RAG orchestration and ReAct agent
# 
# > 📌 **Keep your Logfire dashboard open in a browser tab** — you'll see events appear in real time as each cell runs.

# SETUP LOGFIRE

# In[1]:


import os, time, warnings
warnings.filterwarnings("ignore")


import logfire 
from dotenv import load_dotenv

load_dotenv()


# Verify keys
print("LOGFIRE_TOKEN  :", "✅" if os.getenv("LOGFIRE_TOKEN")  else "❌  missing")
print("GROQ_API_KEY   :", "✅" if os.getenv("GROQ_API_KEY")   else "❌  missing")
print("GEMINI_API_KEY :", "✅" if os.getenv("GEMINI_API_KEY") else "❌  missing")


# ---
# ## 🧱 Part 1 — Why Logfire & First Traces
# 
# The problem with `print()` in production:
# 
# | `print()` | `logfire` |
# |-----------|-----------|
# | Plain string, unsearchable | Structured key-value fields, fully searchable |
# | No timestamp or duration | Automatic timestamps, span duration |
# | Lost in terminal noise | Real-time dashboard with filters and queries |
# | Nothing in production | Persisted traces, alerting, cost analytics |
# 
# Logfire is built on **OpenTelemetry** — the industry standard. Every trace you write here is portable.

# ### 🧪 Experiment 1 — Configure Logfire & First Manual Span
# 
# **Three primitives to learn:**
# 
# 1. `logfire.configure()` — one-time setup, connects to your project dashboard
# 2. `logfire.info(msg, **attrs)` — a structured log event (NOT a string, it's a searchable record)
# 3. `with logfire.span("name", **attrs):` — a *timed block* with a name and attributes
# 
# After running this cell → switch to your **Logfire dashboard** and watch these events appear.

# In[3]:


import logfire

logfire.configure()
logfire.info('Hello, {place}!', place='UDEMY')


# In[4]:


logfire.configure(
    token=os.getenv("LOGFIRE_TOKEN"),
    service_name="llm-observability-course"
)


# SIMPLE INFO

# In[5]:


logfire.info("notebook_started",
            part="PART 1 - BASICS",
            instructer = "Divesh",
            tool = "Pydantic Logfire"
            )


# TRACE

# In[6]:


with logfire.span("data_processing_simulation", dataset="llm_course", rows=1000):
    logfire.info("step_started", step=1, action="loading data")
    time.sleep(0.3)

    logfire.info("step_started", step=2, action="transforming", columns=12)
    time.sleep(0.2)

    logfire.info("step_started", step=3, action="saving results", output="/tmp/out.csv")


# ### 🧪 Experiment 2 — Structured Logging with Pydantic Models
# 
# The *"Pydantic"* in Pydantic Logfire: when you log a Pydantic model, Logfire **expands every field** into a searchable attribute automatically.
# 
# In a real LLM app you log request/response objects hundreds of times per minute. With string logging you get `"{'user_id': 'alice', ...}"` — unsearchable. With Logfire you get filterable columns.

# In[7]:


from pydantic import BaseModel
from typing import Optional

# MOCK DATA nOT REAL DATA

class LLMRequest(BaseModel):
    user_id: str
    session_id: str
    query: str
    model: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None


class LLMResponse(BaseModel):
    answer: str
    input_tokens: int
    output_tokens: int
    latency_ms: float
    model_used: str    



# PASS DATA

# In[8]:


# ── Simulate logging a real LLM request/response ──────────────────────────
request = LLMRequest(
    user_id="priya",
    session_id="sess_abc123",
    query="What is Retrieval-Augmented Generation?",
    model="llama-3.3-70b-versatile",
    max_tokens=500
)

with logfire.span("llm_CALL",
                  user_id = request.user_id,
                  session_id = request.session_id,
                  model_used = request.model):
    logfire.info("request_received" , **request.model_dump())
    
    time.sleep(0.1)

    response = LLMResponse(
        answer="RAG is a technique that retrieves relevant documents...",
        input_tokens=18,
        output_tokens=120,
        latency_ms=342.5,
        model_used="llama-3.3-70b-versatile"
    )
    logfire.info("response_sent", **response.model_dump())


print(response)


# ---
# ## ⚡ Part 2 — Auto-Instrumentation of LLM Calls
# 
# In Part 1 you wrote spans manually. Now let Logfire do it **automatically**.
# 
# `logfire.instrument_openai()` patches the OpenAI Python SDK.
# Since **Groq** and **Gemini** both expose an OpenAI-compatible REST API, the same single line instruments all of them.
# 
# Every LLM call then automatically records:
# - Model name (`llama-3.3-70b-versatile`, `gemini-2.5-flash-lite`, …)
# - Input + output token counts
# - Wall-clock latency
# - Full prompt text and full response text
# 
# You write **zero** extra logging code. It just appears in the dashboard.

# ### 🧪 Experiment 3 — Instrument Groq (llama-3.3-70b)
# 
# We use `ChatOpenAI` from LangChain pointed at Groq's OpenAI-compatible endpoint.
# `logfire.instrument_openai()` patches the underlying SDK — Groq calls appear in traces automatically.
# 
# ```
# Your code  →  ChatOpenAI(base_url="https://api.groq.com/openai/v1")
#                           ↓
#               [logfire.instrument_openai() intercepts here]
#                           ↓
#               Groq API  →  response
# ```

# In[9]:


from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage


logfire.instrument_openai()

llm_groq = ChatOpenAI(
    base_url= "https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY"),
    model = "llama-3.3-70b-versatile",
    temperature=0.3
)

# Make a call — watch the trace appear in the dashboard automatically
print("Calling Groq (llama-3.3-70b)…")
response = llm_groq.invoke([
    HumanMessage(content="Explain what an observability 'span' is, in exactly 2 sentences.")
])

print(response.content)


# ### 🧪 Experiment 4 — Instrument Gemini (gemini-2.5-flash-lite)
# 
# Gemini now exposes an OpenAI-compatible endpoint too:
# `https://generativelanguage.googleapis.com/v1beta/openai/`
# 
# Same `ChatOpenAI` setup — just a different `base_url` and model name.
# `logfire.instrument_openai()` was already called — no need to call it again.
# 
# After this cell, your dashboard will show traces from **two different model names** in the same project.

# In[10]:


# Gemini's OpenAI-compatible endpoint (no extra setup needed)
llm_gemini = ChatOpenAI(
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=os.getenv("GEMINI_API_KEY"),
    model="gemini-2.5-flash-lite",
    temperature=0.3
)


print("Calling Gemini (gemini-2.5-flash-lite)…")
try:
    response = llm_gemini.invoke([
        HumanMessage(content="Explain what an observability 'trace' is, in exactly 2 sentences.")
    ])
    print(f"\n🔵 Gemini Response:\n{response.content}")
except Exception as e:
    print(f"⚠️  Gemini call failed: {e}")
    print("    Check your GEMINI_API_KEY in .env")


# ### 🧪 Experiment 5 — Side-by-Side: Groq vs Gemini in One Trace Waterfall
# 
# Wrap both calls in a **parent span** — the dashboard shows them as a waterfall:
# 
# ```
# model_comparison  ←── parent span (total wall time)
#   ├── groq_call   ←── child span  (latency: Xms, tokens: N)
#   └── gemini_call ←── child span  (latency: Xms, tokens: N)
# ```
# 
# This is exactly how you run **A/B model tests in production** — one trace per comparison, all searchable.

# In[11]:


query = "What is the difference between RAG and fine-tuning? Give 3 bullet points."

with logfire.span("model_comparison", query=query, num_models=2):

    # ── Groq ─────────────────────────────────────────────────────────────
    with logfire.span("groq_call", model="llama-3.3-70b-versatile", provider="groq"):
        t0 = time.time()
        r_groq = llm_groq.invoke([HumanMessage(content=query)])
        groq_ms = round((time.time() - t0) * 1000, 1)
        logfire.info("groq_done", latency_ms=groq_ms, answer_len=len(r_groq.content))

    # ── Gemini ────────────────────────────────────────────────────────────
    with logfire.span("gemini_call", model="gemini-2.5-flash-lite", provider="google"):
        t0 = time.time()
        try:
            r_gemini = llm_gemini.invoke([HumanMessage(content=query)])
            gemini_ms = round((time.time() - t0) * 1000, 1)
            logfire.info("gemini_done", latency_ms=gemini_ms, answer_len=len(r_gemini.content))
            gemini_answer = r_gemini.content
        except Exception as e:
            logfire.warning("gemini_failed", error=str(e))
            gemini_ms = 0
            gemini_answer = f"[Error: {e}]"

# ── Print results ─────────────────────────────────────────────────────────
print(f"🟢 Groq ({groq_ms}ms):\n{r_groq.content}")
print(f"\n🔵 Gemini ({gemini_ms}ms):\n{gemini_answer}")


# ---
# ## 📚 Part 3 — RAG Pipeline Tracing
# 
# A RAG pipeline has **3 stages**, each taking time and each capable of failing:
# 
# ```
# User Query
#     │
#     ▼
# [Embed Query]        ← Gemini text-embedding API call
#     │
#     ▼
# [Retrieve Docs]      ← FAISS similarity search (in-memory)
#     │
#     ▼
# [Generate Answer]    ← LLM API call (Groq llama-3.3-70b)
#     │
#     ▼
# Response
# ```
# 
# Without observability: *"It's slow"* — but which stage? The embedding? The retrieval? The LLM?
# With Logfire: you see **exactly** which stage takes how long and what data flows through each one.
# 
# **Stack:**
# - Embeddings: `gemini-embedding-2-preview` via Gemini API — no local model, reuses your existing key
# - Vector store: `FAISS` — in-memory, no server needed
# - LLM: Groq `llama-3.3-70b-versatile`

# ### 🧪 Experiment 6 — Traced RAG Pipeline
# 
# Load documents from `documents.json`, embed them with Gemini, build a FAISS index, and run a traced RAG pipeline.
# 
# Tracing shows the two things that matter:
# - **Which documents were retrieved** (relevance check without opening the code)
# - **LLM call** — model, tokens, latency, full prompt+response (auto-captured by `instrument_openai`)

# In[12]:


import json
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document


# ── Load knowledge base ────────────────────────────────────────────────────
with open("documents.json") as f:
    raw_docs = json.load(f)
    
# CONVERT THE DOCS IN LANGCHAIN COMPATIPBLE DOCUMENTS

DOCS = [
    Document(page_content=d["content"], metadata={"topic": d["topic"], "source": d["source"]})
    for d in raw_docs
]
print(f"Loaded {len(DOCS)} documents: {[d.metadata['topic'] for d in DOCS]}")


# In[13]:


DOCS


# In[14]:


# ── Embeddings + FAISS index ───────────────────────────────────────────────
embeddings  = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-2-preview",
    google_api_key=os.getenv("GEMINI_API_KEY")
)

vectorstore = FAISS.from_documents(DOCS, embeddings)
retriever   = vectorstore.as_retriever(search_kwargs={"k": 2})
print("✅  FAISS index ready")



# DATA INGESTION DONE

# DATA RETRIEVAL PIPELINE

# In[15]:


# ── RAG with tracing ───────────────────────────────────────────────────────
def rag(question: str, user_id: str = "anonymous") -> str:
    with logfire.span("rag_pipeline", question=question, user_id=user_id):
        docs = retriever.invoke(question)   # search similar vectors 
        logfire.info("docs_retrieved",
                     topics=[d.metadata["topic"] for d in docs],
                     num_docs=len(docs))
        context = "\n\n".join(
            f"[{d.metadata['topic']}] {d.page_content}" for d in docs
        )
        prompt = (
            f"Answer the question based only on the context below.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {question}\n\nAnswer concisely:"
        )
        return llm_groq.invoke(prompt).content


# In[16]:


answer = rag("How does a Rag reduce hallucination" , user_id="student1")
print(f"\nA: {answer}")


# REACT AGENT

# ### 🧪 Experiment 7 — LangGraph ReAct Agent with Retriever as a Tool
# 
# A fixed RAG chain always retrieves. An agent decides *when* to retrieve.
# 
# The retriever is a plain Python function decorated with `@tool` — the agent calls it only when the question needs knowledge-base lookup.
# 
# ```
# agent_run  (logfire span)
#   ├── LLM decides: call tool or answer directly?
#   ├── search_knowledge_base()  ← only if needed
#   └── LLM generates final answer
# ```

# In[17]:


from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage, AIMessage


# In[18]:


# ── Retriever as a plain Python tool ──────────────────────────────────────
@tool
def search_knowledge_base(query: str) -> str:
    """Search the knowledge base for LLM production topics: RAG, guardrails,
    gateways, observability, evaluations, and fine-tuning."""
    docs = vectorstore.similarity_search(query, k=2)
    return "\n\n".join(
        f"[{d.metadata['topic']}] {d.page_content}" for d in docs
    )


# In[19]:


agent = create_agent(
    model=llm_groq,
    tools=[search_knowledge_base],
    system_prompt=(
        "You are a helpful assistant. Use search_knowledge_base for any question "
        "about LLM production topics. Answer directly for general knowledge questions."
    )
)


# In[20]:


# ── Traced agent runner ────────────────────────────────────────────────────
def run_agent(question: str, user_id: str = "anonymous"):
    with logfire.span("agent_run", question=question, user_id=user_id):
        result = agent.invoke({"messages": [HumanMessage(content=question)]})

        # Last message may be a ToolMessage or an AIMessage with empty content
        # — iterate backwards to find the last AIMessage with actual text
        last_ai = next(
            (m for m in reversed(result["messages"]) if isinstance(m, AIMessage)),
            None
        )
        answer    = last_ai.text if last_ai else ""
        used_tool = any(isinstance(m, ToolMessage) for m in result["messages"])

        logfire.info("agent_done", used_tool=used_tool, answer_length=len(answer))
        return answer, used_tool


# In[21]:


# ── Test ───────────────────────────────────────────────────────────────────
queries = [
    ("What is LLM observability and which tools provide it?", "priya"),
    ("How do LLM guardrails work?",  "bhavesh"),
    ("What is the capital of France?", "kunal"),
]


# In[22]:


for q, uid in queries:
    print(f"{'='*55}")
    answer, used_tool = run_agent(q, user_id=uid)
    print(f"Q: {q}")
    print(f"Tool used: {used_tool}  {'← retrieved from KB' if used_tool else '← answered directly'}")
    print(f"A: {answer[:300]}")


# In[ ]:




