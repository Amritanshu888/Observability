# AI Observability — Frameworks & Tools

## 1. Recap: What We Covered in the Previous Video

Before introducing the tools, the instructor briefly recaps the previous discussion on **observability**.

Observability in GenAI applications was discussed through five important pillars:

### The 5 Pillars of Observability

| Pillar | What it helps answer |
|---|---|
| **Logging** | What happened? |
| **Tracing** | How did it happen? |
| **Metrics** | How is the system performing? |
| **User Feedback** | What do users think about the output? |
| **Evaluation Signals** | How good/safe/relevant is the AI output? |

These pillars collectively help us understand the **internal behavior and performance of an AI application**.

The previous lecture also covered:

- Types of observability data
- Observability data flow
- Common observability use cases
- Popular observability tools/platforms
- Why observability is important for enterprise-grade AI applications

Now the focus shifts from **what observability is** to:

> **Which frameworks and platforms can we actually use to implement observability?**

---

# 2. Observability Frameworks/Platforms Covered in the Bootcamp

The instructor mentions several platforms, but the bootcamp will primarily focus on **two important platforms**:

1. **LangSmith**
2. **Pydantic Logfire**

Other platforms such as:

- Grafana
- Helicone

are also mentioned, but they are not the primary platforms selected for the bootcamp.

---

# 3. LangSmith

## What is LangSmith?

**LangSmith** is described as a platform for **agent engineering**.

It provides capabilities around:

- Building agents
- Observing agents
- Evaluating agents
- Deploying agents
- Understanding agent behavior
- Improving agent performance

It can therefore be used throughout the lifecycle of an AI/agentic application.

### Core idea

> **LangSmith helps you understand, evaluate, and improve what your AI agents are doing internally.**

---

# 4. Relationship Between LangChain and LangSmith

This is an important point from the lecture.

If you have worked with **LangChain**, you may already know that the LangChain ecosystem provides frameworks for building:

- AI applications
- Agentic AI applications
- AI agents
- Workflows

Examples mentioned include:

- **LangChain**
- **LangGraph**

Within the LangChain ecosystem, there is also a platform/product called:

> **LangSmith**

So conceptually:

```text
LangChain Ecosystem
        │
        ├── LangChain
        ├── LangGraph
        └── LangSmith
              │
              ├── Observability
              ├── Evaluation
              ├── Deployment
              └── Agent monitoring
```

### Important distinction

LangChain/LangGraph are primarily associated with **building AI applications and agentic workflows**, whereas LangSmith provides capabilities to **observe, evaluate, deploy, and improve those applications/agents**.

---

# 5. What Can You Do with LangSmith?

According to the lecture, LangSmith provides several capabilities.

### 1. Deploy applications

You can use LangSmith for deploying your applications.

### 2. Implement observability

You can observe your AI application and understand:

> **What exactly are my agents doing internally?**

For example, you can inspect:

```text
User Request
     ↓
Agent
     ↓
LLM Call
     ↓
Tool Call
     ↓
Database/API
     ↓
LLM Response
     ↓
Final Answer
```

LangSmith can provide visibility into this process.

---

### 3. Trace agent behavior

You can get a detailed picture of how an agent executes a task.

This is particularly useful for **agentic AI applications**, where a single user request can trigger multiple internal operations.

For example:

```text
User
 ↓
Agent
 ↓
LLM
 ↓
Tool Selection
 ↓
API Call
 ↓
LLM
 ↓
Final Response
```

Observability allows you to understand each of these steps.

---

### 4. Evaluation

LangSmith can also be used for **evaluation**.

The lecture specifically mentions being able to:

- Evaluate agent performance
- Score agent behavior
- Understand feedback
- Identify hallucinations
- Improve performance

This connects directly to the **evaluation signals** pillar discussed previously.

---

### 5. Improve Agent Performance

Observability isn't only about finding errors.

