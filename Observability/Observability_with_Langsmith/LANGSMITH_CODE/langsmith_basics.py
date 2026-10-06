#!/usr/bin/env python
# coding: utf-8

# In[2]:


print("all okay")


# In[1]:


import os, warnings
warnings.filterwarnings("ignore")
from dotenv import load_dotenv
load_dotenv()


# In[2]:


print("LANGSMITH_TRACING :", os.getenv("LANGSMITH_TRACING", "not set"))
print("LANGSMITH_API_KEY :", "✅" if os.getenv("LANGSMITH_API_KEY") else "❌  missing")
print("LANGSMITH_PROJECT :", os.getenv("LANGSMITH_PROJECT", "default"))
print("GROQ_API_KEY      :", "✅" if os.getenv("GROQ_API_KEY")      else "❌  missing")
print("GEMINI_API_KEY    :", "✅" if os.getenv("GEMINI_API_KEY")    else "❌  missing")


# ---
# ## Part 1 — Auto-Tracing, @traceable & Enriching Traces
# 
# ### How LangSmith tracing works
# 
# ```
# Your code                      LangSmith SDK              Dashboard
#   |
#   |-- set LANGSMITH_TRACING=true
#   |
#   |-- any LangChain/LangGraph call --> creates a Run --> appears in dashboard
#   |                                    records input, output, tokens, latency
#   |
#   |-- no extra code needed
# ```
# 
# **Key difference from Logfire:** LangSmith auto-traces every LangChain and LangGraph
# call by monkey-patching triggered by three env vars. No `with span():` blocks needed
# for standard LangChain calls. Custom Python functions need the `@traceable` decorator.
# 
# **What this Part covers:**
# - Experiment 1: See your first trace appear with zero code changes
# - Experiment 2: Use `@traceable` to trace your own Python functions
# - Experiment 3: Add tags, metadata, and custom run names for filtering

# ### 🧪 Experiment 1 — First Auto-Traced LangChain Call
# 
# Set the three environment variables and every LangChain call is automatically sent to
# LangSmith. No code changes whatsoever.
# 
# ```
# LANGSMITH_TRACING=true         ← master switch
# LANGSMITH_API_KEY=...          ← your LangSmith API key
# LANGSMITH_PROJECT=my-project   ← groups related traces (optional)
# ```
# 
# After running this cell: go to smith.langchain.com → your project → you'll see the run.

# In[6]:


from langchain_groq import ChatGroq

llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0.3)

# Plain llm.invoke() — no LCEL, no chain, no decorators.
# LangSmith intercepts this call automatically via the three env vars we set.
response = llm.invoke("What is a LangSmith Run? Answer in 2 sentences.")
print(response.content)


# ### 🧪 Experiment 2 — @traceable: Make Your Own Functions Visible in LangSmith
# 
# LangSmith auto-traces LangChain objects. For your own Python functions, use the `@traceable` decorator.
# 
# ```
# Without @traceable:   LangSmith sees only the LLM call — no context around it
# With @traceable:      LangSmith sees your full function as a parent Run,
#                       with the LLM call nested inside as a child Run
# ```
# 
# **`run_type` values:**
# | Value | When to use |
# |-------|------------|
# | `"llm"` | Function that calls a language model |
# | `"tool"` | Function that retrieves data, searches, or calls an API |
# | `"chain"` | Orchestrator function that calls other functions |

# In[7]:


import re
from langsmith import traceable


# ── Tool: keyword search over the real document ────────────────────────────
@traceable(run_type="tool", name="doc_keyword_search")
def search_document(query: str, top_k: int = 3) -> list:
    """Searches llm_production_guide.txt by keyword overlap. Visible as a Tool Run."""
    with open("data/llm_production_guide.txt", encoding="utf-8") as f:
        text = f.read()
    paragraphs = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 80]
    keywords   = set(re.findall(r"\b\w{4,}\b", query.lower()))
    ranked     = sorted(paragraphs,
                        key=lambda p: sum(1 for kw in keywords if kw in p.lower()),
                        reverse=True)
    return ranked[:top_k]


# In[8]:


# ── Chain: orchestrates search → LLM → answer ─────────────────────────────
@traceable(run_type="chain", name="doc_qa_pipeline")
def doc_qa(question: str) -> str:
    """Parent chain. LangSmith shows: doc_qa_pipeline → doc_keyword_search + ChatGroq."""
    sections = search_document(question)            # ← child Tool Run
    context  = "\n\n".join(sections)
    prompt   = f"Context:\n{context}\n\nQuestion: {question}\nAnswer concisely:"
    return llm.invoke(prompt).content               # ← child LLM Run


