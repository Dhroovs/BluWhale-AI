<p align="center">
  <img src="docs/screenshots/01_dark_welcome.png" alt="BluWhale AI Banner" width="100%">
</p>

<h1 align="center">🐋 BluWhale AI</h1>

<p align="center"><strong>A self-hosted, full-stack AI Chatbot Control Center with RAG, Memory, Assistants, Web Search & Canvas Artifacts.</strong></p>

<p align="center">
  <a href="#-features">Features</a> &nbsp;·&nbsp;
  <a href="#-tech-stack">Tech Stack</a> &nbsp;·&nbsp;
  <a href="#-screenshots">Screenshots</a> &nbsp;·&nbsp;
  <a href="#-quick-start">Quick Start</a> &nbsp;·&nbsp;
  <a href="#-api-reference">API Reference</a> &nbsp;·&nbsp;
  <a href="#-running-tests">Tests</a> &nbsp;·&nbsp;
  <a href="#-architecture">Architecture</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.13+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite">
  <img src="https://img.shields.io/badge/xAI_Grok-LLM_Powered-111111?style=for-the-badge&logo=x&logoColor=white" alt="Grok">
  <img src="https://img.shields.io/badge/Tests-22%20Passed-10b981?style=for-the-badge&logo=pytest&logoColor=white" alt="Tests">
  <img src="https://img.shields.io/badge/License-MIT-blue?style=for-the-badge" alt="License">
</p>

---

BluWhale AI is a **production-ready, self-hosted chatbot workspace** you can run entirely on your own machine. It gives you a full AI control center — organize conversations into projects, feed your assistants custom documents, enable real-time web search, auto-remember user facts, and capture generated code into a Canvas panel. Connect it to the **xAI Grok API** for live responses, or run in **offline simulation mode** with zero external dependencies.

> **"BluWhale AI"** is the name of the platform — a powerful, intelligent AI chatbot workspace. The whale is the brand; the product is a full-stack AI engine.

---

## ✨ Features

### 🧠 Core Intelligence

| Feature | Description |
|---|---|
| **Multi-Assistant System** | Create named AI personas, each with its own system prompt, icon, and knowledge base |
| **RAG (Retrieval Augmented Generation)** | Feed documents to your assistant — it retrieves the most relevant chunks to answer your questions |
| **User Memory** | Automatically extracts and remembers facts about you (name, profession, preferences) across sessions |
| **Web Search Mode** | Switch a conversation to live web search — AI answers with real-time sourced results |
| **Canvas Artifact System** | AI-generated code/SQL/JSON is auto-captured into a separate document panel for copy & download |
| **xAI Grok Integration** | Connects to xAI's Grok API (`grok-beta`, `grok-2`) with graceful offline simulation fallback |

### 🗂️ Workspace Organization

| Feature | Description |
|---|---|
| **Projects & Folders** | Group conversation threads into named project workspaces |
| **Conversation Threads** | Each thread is linked to a specific assistant with its own message history |
| **Chat Mode Switching** | Per-conversation modes: Normal / RAG / Web Search |
| **Conversation Transfer** | Move threads between project folders |
| **Full Message History** | All messages persisted in SQLite with chronological retrieval |

### 📚 Knowledge Base Ingestion

| Method | Supported Formats |
|---|---|
| **File Upload** | `.pdf` (via PyPDF), `.txt`, `.md` |
| **URL Scraping** | Any public web page (via HTTPX + BeautifulSoup4) |
| **Raw Text Paste** | Direct text input |
| **Auto-Chunking** | Recursive character splitter: 500 char chunks, 50 char overlap |

### 🎨 Premium UI

- **Deep Blue Waters** design system — ocean-inspired dark/light themes
- **BluWhale SVG logo** — animated swimming whale identity
- **Glassmorphism** — frosted glass cards, modals, and panels
- **Pulsing send button** — animated ocean glow effect
- **Toast notifications** — 4 types: success, error, warning, info
- **Textarea auto-grow** — input expands as you type
- **Fully responsive** — works across screen sizes

---

## 🛠️ Tech Stack

### Backend

| Technology | Role |
|---|---|
| **Python 3.13** | Core language |
| **FastAPI** | REST API framework — routing, validation, Swagger docs, dependency injection |
| **Uvicorn** | ASGI server with hot-reload for development |
| **SQLAlchemy 2.0** | ORM — maps Python models to SQLite; handles relationships, cascade deletes |
| **SQLite** | Local file database (`deneb.db`) — zero-config, portable |
| **Pydantic v2** | Request/response schema validation & serialization |
| **HTTPX** | HTTP client — Grok API calls + web page scraping |
| **PyPDF** | PDF text extraction for knowledge base ingestion |
| **BeautifulSoup4** | HTML cleaning & web page content scraping |
| **python-multipart** | Multipart file upload support |
| **Pytest** | Automated test framework (22 tests, 100% pass rate) |

### Frontend

| Technology | Role |
|---|---|
| **HTML5** | Single-page app structure |
| **Vanilla CSS** | 2,400+ line custom design system — CSS variables, animations, glassmorphism |
| **Vanilla JavaScript (ES6+)** | 1,350+ lines — all UI logic, API calls, state management |
| **Google Fonts** | Inter, Inter Tight, JetBrains Mono |
| **Font Awesome 6.4** | Icon library |
| **Inline SVG** | Custom animated BluWhale logo |

---

## 📸 Screenshots

<table>
  <tr>
    <td align="center" width="50%">
      <img src="docs/screenshots/01_dark_welcome.png" alt="Dark Mode Welcome" width="100%">
      <br><em>Dark Mode — Welcome Screen</em>
    </td>
    <td align="center" width="50%">
      <img src="docs/screenshots/02_dark_sidebar.png" alt="Projects Sidebar" width="100%">
      <br><em>Dark Mode — Projects & Conversations Sidebar</em>
    </td>
  </tr>
  <tr>
    <td align="center" width="50%">
      <img src="docs/screenshots/03_dark_chat.png" alt="Chat in Progress" width="100%">
      <br><em>Dark Mode — Active Chat with AI Response</em>
    </td>
    <td align="center" width="50%">
      <img src="docs/screenshots/04_dark_assistants.png" alt="Assistants Manager" width="100%">
      <br><em>Dark Mode — Assistants Manager Modal</em>
    </td>
  </tr>
  <tr>
    <td align="center" width="50%">
      <img src="docs/screenshots/05_dark_knowledge.png" alt="Knowledge Base" width="100%">
      <br><em>Dark Mode — Knowledge Base Manager</em>
    </td>
    <td align="center" width="50%">
      <img src="docs/screenshots/06_light_welcome.png" alt="Light Mode Welcome" width="100%">
      <br><em>Light Mode — Welcome Screen</em>
    </td>
  </tr>
  <tr>
    <td align="center" width="50%">
      <img src="docs/screenshots/07_light_chat.png" alt="Light Mode Chat" width="100%">
      <br><em>Light Mode — Active Chat Interface</em>
    </td>
    <td align="center" width="50%">
      <br>
      <br>
      <h3>🐋 Both Themes Supported</h3>
      <p>Switch instantly between dark ocean and light sage themes. Theme preference is remembered across sessions.</p>
    </td>
  </tr>
</table>

---

## ⚡ Quick Start

### Prerequisites

- **Python 3.10+** — [python.org](https://www.python.org/downloads/)
- **Git**

### 1. Clone the Repository

```bash
git clone https://github.com/Dhroovs/BluWhale-AI.git
cd BluWhale-AI
```

### 2. Create & Activate Virtual Environment

```bash
# Create environment
python -m venv venv

# Activate — Windows PowerShell
.\venv\Scripts\Activate.ps1

# Activate — macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Seed the Database (optional but recommended)

```bash
python seed_data.py
```

### 5. Start the Server

```bash
python main.py
```

> The server starts at **`http://127.0.0.1:8000`**

### 6. Open the App

Navigate to **[http://127.0.0.1:8000/chat](http://127.0.0.1:8000/chat)**

---

## 🔑 API Keys

BluWhale AI has two separate keys:

| Key | Purpose | Where to set |
|---|---|---|
| **App API Key** | Authenticates all REST API calls (default: `deneb-secret-key`) | Settings drawer in UI → Save Keys |
| **Grok API Key** | Powers real xAI Grok LLM responses | Settings drawer in UI → Save Keys |

> If no Grok key is provided, the system gracefully falls back to **offline simulation mode** — it still returns meaningful responses using RAG context and web search results. Nothing breaks.

Get a Grok API key at [console.x.ai](https://console.x.ai)

---

## 🔌 API Reference

All endpoints are prefixed with `/api/v1/` and require the `X-API-Key` header.

### Chatbot Agents
```
POST   /api/v1/chatbots/              Create chatbot agent
GET    /api/v1/chatbots/              List with search, filter, pagination
GET    /api/v1/chatbots/{id}          Get details
PUT    /api/v1/chatbots/{id}          Update (partial)
DELETE /api/v1/chatbots/{id}          Delete (cascades KB)
POST   /api/v1/chatbots/{id}/chat     Chat with Grok + RAG injection
POST   /api/v1/chatbots/{id}/simulate Simulate RAG context retrieval
```

### Assistants
```
POST   /api/v1/assistants/            Create assistant persona
GET    /api/v1/assistants/            List assistants
GET    /api/v1/assistants/{id}        Get details
PUT    /api/v1/assistants/{id}        Update
DELETE /api/v1/assistants/{id}        Delete
```

### Projects & Conversations
```
POST   /api/v1/projects               Create project folder
GET    /api/v1/projects               List projects
PUT    /api/v1/projects/{id}          Rename/update
DELETE /api/v1/projects/{id}          Delete (cascade)

POST   /api/v1/conversations          Create conversation thread
GET    /api/v1/conversations          List threads
PUT    /api/v1/conversations/{id}     Update/move/rename
DELETE /api/v1/conversations/{id}     Delete thread

GET    /api/v1/conversations/{id}/messages   Get message history
POST   /api/v1/conversations/{id}/messages   Send chat message (main chat action)
GET    /api/v1/conversations/{id}/artifacts  List canvas artifacts
```

### Knowledge Base
```
POST   /api/v1/knowledge-base/                          Create knowledge base
GET    /api/v1/knowledge-base/                          List knowledge bases
DELETE /api/v1/knowledge-base/{id}                      Delete KB
POST   /api/v1/knowledge-base/{id}/documents/text       Ingest raw text
POST   /api/v1/knowledge-base/{id}/documents/upload     Upload PDF/TXT file
POST   /api/v1/knowledge-base/{id}/documents/url        Scrape web page URL
DELETE /api/v1/knowledge-base/{kb_id}/documents/{doc_id} Remove document
```

### Memory
```
GET    /api/v1/memories/    List memories (filter by category/search)
POST   /api/v1/memories/    Create memory entry
PUT    /api/v1/memories/{id} Update memory
DELETE /api/v1/memories/{id} Delete memory
```

> **Interactive Swagger docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
> **ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🧪 Running Tests

```bash
python -m pytest test_api.py test_advanced_features.py -v
```

### Test Results

```
test_api.py::test_create_chatbot                          PASSED
test_api.py::test_create_chatbot_invalid_temp             PASSED
test_api.py::test_create_chatbot_invalid_model            PASSED
test_api.py::test_get_chatbot_details                     PASSED
test_api.py::test_update_chatbot_details                  PASSED
test_api.py::test_delete_chatbot                          PASSED
test_api.py::test_list_chatbots_pagination_and_search     PASSED
test_api.py::test_create_knowledge_base                   PASSED
test_api.py::test_create_kb_invalid_chatbot               PASSED
test_api.py::test_delete_chatbot_cascades_kb              PASSED
test_api.py::test_api_key_verification                    PASSED
test_api.py::test_knowledge_base_auto_chunking            PASSED
test_api.py::test_file_upload_txt                         PASSED
test_api.py::test_file_upload_pdf                         PASSED
test_api.py::test_url_scraping_and_auto_scraping          PASSED
test_api.py::test_chat_simulation                         PASSED
test_api.py::test_chat_with_grok_fallback                 PASSED
test_api.py::test_chat_with_grok_mocked                   PASSED
test_advanced_features.py::test_assistant_crud            PASSED
test_advanced_features.py::test_memory_crud               PASSED
test_advanced_features.py::test_project_and_conversation_workflow  PASSED
test_advanced_features.py::test_web_search_and_canvas_extraction   PASSED

========================= 22 passed in 4.14s =========================
```

---

## 🏗️ Architecture

### Project Structure

```
BluWhale-AI/
│
├── main.py                          # FastAPI app entry — routes, static files, /chat
├── requirements.txt                 # Python dependencies
├── seed_data.py                     # Database seeding script
├── test_api.py                      # Core API test suite (18 tests)
├── test_advanced_features.py        # Advanced features test suite (4 tests)
│
├── app/
│   ├── config.py                    # Settings: DB URL, API keys
│   ├── database/connection.py       # SQLite engine + SessionLocal factory
│   ├── models/                      # SQLAlchemy ORM models
│   │   ├── chatbot.py               # Chatbot + KnowledgeBase + Chunk models
│   │   ├── assistant.py             # Assistant model
│   │   ├── memory.py                # Memory model
│   │   └── project.py               # Project + Conversation + Message + Artifact
│   ├── schemas/                     # Pydantic request/response schemas
│   ├── routes/                      # FastAPI route controllers
│   ├── services/
│   │   ├── chat.py                  # ★ Main 11-step chat pipeline
│   │   ├── llm.py                   # Grok API wrapper + simulation fallback
│   │   ├── memory.py                # Memory CRUD + auto-extraction
│   │   └── search.py                # Web search service
│   └── utils/
│       ├── extractor.py             # PDF + URL text extraction
│       ├── text_splitter.py         # Recursive document chunker
│       └── security.py              # API key authentication dependency
│
├── static/
│   ├── index.html                   # Single-page app HTML
│   ├── style.css                    # 2,400+ line design system
│   └── app.js                       # 1,350+ line frontend logic
│
└── docs/screenshots/                # UI screenshots for this README
```

### The Chat Pipeline

Every message sent goes through an **11-step pipeline** in `app/services/chat.py`:

```
 1. Load conversation + assistant from database
 2. Auto-extract memory facts from user message (regex heuristics)
 3. Retrieve & inject top user memories into system prompt
 4. Score all KB chunks by keyword overlap → inject top 2 (RAG)
 5. Run web search if chat_mode = 'web_search' → inject results
 6. Build consolidated system prompt (assistant + memory + RAG + search)
 7. Load last 15 messages for conversation context window
 8. Call LLMService → xAI Grok API (or simulation fallback)
 9. Auto-extract code blocks → save as Canvas Artifacts
10. Persist user + assistant messages to database
11. Return response payload with sources, artifact, and metadata
```

---

## 🔒 Security Model

All API routes require the `X-API-Key` header:

```python
# FastAPI dependency applied globally to all routers
async def verify_api_key(x_api_key: str = Header(..., alias="X-API-Key")):
    if x_api_key != settings.API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
```

Override the default key via environment variable:
```bash
export API_KEY=your-secret-key
export GROK_API_KEY=your-grok-key
python main.py
```

---

## 🎨 Design System

BluWhale AI uses the **"Deep Blue Waters"** color palette — inspired by Nordic seascapes and ocean depths.

| Color | Hex | Usage |
|---|---|---|
| Steel Blue | `#3a7ca5` | Primary actions, logo, borders |
| Sky Blue | `#81c3d7` | Accents, hover states |
| Baltic Blue | `#16425b` | Card backgrounds, sidebar |
| Ocean Dark | `#0a2233` | Main background |
| Ice White | `#e8f4f8` | Primary text |

Both **dark** and **light** modes fully supported — toggle with one click, persisted to localStorage.

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<p align="center">Built with 🐋 by <a href="https://github.com/Dhroovs">Dhroovs</a></p>