The collected information can also be used for **optimization**.

For example, you can analyze:

- How the LLM is performing
- Where the agent is failing
- Where hallucinations occur
- How users are responding
- How the workflow can be optimized

Therefore:

```text
Observe
   ↓
Evaluate
   ↓
Identify Problems
   ↓
Optimize
   ↓
Improve Agent
```

---

# 6. LangSmith Dashboard

The instructor highlights the dashboard as one of the useful aspects of LangSmith.

The dashboard provides visibility into **agent behavior and application execution**.

You can use it to understand things such as:

- Agent behavior
- LLM performance
- Hallucination-related scores
- Feedback scores
- Execution traces
- Application performance
- Optimization opportunities

The key idea is:

> **Instead of treating the AI application as a black box, LangSmith gives visibility into what is happening internally.**

---

# 7. LangSmith SDK Support

An important technical point mentioned in the lecture is that LangSmith supports multiple SDKs.

The instructor specifically mentions:

- **Python**
- **TypeScript**
- **Go**
- **Java**

This makes LangSmith usable across different technology stacks.

Conceptually:

```text
                 LangSmith
                    │
       ┌────────────┼────────────┐
       ↓            ↓            ↓
    Python      TypeScript       Go
                    │
                    ↓
                   Java
```

So you aren't restricted to a single programming language.

---

# 8. Practical/Industry Experience with LangSmith

The instructor mentions that they have personally used LangSmith extensively, including in their company.

The use case mentioned is essentially:

> Understanding how an AI agent is actually working internally.

This highlights an important industry perspective:

Building an agent is only one part of developing an enterprise AI system.

You also need to understand:

- What the agent is doing
- Why it is doing it
- How well it is performing
- Where it is failing
- How it can be optimized

This is where observability platforms become important.

---

# 9. Hallucination and Feedback Monitoring

The lecture specifically mentions being able to obtain things such as:

### Hallucination Score

You can monitor signals related to whether the model is hallucinating.

For example:

```text
User Query
    ↓
LLM
    ↓
Generated Answer
    ↓
Evaluation
    ↓
Hallucination / Quality Signal
```

### Feedback Score

You can also examine feedback related to the AI output.

This can help determine:

> Is the AI application actually producing useful responses?

This connects directly to the previous lecture's:

**User Feedback + Evaluation Signals**

pillars.

---

# 10. Pydantic Logfire

The second major platform selected for the bootcamp is:

> **Pydantic Logfire**

The instructor describes it as:

> **An AI observability platform for LLMs, applications, and AI agents.**

It provides an observability dashboard for AI applications.

---

# 11. What is Pydantic Logfire Used For?

According to the lecture, Logfire provides visibility into different components of an AI application.

The instructor emphasizes that many operations can be tracked.

For example:

```text
Application
    │
    ├── Guardrails
    │
    ├── LLM Gateway
    │
    ├── LLM Calls
    │
    ├── API Requests
    │
    ├── Database Operations
    │
    └── Other Application Operations
```

These operations can be tracked through the observability platform.

---

# 12. Logfire Dashboard

One of the features highlighted is the **dashboard**.

The dashboard allows developers to inspect what is happening inside their applications.

The instructor also mentions that you can:

- Write queries
- Get responses
- Connect to multiple databases
- Track application operations

So Logfire isn't presented simply as a place to store logs.

It can provide a broader observability experience across an AI application.

---

# 13. Tracking Different AI Operations

One of the important statements in the lecture is that operations ranging from:

> **Guardrails → LLM gateways → LLM calls → API requests**

can be tracked.

This is particularly relevant to the architecture of production AI systems.

For example:

```text
User
 ↓
AI Application
 ↓
Guardrails
 ↓
LLM Gateway
 ↓
LLM
 ↓
Tool/API
 ↓
Database
 ↓
Response
```

Observability should ideally cover these different stages rather than only monitoring the final response.

---

# 14. Logfire and Evaluation

Another important point is that **evaluation capabilities are also integrated** into the broader Pydantic ecosystem.

The instructor specifically highlights examples involving:

> **Pydantic AI + Logfire**

and mentions that evaluation is also part of the features that will be discussed later in the bootcamp.

This reinforces an important idea:

```text
Observability
      +
Evaluation
      ↓
Better AI Systems
```

Observability tells you **what happened**, while evaluation helps determine **how good the result was**.

---

# 15. Other Observability Platforms

The instructor also mentions several other platforms.

### Grafana

A popular observability and monitoring platform.

### Helicone

Another platform used for observing LLM applications.

These are acknowledged as good platforms, but they are **not the primary platforms selected for this bootcamp**.

---

# 16. Why Were LangSmith and Logfire Selected?

The instructor explains that there are many observability platforms available.

However, the bootcamp wants to focus on platforms that provide a broad range of the required capabilities.

The goal is essentially:

> **Cover as many required observability features as possible using the selected platforms.**

Therefore, instead of teaching every observability platform individually, the course focuses on:

```text
             Observability
                  │
        ┌─────────┴─────────┐
        ↓                   ↓
    LangSmith           Logfire
        │                   │
        └─────────┬─────────┘
                  ↓
      Enterprise AI Observability
```

---

# 17. Future Tools and Updates

The instructor also makes an important point about the rapidly changing AI ecosystem.

New observability platforms may appear in the future.

Therefore, the course may:

- Cover new platforms
- Update course material
- Add new frameworks
- Introduce new capabilities

as the ecosystem evolves.

This is especially relevant for GenAI because tools and frameworks are changing rapidly.

---

# 18. LangSmith vs Pydantic Logfire — Lecture-Based Comparison

| Feature | LangSmith | Pydantic Logfire |
|---|---|---|
| AI observability | ✅ | ✅ |
| Agent observability | ✅ | ✅ |
| Agent evaluation | ✅ | Mentioned |
| Agent performance analysis | ✅ | ✅ |
| Dashboard | ✅ | ✅ |
| Tracing/visibility | ✅ | ✅ |
| LLM monitoring | ✅ | ✅ |
| API/application monitoring | ✅ | ✅ |
| Query capabilities | — | ✅ Mentioned |
| Database connectivity | — | ✅ Mentioned |
| SDK support | Python, TypeScript, Go, Java | — |
| Bootcamp focus | ✅ | ✅ |

**Note:** The table reflects what the lecturer explicitly discusses in this transcript; it is not intended as a complete product feature comparison.

---

# 19. Where These Tools Fit in a Production AI Architecture

The previous lectures discussed production AI systems containing components such as:

```text
                 User
                   │
                   ↓
              AI Application
                   │
          ┌────────┼────────┐
          ↓        ↓        ↓
      Guardrails  Agent   Gateway
                   │
                   ↓
                  LLM
                   │
          ┌────────┴────────┐
          ↓                 ↓
      Vector DB          Tools/APIs
          │                 │
          └────────┬────────┘
                   ↓
              Final Answer
```

Observability platforms such as **LangSmith** and **Pydantic Logfire** provide visibility across these components.

Conceptually:

```text
                  Observability
                       │
          ┌────────────┴────────────┐
          ↓                         ↓
      LangSmith                 Logfire
          │                         │
          └────────────┬────────────┘
                       ↓
        Monitor Production AI System
```

---

# 20. Important Connection to Previous Lecture

This lecture should not be studied independently from the previous observability lecture.

The previous lecture established:

### What should we observe?

```text
Logging
Tracing
Metrics
User Feedback
Evaluation Signals
```

This lecture establishes:

### What can we use to implement observability?

```text
LangSmith
Pydantic Logfire
```

with other platforms such as:

```text
Grafana
Helicone
```

also available in the ecosystem.

So the progression is:

```text
WHAT?
  ↓
Observability
  ↓
WHY?
  ↓
Debugging + Performance + Quality + Cost + Trust
  ↓
WHAT DO WE OBSERVE?
  ↓
Logging + Tracing + Metrics + Feedback + Evaluation
  ↓
HOW DO WE IMPLEMENT IT?
  ↓
LangSmith + Pydantic Logfire
```

---

# 21. Key Terminology

### LangSmith
A platform for **agent engineering**, providing capabilities for building, observing, evaluating, deploying, and improving agents.

### Pydantic Logfire
An **AI observability platform for LLMs, applications, and AI agents**.

### Agent Engineering
The process of building, observing, evaluating, deploying, and improving AI agents.

### Agent Observability
The ability to see and understand what an AI agent is doing internally during execution.

### Evaluation
Measuring the quality/performance of an AI system using evaluation signals.

### Hallucination Score
A signal used to understand the extent to which an AI system produces unsupported or incorrect information.

### Feedback Score
A signal derived from feedback that helps understand the quality/usefulness of an AI system's responses.

---

# 22. Interview Perspective

### Q: What tools can be used for observability in GenAI applications?

A good answer:

> **Popular observability platforms for GenAI applications include LangSmith, Pydantic Logfire, Grafana, and Helicone. In this bootcamp, LangSmith and Pydantic Logfire are the primary platforms used to implement observability.**

---

### Q: What is LangSmith?

> **LangSmith is a platform for agent engineering that provides capabilities for observing, evaluating, deploying, and improving AI agents and agentic applications. It provides visibility into agent behavior and supports multiple SDKs including Python, TypeScript, Go, and Java.**

---

### Q: What is Pydantic Logfire?

> **Pydantic Logfire is an AI observability platform for LLMs, applications, and AI agents. It provides dashboards and monitoring capabilities for operations such as LLM calls, API requests, guardrails, and other application-level operations.**

---

### Q: Why is observability important for AI agents?

Because an AI agent isn't simply:

```text
Input → Output
```

It may perform multiple internal operations:

```text
Input
 ↓
Agent
 ↓
LLM
 ↓
Tool Selection
 ↓
API
 ↓
Database
 ↓
LLM
 ↓
Final Response
```

Without observability, it becomes difficult to understand **where and why something went wrong**.

---

# 23. Most Important Takeaways

### 1. LangSmith is the first major platform
Used for:

- Agent engineering
- Observability
- Evaluation
- Deployment
- Performance improvement

### 2. Pydantic Logfire is the second major platform
Used for:

- LLM observability
- Application observability
- Agent observability
- Tracking calls/operations
- Dashboard-based monitoring
- Querying/DB connectivity

### 3. Other platforms exist

Examples:

- Grafana
- Helicone

But the bootcamp primarily focuses on **LangSmith and Pydantic Logfire**.

### 4. Observability and evaluation are connected

Observability helps you understand:

> **What happened?**

Evaluation helps determine:

> **How good was it?**

Together they enable continuous improvement.

### 5. Production AI requires visibility across the entire pipeline

Not just the final LLM response.

You should ideally be able to observe:

```text
User
 ↓
Application
 ↓
Guardrails
 ↓
Agent
 ↓
LLM Gateway
 ↓
LLM
 ↓
Tools/APIs
 ↓
Database/Vector DB
 ↓
Response
```

---

## 🧠 Easy Memory Trick

Remember:

> **Previous lecture = WHAT to observe**  
> **This lecture = WHICH TOOLS to use**

### WHAT?

**L-T-M-F-E**

- **L** → Logging
- **T** → Tracing
- **M** → Metrics
- **F** → Feedback
- **E** → Evaluation

### WHICH TOOLS?

**L + P**

- **L** → LangSmith
- **P** → Pydantic Logfire

So:

> **LTMFE tells you what observability consists of; LangSmith and Logfire help you implement it.**
