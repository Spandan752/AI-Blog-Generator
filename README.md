# ✍️ AI Blog Generator

> A production-deployed agentic AI system that generates high-quality blog posts through a self-evaluating LangGraph pipeline — not a simple LLM wrapper.

[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agentic%20Pipeline-orange)](https://langchain-ai.github.io/langgraph/)
[![Groq](https://img.shields.io/badge/Groq-LLaMA%203.1-red)](https://groq.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-Live%20Demo-FF4B4B?logo=streamlit)](https://streamlit.io)
[![Render](https://img.shields.io/badge/Render-API%20Deployed-46E3B7?logo=render)](https://render.com)
[![LangSmith](https://img.shields.io/badge/LangSmith-Tracing-blue)](https://smith.langchain.com)

🔗 **[Live Demo →](https://ai-blog-generator-sp.streamlit.app/)** &nbsp;|&nbsp; 📖 **[API Docs →](https://ai-blog-generator-api-favc.onrender.com/docs)**

---

## 📌 What This Project Demonstrates

This project goes beyond calling an LLM and returning a response. It showcases:

- Designing a **multi-node agentic graph** with LangGraph including conditional edges and revision cycles
- Implementing a **self-evaluation loop** where the graph scores its own output and regenerates if quality is insufficient
- Building a **streaming REST API** with FastAPI that pushes real-time node progress to the client
- **Separating concerns** across a deployed FastAPI backend (Render) and a Streamlit frontend (Streamlit Cloud)
- **Tone-aware generation** that injects writing style instructions at every stage of the pipeline

---

## 🏗️ System Architecture

```
User Request (topic + tone + language)
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend (Render)                      │
│                                                                 │
│   POST /blogs          POST /blogs/stream                       │
│   (full response)      (SSE node-by-node events)               │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                  LangGraph Agentic Pipeline                      │
│                                                                 │
│  ┌──────────────┐   ┌──────────────────┐   ┌────────────────┐  │
│  │title_creation│──►│outline_generation│──►│content_generat.│  │
│  └──────────────┘   └──────────────────┘   └───────┬────────┘  │
│                                                     │           │
│                                                     ▼           │
│                                           ┌──────────────────┐  │
│                          ┌────revise──────│  quality_check   │  │
│                          │                └────────┬─────────┘  │
│                          │                         │ approve    │
│                          ▼                         ▼            │
│                  content_generation        ┌──────────────┐     │
│                  (with feedback)           │    route     │     │
│                                            └──────┬───────┘     │
│                                      ┌────────────┼───────────┐ │
│                                      ▼            ▼           ▼ │
│                               hindi_trans  marathi_trans  french │
│                                      └────────────┴───────────┘ │
│                                                   │             │
│                                                  END            │
└─────────────────────────────────────────────────────────────────┘
```

### The Quality Check Loop — Why This Matters

LangGraph supports **cycles** in the graph, which standard LLM chains (LCEL) do not. The `quality_check` node scores the blog 0–10 and provides actionable feedback. If the score is below 7, the graph routes back to `content_generation` with the feedback injected into the prompt, forcing the LLM to improve on its previous attempt. This loops up to 3 times before accepting the best result — making this an **agentic** system, not just a pipeline.

---

## 🚀 Graph Flows

### Topic Graph (English)
```
START → title_creation → outline_generation → content_generation
              → quality_check ──(approve)──► END
                     │
                     └──(revise)──► content_generation (with feedback)
```

### Language Graph (with Translation)
```
START → title_creation → outline_generation → content_generation
              → quality_check ──(approve)──► route
                     │                          │
                     └──(revise)──► content   hindi / marathi / french → END
```

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **LLM** | Groq LLaMA 3.1 8B Instant | Ultra-fast inference for all generation nodes |
| **Agentic Framework** | LangGraph (StateGraph) | Multi-node graph with conditional edges and cycles |
| **State Management** | TypedDict + Pydantic | Typed state flowing through every graph node |
| **API** | FastAPI + Uvicorn | REST endpoints with streaming support |
| **Observability** | LangSmith | Full trace of every node, prompt, and LLM call |
| **UI** | Streamlit | Live demo with real-time pipeline progress |
| **Backend Hosting** | Render (Docker) | Containerised FastAPI deployment |
| **Frontend Hosting** | Streamlit Community Cloud | Public UI deployment |

---

## 📂 Project Structure

```
AI-Blog-Generator/
├── src/
│   ├── LLMs/
│   │   └── groqllm.py              # Groq LLM initialisation
│   ├── graphs/
│   │   └── graph_builder.py        # LangGraph StateGraph construction
│   ├── nodes/
│   │   └── blog_node.py            # All graph node functions + routing logic
│   └── state/
│       └── blog_state.py           # BlogState TypedDict + Blog Pydantic model + tone instructions
├── app.py                          # FastAPI server — /blogs and /blogs/stream endpoints
├── streamlit_app.py                # Streamlit UI with real-time streaming progress
├── Dockerfile                      # Container definition for Render deployment
├── requirements.txt                # Python dependencies
├── langgraph.json                  # LangGraph Cloud deployment config
└── .env.example                    # Environment variable template
```

---

## ⚙️ How It Works

### 1. Title Creation
The graph starts by generating a creative, SEO-friendly title using the topic and tone instruction. The tone instruction (e.g. "Write in a witty, humorous tone...") is injected at this stage and every subsequent stage.

### 2. Outline Generation
Before writing content, the graph produces a structured outline with introduction, 4–6 main sections, and conclusion. This forces the LLM to plan before writing, producing significantly more coherent long-form content.

### 3. Content Generation
Full blog content is written following the outline. If this is a revision pass, the quality checker's feedback from the previous attempt is injected into the prompt so the model addresses specific weaknesses.

### 4. Quality Check (Agentic Loop)
A senior editor persona scores the blog 0–10 across length, structure, engagement, and tone consistency. If the score is below 7 and fewer than 3 revisions have occurred, the graph routes back to content generation. This is the core agentic behaviour.

### 5. Translation (Optional)
After approval, the `route` node reads `current_language` from state and conditionally routes to the appropriate translation node (Hindi, Marathi, or French), which preserves markdown formatting.

---

## 🏃 Running Locally

### Prerequisites
- Python 3.12+
- Groq API key ([console.groq.com](https://console.groq.com))
- LangSmith API key ([smith.langchain.com](https://smith.langchain.com)) — optional but recommended

### Setup

```bash
git clone https://github.com/Spandan752/AI-Blog-Generator.git
cd AI-Blog-Generator
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Environment Variables

```bash
cp .env.example .env
# Edit .env and add your keys
```

```env
GROQ_API_KEY=your_groq_api_key_here
LANGCHAIN_API_KEY=your_langsmith_api_key_here
```

### Run the API

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
# API: http://127.0.0.1:8000
# Swagger docs: http://127.0.0.1:8000/docs
```

### Run the Streamlit UI

```bash
streamlit run streamlit_app.py
# UI: http://localhost:8501
```

### Run with Docker

```bash
docker build -t ai-blog-generator .
docker run -p 8000:8000 \
  -e GROQ_API_KEY=your_key \
  -e LANGCHAIN_API_KEY=your_key \
  ai-blog-generator
```

---

## 🔌 API Reference

### `GET /`
Health check.

**Response:**
```json
{ "status": "ok", "message": "AI Blog Generator API is running." }
```

---

### `POST /blogs`
Generate a complete blog post synchronously.

**Request:**
```json
{
  "topic": "The future of renewable energy",
  "tone": "casual",
  "language": ""
}
```

| Field | Type | Required | Options |
|---|---|---|---|
| `topic` | string | ✅ | Min 3 characters |
| `tone` | string | ❌ | `professional`, `casual`, `academic`, `humorous` (default: `professional`) |
| `language` | string | ❌ | `hindi`, `marathi`, `french` (default: English) |

**Response:**
```json
{
  "title": "Why Going Green is Actually Pretty Cool",
  "outline": "## Introduction\n## ...",
  "content": "## Introduction\n\nLet's be honest — renewable energy...",
  "language": "",
  "tone": "casual",
  "quality_score": 8,
  "revision_count": 1
}
```

---

### `POST /blogs/stream`
Stream pipeline events as Server-Sent Events. Each line is a JSON object emitted as each graph node completes.

**Request:** Same as `/blogs`

**Stream output:**
```
{"node": "title_creation", "title": "Why Going Green is Actually Pretty Cool", ...}
{"node": "outline_generation", ...}
{"node": "content_generation", ...}
{"node": "quality_check", "quality_score": 6, "revision_count": 1}
{"node": "content_generation", ...}
{"node": "quality_check", "quality_score": 8, "revision_count": 2}
```

---

## 🎨 Tone Examples

Same topic, four different tones — the difference is striking:

| Tone | Example Title |
|---|---|
| **Professional** | "The Strategic Case for Renewable Energy Investment in 2025" |
| **Casual** | "Why Going Green is Actually Pretty Cool (and Cheaper Than You Think)" |
| **Academic** | "Renewable Energy Transition: An Analysis of Adoption Barriers and Policy Frameworks" |
| **Humorous** | "Sun, Wind, and Zero Guilt: A Love Letter to Renewable Energy" |

---

## 🧠 Key Engineering Decisions

**Why LangGraph over a simple LCEL chain?**
LCEL chains are linear — they can't loop. The quality check revision cycle requires the graph to route back to a previous node based on a score, which is only possible with LangGraph's `StateGraph` and `add_conditional_edges`. This is the fundamental reason LangGraph exists.

**Why stream events rather than waiting for the full response?**
Blog generation with quality loops takes 15–30 seconds. A blank screen for that duration destroys the UX. The streaming endpoint emits a JSON event after each node completes, so the UI can show live progress — making the wait feel interactive rather than broken.

**Why separate outline and content generation into two nodes?**
A single "write the blog" prompt produces generic, poorly structured output. Separating outline generation forces the LLM to plan the structure first, then write section by section following that plan. The resulting content is measurably more coherent and better structured.

**Why inject tone instructions at every node?**
Tone drift is a common failure mode — the title might be humorous but the content drifts academic. By injecting the full tone instruction string (not just the word "humorous") at title, outline, and content generation stages, the style stays consistent throughout. The quality checker also validates tone consistency as part of its score.

---

## ☁️ Deployment

### Required Environment Variables

| Variable | Description |
|---|---|
| `GROQ_API_KEY` | Groq API key for LLaMA inference |
| `LANGCHAIN_API_KEY` | LangSmith API key for tracing |

### Architecture
- **FastAPI backend** → Deployed on Render (Docker, free tier)
- **Streamlit frontend** → Deployed on Streamlit Community Cloud
- **Backend URL** → `https://ai-blog-generator-api-favc.onrender.com`

> ⚠️ The free Render tier spins down after 15 minutes of inactivity. The first request after idle may take ~30 seconds to wake up.

---

## ⚠️ Disclaimer

This tool generates AI-assisted content intended as a starting point. Always review and edit generated blogs before publishing. AI-generated content should be fact-checked before use.

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.