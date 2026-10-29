# 🌟 SoulSync: Multimodal Emotional AI Companion & Assistant

SoulSync is an empathetic, beginner-friendly multimodal AI assistant designed to provide emotional support, contextual guidance, and intelligent research capabilities. Built with **React**, **FastAPI**, and **PostgreSQL (pgvector)**, it bridges compassionate conversation with document retrieval, live web search, and cross-modal interactions (Text, Audio, Images, Documents).

---

## 🎯 Project Overview & MVP Scope

This project focuses on delivering a streamlined, zero-friction AI companion experience by skipping administrative dashboards and complex user authentication in Phase 1, prioritizing core multimodal intelligence and conversational empathy.

### Core Capabilities

1. **Multimodal Input & Understanding**:
   - 💬 **Text**: Natural conversational prompts and emotional journaling.
   - 🎙️ **Voice/Audio**: Real-time microphone input / audio file uploads with automated transcription.
   - 🖼️ **Images**: Visual scene understanding, facial expression analysis, emotional context extraction.
   - 📄 **Documents**: PDF, TXT, and Markdown upload for grounded contextual understanding.

2. **Multimodal Output Generation**:
   - 📝 **Empathetic Text**: Emotionally attuned, validating responses using compassionate conversational frameworks.
   - 🔊 **Voice Synthesis (TTS)**: Calming spoken audio responses.
   - 🎨 **Visual Output**: Generated imagery, uplifting affirmations, and structured markdown visuals.

3. **Knowledge Retrieval (RAG) & Document Memory**:
   - Grounded context retrieval using **PostgreSQL + pgvector**.
   - Document chunking, semantic embedding, and hybrid similarity search.
   - Ability to **create, edit, and summarize personal notes or companion documents** directly within the chat workflow.

4. **Live Web Search**:
   - Built-in web search integration (DuckDuckGo / Tavily) to verify facts, find mental wellness resources, hotlines, or answer general real-time queries.

5. **Personal Emotional Assistant Persona**:
   - Built-in emotional intelligence layer providing active listening, reflective questioning, non-judgmental companionship, and gentle wellness check-ins.

---

## 🏗️ Architecture Overview

```mermaid
flowchart TD
    User([User]) <-->|Text / Voice / Images / Files| Frontend[React + Vite Frontend]
    
    subgraph Frontend_Layer [Frontend: React SPA]
        ChatUI[Chat Interface & Emotional Tone Indicator]
        AudioIO[Voice Input / TTS Audio Player]
        DocManager[Attached Documents & Notes Panel]
    end
    
    Frontend <-->|REST API / Multipart| Backend[FastAPI Backend]
    
    subgraph Backend_Layer [Backend: Python / FastAPI]
        Router[API Routers: /chat, /documents, /search]
        Orchestrator[Agent Orchestrator & Emotion Prompt Engine]
        SearchTool[Web Search Engine]
        RAGPipeline[RAG & Embedding Pipeline]
    end
    
    Backend <-->|SQL & Vector Queries| Database[(PostgreSQL + pgvector)]
    Backend <-->|Multimodal LLM / TTS| ModelProvider[LLM Provider API: Gemini / OpenAI]
    Backend <-->|Real-time Search| Web[DuckDuckGo / Web Engine]
```

---

## 💻 Tech Stack

| Component | Technology | Rationale |
| :--- | :--- | :--- |
| **Frontend** | React 18, Vite, Tailwind CSS, Lucide Icons | Responsive, fast, and simple component architecture |
| **Backend API** | Python 3.10+, FastAPI, Uvicorn, Pydantic | High-performance asynchronous API framework |
| **Database & Vector Store** | PostgreSQL 15+ with `pgvector` extension | Single datastore for relational documents and semantic embeddings |
| **ORM & DB Access** | SQLAlchemy 2.0 (Async) + Alembic | Modern async Python database access |
| **AI / Multimodal LLM** | Google Gemini 1.5 Flash / Pro (or OpenAI GPT-4o) | Native multimodal vision, audio, and text reasoning |
| **Speech (STT / TTS)** | Whisper API / Web Speech API (STT), gTTS / ElevenLabs (TTS) | Expressive voice input and output |
| **Web Search** | `duckduckgo-search` or Tavily API | Fast, privacy-friendly, zero-cost search engine |
| **Embeddings & Chunking** | LangChain / Sentence-Transformers | Robust text splitting and embedding generation |

---

## 📂 Project Directory Structure

```text
ML chatbot/
├── README.md
├── docker-compose.yml              # PostgreSQL + pgvector container
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI application entry point
│   │   ├── config.py               # Settings and environment variables
│   │   ├── db/
│   │   │   ├── session.py          # Async PostgreSQL connection
│   │   │   └── models.py           # Messages, Documents, and Vector tables
│   │   ├── schemas/
│   │   │   ├── chat.py             # Request/Response schemas
│   │   │   └── document.py
│   │   ├── services/
│   │   │   ├── llm_service.py      # Multimodal LLM & Emotional Assistant prompt
│   │   │   ├── rag_service.py      # Chunking, embedding & vector retrieval
│   │   │   ├── search_service.py   # Web search integration
│   │   │   ├── audio_service.py    # Speech-to-Text & Text-to-Speech
│   │   │   └── document_service.py # Note creation & document updates
│   │   └── api/
│   │       ├── v1/
│   │       │   ├── chat.py
│   │       │   ├── documents.py
│   │       │   └── health.py
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── package.json
    ├── vite.config.js
    ├── tailwind.config.js
    ├── src/
    │   ├── App.jsx
    │   ├── main.jsx
    │   ├── components/
    │   │   ├── ChatWindow.jsx      # Chat stream and message bubbles
    │   │   ├── MessageInput.jsx    # Text, Audio Recorder, Image/Doc Uploader
    │   │   ├── DocumentPanel.jsx   # Document viewer, editor & update trigger
    │   │   ├── EmotionalStatus.jsx # Calming companion avatar & mood badge
    │   │   └── AudioPlayer.jsx     # Spoken response playback
    │   └── services/
    │       └── api.js              # Axios / Fetch client
    └── .env.example
```

---

## 🚀 Quickstart Guide

### Prerequisites
- **Python 3.10+**
- **Node.js 18+** & npm
- **Docker & Docker Compose** (for PostgreSQL with `pgvector`) or a local PostgreSQL installation with `pgvector` enabled.
- API Key: Google Gemini API Key (`GEMINI_API_KEY`) or OpenAI API Key (`OPENAI_API_KEY`).

---

### Step 1: Database Setup with Docker

Run PostgreSQL with the `pgvector` extension pre-installed:

```bash
docker run -d \
  --name soul-postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=soulsync_db \
  -p 5432:5432 \
  pgvector/pgvector:pg16
```

---

### Step 2: Backend Setup (FastAPI)

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Linux/macOS:
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables in `.env`:
   ```env
   DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/soulsync_db
   GEMINI_API_KEY=your_gemini_api_key_here
   APP_ENV=development
   ```

5. Run the FastAPI development server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   *Swagger API Documentation will be available at: `http://localhost:8000/docs`*

---

### Step 3: Frontend Setup (React)

1. Navigate to the frontend directory:
   ```bash
   cd ../frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Configure environment variables in `.env`:
   ```env
   VITE_API_BASE_URL=http://localhost:8000/api/v1
   ```

4. Start the Vite development server:
   ```bash
   npm run dev
   ```
   *Application will be available at: `http://localhost:5173`*

---

## 📡 API Endpoints (MVP)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/chat` | Main multimodal conversation endpoint (Accepts text, image, audio, doc context) |
| `POST` | `/api/v1/documents/upload` | Ingests a PDF/TXT document, creates chunks, and stores embeddings in `pgvector` |
| `GET` | `/api/v1/documents` | Lists all created / attached personal notes and documents |
| `PUT` | `/api/v1/documents/{id}` | Updates document content (manual or AI-triggered note editing) |
| `POST` | `/api/v1/search` | Performs web query retrieval to enrich assistant context |
| `GET` | `/api/v1/health` | Service and database health check |

---

## 🛡️ Emotional Assistance Guidelines & Safety Boundaries
- **Active Listening & Validation**: Prioritizes empathetic reflection before offering solutions.
- **Crisis Guardrails**: Detects severe distress keywords and provides immediate emergency helpline resources (e.g., Suicide & Crisis Lifeline, Crisis Text Line) while gently disclaiming medical authority.
- **Personalized Notes**: Acts as an emotional scribe, creating or updating "Reflection Journal" entries at the user's request.

---

## 🗺️ Roadmap Beyond MVP
- [ ] User authentication (OAuth2 / JWT) & multi-session isolation.
- [ ] Voice streaming via WebSockets for low-latency voice conversations.
- [ ] Custom visual avatars with reactive emotional expressions.
- [ ] Long-term semantic user memory & mood trend analytics.