# In[9]:


answer = doc_qa("What are the main LLM security threats?")
print(f"Answer: {answer[:300]}...")


# ### 🧪 Experiment 3 — Enrich Traces: Tags, Metadata, run_name
# 
# Raw traces tell you *what* happened. Tags and metadata tell you *who*, *why*, and *in what context*.
# 
# Pass `langsmith_extra=` directly to any `llm.invoke()` or inside a `@traceable` function — no LCEL, no RunnableConfig needed.
# 
# | Field | Purpose | Example |
# |-------|---------|---------|
# | `tags` | String labels — filter in dashboard | `["production", "groq"]` |
# | `metadata` | Any key-value dict — visible in run detail | `{"user_id": "alice", "feature": "support-bot"}` |
# | `run_name` | Override the default run title | `"support-query-alice"` |
# 
# **Real production use:** filter `metadata.user_id = "alice"` to see all of one user's traces and sum their token costs.

# In[10]:


from langsmith import get_current_run_tree 

@traceable(run_type="chain", name="support-query")
def support_qa(question: str, user_id: str, session_id: str) -> str:
    run = get_current_run_tree()
    if run:
        run.metadata.update({
            "user_id":    user_id,
            "session_id": session_id,
            "feature":    "customer-support",
            "env":        "production",
        })
        run.tags = ["production", "support-bot", "groq"]
    return llm.invoke(question).content


# In[11]:


list_of_queriers = [
    ("priya",   "sess_001", "What is prompt injection and how do we prevent it?"),
    ("aditi",   "sess_002", "What are best practices for LLM output validation?"),
    ("sheetal", "sess_003", "How do we monitor LLM costs in production?"),
]


# In[12]:


# Run three different users — each trace is tagged for filtering
for user, session, q in list_of_queriers:
    answer = support_qa(q, user_id=user, session_id=session)
    print(f"[{user}] {answer[:150]}...\n")


# ### 🧪 Experiment 4 — Traced RAG over a Real Text File
# 
# Load `data/llm_production_guide.txt`, split into chunks, embed with **Google Gemini** (`gemini-embedding-2-preview`), build a FAISS index, then wrap the whole RAG function in `@traceable`.
# 
# LangSmith shows the trace as:
# ```
# production_guide_rag  (run_type=chain)
#   └── ChatGroq call    (run_type=llm)
#         input:  full prompt WITH retrieved chunks
#         output: answer
#         tokens: input + output counts
# ```
# 
# The retrieved chunks and `user_id` are stored as metadata on the run — searchable in the dashboard.

# In[13]:


import os
from langsmith import get_current_run_tree
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings


# LOAD

# In[14]:


# ── Load + split the real guide document ─────────────────────────────────
loader   = TextLoader("data/llm_production_guide.txt", encoding="utf-8")
raw_docs = loader.load()
print(f"Loaded: {len(raw_docs[0].page_content):,} characters")


# SPLIT

# In[15]:


splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=80)
chunks   = splitter.split_documents(raw_docs)
print(f"Chunks: {len(chunks)}  (avg {sum(len(c.page_content) for c in chunks)//len(chunks)} chars each)")


# VECTORIZE

# In[16]:


print("\nEmbedding chunks via Gemini API (gemini-embedding-2-preview)…")
embeddings  = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-2-preview",
    google_api_key=os.getenv("GEMINI_API_KEY")
)
vectorstore = FAISS.from_documents(chunks, embeddings)
retriever   = vectorstore.as_retriever(search_kwargs={"k": 3})
print("✅  FAISS index ready")


# custom TRACE

# In[17]:


# ── Traced RAG function — @traceable, no LCEL ────────────────────────────
@traceable(run_type="chain", name="production_guide_rag")
def rag(question: str, user_id: str = "anonymous") -> str:
    docs    = retriever.invoke(question)
    context = "\n\n".join(f"[chunk {i+1}] {d.page_content}" for i, d in enumerate(docs))
    prompt  = (
        f"Answer based ONLY on the context below.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {question}\n\nAnswer concisely:"
    )
    run = get_current_run_tree()
    if run:
        run.metadata.update({"user_id": user_id, "chunks_retrieved": len(docs)})
    return llm.invoke(prompt).content


# In[18]:


# ── Test with two questions ───────────────────────────────────────────────
for q, uid in [
    ("What are the main LLM security risks in production?", "student_01"),
    ("How should we evaluate LLM outputs for quality?",     "student_02"),
]:
    answer = rag(q, user_id=uid)
    print(f"\nQ: {q}")
    print(f"A: {answer[:250]}...")


# ### 🧪 Experiment 5 — Multi-Tool ReAct Agent (Local Docs + Web Search)
# 
# A ReAct agent with **two tools** — the agent decides which to call:
# 
# | Tool | When the agent uses it | Data source |
# |------|----------------------|-------------|
# | `search_local_docs` | LLM production, security, RAG, deployment topics | FAISS index from Exp 4 |
# | `google_search` | Current news, recent events, real-time info | Google Serper API (live web) |
# 
# **LangSmith auto-traces the entire LangGraph agent** — every reasoning step, every tool call, every response — with zero extra tracing code. Just the env vars set in setup.
# 
# ```
# LangSmith trace for "What are the latest AI safety regulations in 2025?":
# 
# langgraph  (agent graph run)
#   ├── ChatGroq  [LLM decides: use google_search]
#   ├── google_search  [Tool call: live web results]
#   └── ChatGroq  [LLM generates final answer]
# ```

# In[19]:


from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage, AIMessage
from langchain_community.utilities import GoogleSerperAPIWrapper


# setup google serper

# In[20]:


serper = GoogleSerperAPIWrapper()


# tool 
# 
# 1) retriver - search local docs 
# 2) Google search

# In[21]:


@tool
def search_local_docs(query: str) -> str:
    """
    Search the internal LLM production guide.

    IMPORTANT:
    - Use only once per question.
    - After receiving results, answer the user.
    - Do not call repeatedly.
    """

    docs = vectorstore.similarity_search(query, k=3)

    if not docs:
        return "No relevant documents found."

    response = "\n\n".join(
        f"[Chunk {i+1}]\n{doc.page_content[:700]}"
        for i, doc in enumerate(docs)
    )

    # Prevent huge context windows
    return response[:2500]


# In[22]:


@tool
def google_search(query: str) -> str:
    """
    Search the web for recent information.

    IMPORTANT:
    - Use only once per question.
    - After receiving results, answer the user.
    - Do not search again unless absolutely required.
    """

    try:
        result = serper.run(query)

        if not result:
            return "No search results found."

        return str(result)[:2500]

    except Exception as e:
        return f"Search failed: {str(e)}"


# REACT AGENT

# In[23]:


agent = create_agent(
    model=llm,
    tools = [search_local_docs , google_search],
    system_prompt=""" 
    
    You are a research assistant.

    You have two tools:

    1. search_local_docs
    - Use for RAG, security, evaluation, monitoring,
    prompt engineering, guardrails, deployment.

    2. google_search
    - Use for current events, news,
    regulations, recent AI developments.

    Rules:

    1. Call a tool ONLY if needed.
    2. Never call the same tool more than once.
    3. Maximum TWO total tool calls.
    4. After receiving tool results, provide the final answer.
    5. Do NOT continue searching if enough information exists.
    6. Do NOT loop.
    7. If one tool gives sufficient information,
    answer immediately.
    
    """
)


# runner 

# In[24]:


def run_agent(question: str):

    result = agent.invoke(
        {
            "messages": [
                HumanMessage(content=question)
            ]
        },
        config={
            "recursion_limit": 10
        }
    )

    tools_used = []

    for msg in result["messages"]:
        if isinstance(msg, ToolMessage):
            tools_used.append(msg.name)

    final_answer = ""

    for msg in reversed(result["messages"]):
        if isinstance(msg, AIMessage):
            final_answer = msg.content
            break

    return final_answer, list(dict.fromkeys(tools_used))


# In[25]:


queries = [
    (
        "What are LLM prompt injection attacks and how do we defend against them?",
        "search_local_docs"
    ),
    (
        "What are the latest AI regulations passed in 2025?",
        "google_search"
    ),
    (
        "How does RAG work and what are the latest open-source RAG frameworks in 2025?",
        "both"
    )
]


# run and evaluatue and observe

# In[26]:


for question, expected in queries:

    print("\n" + "=" * 80)
    print("QUESTION:")
    print(question)

    print("\nEXPECTED:")
    print(expected)

    answer, tools = run_agent(question)

    print("\nTOOLS USED:")
    print(tools)

    print("\nANSWER:")
    print(answer[:500])

print("\n✅ Completed successfully")


# In[ ]:




