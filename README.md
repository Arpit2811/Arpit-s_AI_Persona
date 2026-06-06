# Arpit AI Persona - RAG + Agentic AI System

A production-ready hybrid system combining **Retrieval-Augmented Generation (RAG)** for intelligent Q&A with **Agentic AI** for autonomous multi-step interview booking workflows. Supports voice, chat, and SMS interactions across FAISS vector search, GPT-4o-mini LLM, Make.com calendar automation, and external webhooks.

---

## 🎯 Project Overview

**Arpit AI Persona** is a hybrid **RAG (Retrieval-Augmented Generation) + Agentic AI** system that intelligently processes user requests through dual pathways:

### 🧠 Retrieval-Augmented Generation (RAG) Pathway
- **Knowledge Q&A**: Answers questions about Arpit's resume, skills, experience, and GitHub projects
- **Semantic Search**: FAISS vector database with 768-dim BGE embeddings indexes resume + 5 GitHub READMEs
- **Smart Retrieval**: Intent-based routing (Resume vs. GitHub) + repo-specific context window expansion
- **Context-Aware Responses**: GPT-4o-mini generates answers with multi-turn conversation history

### 🤖 Agentic AI Pathway
- **Intent Detection**: Automatically classifies user input as knowledge question or booking request
- **Multi-Step Booking Workflow**: State machine with 7 stages (date → slot → name → email → subject → notes → booking)
- **External API Orchestration**: Calls Make.com webhooks for calendar availability checks and booking creation
- **Autonomous Decision Making**: Validates inputs, handles errors, routes to next stage based on user response
- **Stateful Conversation**: Maintains session state and conversation history across turns

### 🌐 Multi-Channel Support
- **Web Chat**: Streamlit frontend with full RAG + booking capabilities
- **Voice Calls**: Vapi voice agent for conversational AI interaction
- **SMS/Phone**: Twilio integration for text and voice at +18582640535
- **Session Management**: Per-channel conversation history and booking state tracking

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACES                         │
├─────────────────────────────────────────────────────────────────┤
│  Streamlit Web UI  │  Twilio SMS/Phone  │  Vapi Voice Agent   │
│  (:8501)           │  (+18582640535)    │  (IVR/Voice)        │
└──────────┬──────────┴──────────┬─────────┴──────────┬───────────┘
           │                      │                    │
           └──────────┬───────────┴────────────────────┘
                      │
          ┌───────────▼────────────┐
          │   FastAPI Backend      │
          │   (main.py :8001)      │
          └───────┬────────────────┘
                  │
    ┌─────────────┼─────────────┬──────────────┐
    │             │             │              │
    ▼             ▼             ▼              ▼
┌────────┐  ┌──────────────┐ ┌──────────┐  ┌─────────────┐
│ RAG    │  │ Booking      │ │ Intent   │  │ Make.com    │
│ Engine │  │ Workflow     │ │ Router   │  │ Integration │
│        │  │              │ │          │  │             │
│ (Vdb)  │  │ (Multistep   │ │ (Smart   │  │ (Calendar   │
│        │  │ Questions)   │ │ Intent   │  │ Webhooks)   │
└────┬───┘  └──────────────┘ │ Detection│  └─────────────┘
     │                        │          │
     │                        └──────────┘
     │
  ┌──▼─────────────────────┐
  │  FAISS Vector DB       │
  │  ├─ chunks.json        │
  │  └─ resume.index       │
  │                        │
  │  Indexed Sources:      │
  │  • Resume (.docx)      │
  │  • GitHub READMEs      │
  │  • BGE Embeddings      │
  │    (768-dim)           │
  └────────────────────────┘
```

### Component Flow

```
User Input (Chat/Voice/SMS)
    │
    ├─→ Intent Detection
    │   ├─ Is booking intent? → Booking Workflow
    │   └─ Is knowledge question? → RAG Pipeline
    │
    ├─→ Booking Workflow (if intent detected)
    │   ├─ Stage 1: Await Date → Parse date → Check availability (Make.com)
    │   ├─ Stage 2: Await Slot → Validate slot selection
    │   ├─ Stage 3: Await Name → Collect candidate name
    │   ├─ Stage 4: Await Email → Validate email
    │   ├─ Stage 5: Await Subject → Get interview title
    │   ├─ Stage 6: Await Notes → Get agenda/notes
    │   └─ Stage 7: Complete → Create booking (Make.com) → Return confirmation
    │
    ├─→ RAG Pipeline (if knowledge question)
    │   ├─ Expand Query (synonym expansion)
    │   ├─ Detect Source Filter (Resume vs GitHub)
    │   ├─ Detect Repo (if GitHub repo mentioned)
    │   ├─ Retrieve Context (FAISS semantic search)
    │   ├─ Assemble Context (filter by relevance + format)
    │   └─ Generate Answer (GPT-4o-mini + conversation history)
    │
    └─→ Response
        ├─ Chat Interface (Streamlit)
        ├─ Voice Response (Vapi)
        └─ SMS Response (Twilio)
```

---

## 🗂️ Project Structure

```
sclaer/
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
│
├── backend/                           # FastAPI server
│   ├── main.py                        # Main API endpoints & CORS setup
│   ├── booking_workflow.py            # Multi-step booking state machine
│   ├── rag_retrieve.py                # RAG pipeline & intent routing
│   ├── make_service.py                # Make.com webhook integration
│   ├── ingest.py                      # FAISS indexing pipeline
│   └── testing.py                     # Test utilities
│
├── frontend/                          # User interfaces
│   └── app.py                         # Streamlit web UI
│
├── data/                              # Source documents
│   ├── Resume_Arpit_v2026.docx       # Resume (parsed into resume section)
│   └── repos/                         # GitHub project READMEs
│       ├── Arxiv_scrapping/README.md
│       ├── Minhash-LSH-Jaccard.../README.md
│       ├── Rag_based_ATS_Analyser/README.md
│       ├── SFT_MODEL_TRAINING/README.md
│       └── Zlib_epub_extractor/README.md
│
├── index1/                            # FAISS Vector Database (indexed)
│   ├── resume.index                   # FAISS flat IP index (768-dim, BGE embeddings)
│   └── chunks.json                    # All indexed chunks with metadata
│
└── scaler_venv/                       # Python virtual environment
```

---

## 🔌 External Integrations

### 1. **Make.com Webhooks**

#### Availability Webhook
- **Endpoint**: `MAKE_AVAILABILITY_WEBHOOK` (environment variable)
- **Purpose**: Fetch available calendar slots for a given date
- **Request**:
  ```json
  {
    "interviewDate": "2026-05-09"
  }
  ```
- **Response**:
  ```json
  {
    "busySlots": [
      { "start": "2026-05-09T09:00:00.000Z" },
      { "start": "2026-05-09T14:00:00.000Z" }
    ]
  }
  ```
- **Used in**: `make_service.py` → `get_available_slots()`

#### Booking Webhook
- **Endpoint**: `MAKE_BOOKING_WEBHOOK` (environment variable)
- **Purpose**: Create Google Meet interview invitation
- **Request**:
  ```json
  {
    "candidateName": "John Doe",
    "candidateEmail": "john@example.com",
    "interviewDate": "2026-05-09",
    "startTime": "10:00",
    "subject": "AI Engineer Interview - Round 1",
    "body": "Agenda: Technical round focusing on NLP"
  }
  ```
- **Used in**: `make_service.py` → `create_booking()`

### 2. **Twilio Integration**

- **Phone Number**: `+18582640535`
- **Purpose**: SMS and voice call routing to the system
- **Flow**:
  ```
  Incoming Call/SMS
      ↓
  Twilio Routes to Backend API
      ↓
  Message processed (Chat/Voice RAG)
      ↓
  Response returned
      ↓
  Twilio sends Voice/SMS back to user
  ```
- **Configuration**: Set Twilio webhook URL to `http://<backend-ip>:8001/voice-rag`

### 3. **Vapi - Voice Agent**

- **Purpose**: Handle voice calls, voice transcription, and natural conversation
- **Integration Points**:
  - Voice input → transcribed to text
  - Routed through `/voice-rag` endpoint
  - Response synthesized to speech
  - Maintains conversation history per session
- **Configuration**: Vapi connects to the `/voice-rag` endpoint

---

## 📊 Vector Database - FAISS

### Overview
- **Type**: FAISS IndexFlatIP (Inner Product for cosine similarity after L2 normalization)
- **Embedding Model**: `BAAI/bge-base-en-v1.5` (768-dimensional)
- **Normalization**: L2 normalized for cosine similarity
- **Total Chunks**: ~100+ (resume + 5 GitHub READMEs)

### Index Files

**`resume.index`**
- Binary FAISS index file
- Contains all 768-dim embeddings
- Supports semantic similarity search

**`chunks.json`**
- JSON metadata for all chunks
- Each chunk structure:
  ```json
  {
    "id": "chunk_0001",
    "source": "resume" | "github",
    "section": "experience" | "skills" | "github_repo",
    "text": "Full text content of chunk",
    "metadata": {
      "type": "role" | "project" | "readme_section",
      "repo": "Repo name (if GitHub)",
      "heading": "Section heading (if GitHub)",
      "company": "Company name (if experience)"
    }
  }
  ```

### Ingestion Pipeline (`ingest.py`)

**Resume Processing**:
1. Parse `.docx` file using `python-docx`
2. Extract sections: summary, experience, projects, skills, certifications, education, interests
3. Create chunks per section/item
4. Chunk structure preserves section metadata

**GitHub README Processing**:
1. Read each `.md` file
2. Split by heading levels (# / ##)
3. Filter out code blocks and short sections
4. Split long sections (>800 chars) into sub-chunks by paragraph
5. Tag with repo name and heading

**Embedding & Indexing**:
1. Embed all chunks using BGE model
2. L2 normalize embeddings
3. Create FAISS IndexFlatIP with 768 dimensions
4. Save index and chunks metadata

### Retrieval (`rag_retrieve.py`)

**Smart Retrieval with Intent Routing**:

| Condition | Strategy |
|-----------|----------|
| Repo name mentioned (e.g., "Minhash") | Fetch ALL chunks from that repo (context-heavy) |
| GitHub keywords + intent | Semantic search filtered to GitHub only |
| Resume keywords + intent | Semantic search filtered to resume only |
| Default | Semantic search across all sources |

**Semantic Search Parameters**:
- Query prefix: `"Represent this sentence for searching relevant passages: "`
- Top K fetch: 6 (or 20 for repo-specific)
- Relevance threshold: 0.10 (inner product score)
- Multiplier: Fetch 15× more and re-rank

---

## 🤖 Agentic AI - Booking Workflow

### Multi-Step State Machine

```
START
  ↓
[Stage: awaiting_date]
  User provides: date (YYYY-MM-DD or DD-MM-YYYY)
  Action: Validate format → Normalize to YYYY-MM-DD
  Action: Call get_available_slots(date) via Make.com
  Outcome: ✓ Display slots → Next stage
           ✗ No slots available → Ask for different date
  ↓
[Stage: awaiting_slot]
  User provides: time slot (HH:MM)
  Action: Validate slot is in available list
  Outcome: ✓ Slot selected → Next stage
           ✗ Invalid slot → Show available slots again
  ↓
[Stage: awaiting_name]
  User provides: full name
  Action: Store name
  ↓
[Stage: awaiting_email]
  User provides: email address
  Action: Validate email format (regex)
  Outcome: ✓ Email stored → Next stage
           ✗ Invalid email → Ask for valid email
  ↓
[Stage: awaiting_subject]
  User provides: interview title
  Action: Store subject
  ↓
[Stage: awaiting_body]
  User provides: agenda/notes (or "No notes")
  Action: Store body
  Action: Call create_booking(session) via Make.com
  Outcome: ✓ Booking created → Next stage
           ✗ Booking failed → Error message
  ↓
[Stage: completed]
  Response: Confirmation with all details
  Action: Clear session state
END
```

### Booking Workflow Files

**`booking_workflow.py`**
- `is_booking_intent(query)`: Detects if user wants to book
- `start_booking()`: Initiates workflow with greeting
- `handle_booking(session, message)`: State machine handler
- `reset_booking(session_id, conversation_state)`: Cleans up state

**Booking Keywords**:
```python
"interview", "availability", "slot", "call", "meeting", "chat", 
"discuss", "talk", "connect", "schedule", "book"
```

### State Storage

**In-Memory Storage** (`main.py`):
```python
conversation_state = {}  # session_id → {"intent", "stage", "date", "slot", "name", "email", "subject", "body"}
conversation_history = {}  # session_id → [{"role", "content"}, ...]
voice_history = {}  # session_id → [{"role", "content"}, ...]
```

---

## 🚀 API Endpoints

### FastAPI Backend (`main.py` - Port 8001)

#### 1. Health Check
```
GET /
Response: {"status": "healthy", "persona": "Arpit AI"}
```

#### 2. Chat Endpoint (Multi-turn + Booking)
```
POST /chat
Request:
{
  "session_id": "uuid",
  "message": "How many years of experience do you have?"
}

Response:
{
  "answer": "Based on Arpit's resume, he has 5+ years..."
}
```
- Routes to booking workflow if intent detected
- Routes to RAG pipeline if knowledge question
- Maintains conversation history (last 20 turns)

#### 3. Voice RAG Endpoint
```
POST /voice-rag
Request:
{
  "session_id": "uuid",
  "question": "What projects have you built?"
}

Response:
{
  "answer": "Arpit has built several projects including..."
}
```
- Used by Vapi for voice transcription → text response
- Maintains separate voice history (last 20 turns)

#### 4. Availability Endpoint
```
POST /availability
Request:
{
  "date": "2026-05-09"
}

Response:
{
  "slots": ["09:00", "10:00", "11:00", ...]
}
```
- Calls Make.com webhook
- Calculates available slots (9 AM - 5 PM)
- Filters out busy hours

#### 5. Book Interview Endpoint
```
POST /book-interview
Request:
{
  "name": "John Doe",
  "email": "john@example.com",
  "date": "2026-05-09",
  "time": "10:00",
  "subject": "AI Engineer Interview",
  "body": "Technical round"
}

Response:
{
  "success": true
}
```
- Calls Make.com booking webhook
- Creates Google Meet invitation
- Returns success status

---

## 💬 RAG Pipeline - Intent Routing & Retrieval

### Intent Detection (`rag_retrieve.py`)

**Three-layer Intent Routing**:

1. **Repo Detection**
   - Keywords: "arxiv", "minhash", "ats", "sft", "zlib", etc.
   - Maps to exact repo names in chunks.json
   - If detected: Fetch all chunks from repo (up to 20)

2. **Source Filter Detection**
   - **Resume Keywords**: "certif", "skill", "experience", "education", "email", "hire", "strengths"
   - **GitHub Keywords**: "repo", "github", "how does", "implementation", "architecture", "design choice"
   - **Person Triggers**: "arpit", "he", "his", "him", "kumble"
   - Routes to appropriate source or auto-detects

3. **Query Expansion**
   - Maps common phrases to expanded queries
   - Examples:
     - "certif" → "certifications licenses courses completed by Arpit"
     - "hire" → "reasons to hire Arpit skills experience achievements"
     - "tell me about arpit" → "Arpit Kumble summary background experience skills"

### Retrieval Strategy

```python
Retrieve(query, index, embedder, top_k=6, source_filter='auto'):
  1. Embed query with BGE model (add search prefix)
  2. L2 normalize query embedding
  3. Search FAISS with fetch_k = top_k * 15
  4. Re-rank by inner product score
  5. Filter:
     - By relevance threshold (≥0.10)
     - By source_filter if specified (resume vs github)
  6. Return top_k chunks with scores
```

### Context Assembly
- Filters chunks by relevance threshold (0.10)
- Formats each chunk with source info and metadata
- Joins with section separators
- Max context ~2000 tokens

### LLM Generation (GPT-4o-mini)

**System Prompt**:
```
You are a precise, factual Q&A assistant for Arpit Kumble.
- Answer ONLY from provided context chunks
- Be concise (2-5 sentences unless a list)
- If answer not in context: respond "INFORMATION NOT AVAILABLE HERE"
- Synthesize across all context for "why hire", "strengths" questions
- Use conversation history for follow-ups
```

**Input Format**:
```
[System Prompt]
[Conversation History]
[Context Chunks]
Question: [User Question]
```

---

## 🔐 Environment Variables

Create a `.env` file in the backend directory:

```bash
# Make.com Webhooks
MAKE_AVAILABILITY_WEBHOOK=https://hook.make.com/availability/...
MAKE_BOOKING_WEBHOOK=https://hook.make.com/booking/...

# OpenAI API
OPENAI_API_KEY=sk-...

# Optional: Logging
DEBUG=False
```

---

## 📦 Installation & Setup

### Prerequisites
- Python 3.11+
- FAISS (CPU or GPU)
- FastAPI & Uvicorn
- Streamlit
- Sentence Transformers (BGE model)
- OpenAI Python client

### Step 1: Clone & Setup Virtual Environment

```bash
cd sclaer
python -m venv scaler_venv
scaler_venv\Scripts\activate  # Windows
# or
source scaler_venv/bin/activate  # Mac/Linux
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

**Key Dependencies**:
```
fastapi==0.104.1
uvicorn==0.24.0
streamlit==1.28.1
python-docx==0.8.11
sentence-transformers==2.2.2
faiss-cpu==1.7.4
numpy==1.24.3
openai==1.3.0
python-dotenv==1.0.0
aiohttp==3.9.0
requests==2.31.0
```

### Step 3: Generate FAISS Index

```bash
cd backend
python ingest.py
```

This will:
- Parse `data/Resume_Arpit_v2026.docx`
- Parse all README files in `data/repos/`
- Create `index1/resume.index` (FAISS index)
- Create `index1/chunks.json` (metadata)

### Step 4: Start Backend Server

```bash
cd backend
uvicorn main:app --reload --port 8001
```

Backend running at: `http://localhost:8001`

### Step 5: Start Frontend (Streamlit)

```bash
cd frontend
streamlit run app.py
```

Frontend running at: `http://localhost:8501`

### Step 6: Configure External Integrations

1. **Make.com**: Create availability & booking workflows, get webhook URLs
2. **Vapi**: Configure voice agent with backend endpoint
3. **Twilio**: Set up phone number, configure webhook to `/voice-rag`

Add all URLs to `.env` file.

---

## 🧪 Testing

Run test utilities:

```bash
cd backend
python testing.py
```

Manual API tests:

```bash
# Health check
curl http://localhost:8001/

# Chat endpoint
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test-1", "message": "What are your skills?"}'

# Availability
curl -X POST http://localhost:8001/availability \
  -H "Content-Type: application/json" \
  -d '{"date": "2026-05-09"}'
```

---

## 📱 Multi-Channel Usage

### Web Chat (Streamlit)
1. Open `http://localhost:8501`
2. Ask questions or type booking intent
3. Maintain session with Streamlit session state

### Voice (Vapi)
1. Call configured Vapi number
2. Ask questions or say booking phrases
3. Get voice response with text-to-speech
4. Booking workflow works via voice interaction

### SMS/Phone (Twilio)
1. Text or call `+18582640535`
2. Send message (question or booking intent)
3. Receive SMS response or voice response
4. Multi-turn conversation maintained per session

---

## 🔄 Conversation State Management

### Chat Flow (Web + API)

1. **Session Creation**: First request creates unique `session_id`
2. **State Storage**: In-memory dictionaries maintain session state
3. **History Management**: Keeps last 20 turns for context
4. **State Cleanup**: Automatically clears completed booking sessions

### Persistence Note
⚠️ Current implementation uses **in-memory storage**. For production:
- Use Redis for distributed session management
- Persist conversation history to database
- Implement timeout cleanup

---

## 🎓 Knowledge Sources

### Resume Content
- Summary & contact
- Work experience (roles, companies, dates)
- Projects (academic & professional)
- Technical skills & certifications
- Education & interests

### GitHub Repositories
1. **Arxiv Scrapping** - Academic paper downloading
2. **Minhash-LSH-Jaccard** - Deduplication on parquet datasets
3. **Rag Based ATS Analyzer** - Resume screening system
4. **SFT Model Training** - Model fine-tuning
5. **Zlib EPUB Extractor** - E-book processing

Each README is fully indexed with semantic search enabled.

---

## 🛠️ Development Notes

### Adding New Knowledge Sources

1. Add resume data: Update `data/Resume_Arpit_v2026.docx`
2. Add GitHub projects: Place `README.md` in `data/repos/<project-name>/`
3. Re-index: Run `python backend/ingest.py`
4. Restart backend server

### Extending Booking Workflow

Edit `booking_workflow.py`:
- Add new stages to state machine
- Extend `handle_booking()` function
- Update `BOOKING_KEYWORDS` for new triggers

### Customizing Intent Routing

Edit `rag_retrieve.py`:
- Add keywords to `RESUME_KEYWORDS` / `GITHUB_KEYWORDS`
- Update `REPO_ALIASES` for new repos
- Modify `QUERY_EXPANSIONS` for custom phrases

---

## 📊 System Performance

- **Embedding Model**: BGE (768-dim, ~50ms per query)
- **Retrieval**: FAISS semantic search (~10ms for 100+ chunks)
- **LLM Generation**: GPT-4o-mini (~2-3 seconds)
- **Total latency**: ~3-4 seconds per response
- **Concurrent sessions**: In-memory; scale with state management

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| FAISS index not found | Run `python backend/ingest.py` |
| Make.com webhook fails | Verify webhook URLs in `.env`, test in Make.com |
| BGE model download timeout | Pre-download model: `from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-base-en-v1.5')` |
| Streamlit CORS error | CORS middleware in `main.py` handles this |
| Session state lost on restart | Use Redis/database for persistence (see above) |

---

## 📜 License

This project is provided as-is for Arpit's AI persona.

---

## 📧 Contact & Support

- **Resume**: See `data/Resume_Arpit_v2026.docx`
- **GitHub**: Check integrated repositories in `data/repos/`
- **Phone**: +18582640535 (via Twilio)
- **Email**: Available in resume and via agentic workflow

---

## 🚀 Future Enhancements

- [ ] PostgreSQL for conversation persistence
- [ ] Redis for distributed session management
- [ ] Multi-language support with translation
- [ ] Advanced analytics dashboard
- [ ] Custom LLM model fine-tuning
- [ ] Interview recording & post-interview analysis
- [ ] Calendar integration (Google Calendar API)
- [ ] Email notifications for bookings
- [ ] Feedback collection & sentiment analysis

---

**Created**: June 2026  
**Version**: 1.0  
**Status**: Production Ready
