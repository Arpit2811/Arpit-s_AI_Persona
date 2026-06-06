# Arpit AI Persona - Loom Video Script

## 📹 Video Overview
**Duration**: ~10-12 minutes  
**Scope**: Project walkthrough, features demo, and architecture explanation  
**Visuals**: Code, running applications, API calls

---

## 🎬 Section 1: Introduction (1:00-1:30)

**[SHOW: Title slide or README.md file]**

"Hello! Today I'm walking you through **Arpit AI Persona**, a hybrid system that combines **Retrieval-Augmented Generation (RAG)** with **Agentic AI** to create an intelligent persona that can:
- Answer questions about someone's resume and GitHub projects using smart semantic search
- Autonomously schedule interviews through a multi-step conversational workflow
- Support multiple interaction channels: web chat, voice calls, and text messages

This is a production-ready system that demonstrates enterprise-level AI architecture. Let me break down what I've built here."

---

## 🎬 Section 2: Project Structure Tour (1:30-2:30)

**[SHOW: File explorer - project root directory]**

"Let me walk you through the project structure. We have several key directories:

**Backend** - This is where the FastAPI server lives. It handles:
- Main API endpoints for chat and booking
- RAG retrieval pipeline with FAISS integration
- Multi-step booking workflow state machine
- Integration with Make.com webhooks

**Frontend** - A Streamlit web application that provides a user interface for:
- Conversational chat with the AI
- Interview booking workflow
- Session management with chat history

**Data** - Contains the knowledge sources:
- Resume in .docx format
- Five GitHub project READMEs that get indexed

**Index1** - This is the FAISS vector database we create. It contains:
- resume.index - the actual vector embeddings
- chunks.json - metadata for all indexed content

The entire system uses a Python virtual environment for dependencies."

---

## 🎬 Section 3: Architecture Explanation (2:30-4:00)

**[SHOW: README.md Architecture section or diagram]**

"Let me explain the architecture. Think of this as having two main pathways:

### **Pathway 1: RAG (Retrieval-Augmented Generation)**

When a user asks a knowledge question like 'What are your skills?', the system:

1. **Intent Detection** - Figures out: Is this a booking request or a knowledge question?
2. **Smart Retrieval** - If it's knowledge:
   - Detects if they're asking about resume or GitHub repos
   - Uses FAISS with semantic search to find relevant chunks
   - BGE model converts the question into a 768-dimensional vector
   - Searches against indexed resume and GitHub content
3. **Context Assembly** - Takes the most relevant chunks and formats them
4. **LLM Generation** - GPT-4o-mini generates a natural response using the context

All of this happens while maintaining conversation history for follow-up questions.

### **Pathway 2: Agentic AI - Booking Workflow**

When a user says something like 'I want to schedule an interview', the system:

1. **Enters Booking Intent** - Recognizes booking keywords
2. **Stage 1: Awaiting Date** - Asks 'Which day?' and validates the date format
3. **Stage 2: Check Availability** - Calls Make.com webhook to fetch available slots from the calendar
4. **Stage 3: Awaiting Slot** - Shows available times, user picks one
5. **Stage 4: Awaiting Name** - Collects candidate name
6. **Stage 5: Awaiting Email** - Validates email format
7. **Stage 6: Awaiting Subject** - Gets interview title
8. **Stage 7: Awaiting Notes** - Gets agenda or notes
9. **Final: Create Booking** - Calls Make.com webhook to create Google Meet invitation

The key here is that the system maintains state across all these steps. It knows exactly where in the workflow the user is.

### **Multi-Channel Integration**

All of this works across three channels simultaneously:
- Web chat (Streamlit)
- Voice calls (Vapi)
- SMS/Phone (Twilio at +18582640535)

Each channel maintains its own conversation history and booking state."

---

## 🎬 Section 4: Technical Deep Dive - Vector Database (4:00-5:00)

**[SHOW: backend/ingest.py or index1/ directory]**

"Let me show you the vector database part. FAISS is a Facebook AI Similarity Search library.

**What we index:**
- Resume: Parsed into sections - experience, skills, education, certifications, projects, interests
- GitHub READMEs: 5 repositories, each split by heading and paragraph

**Embedding Model:**
- BGE (BAAI/bge-base-en-v1.5) - creates 768-dimensional vectors
- These embeddings capture semantic meaning

**How it works:**
When you ask a question, it gets converted to the same 768-dim vector space. Then FAISS performs cosine similarity search to find the most relevant chunks. We use IndexFlatIP which is fast and accurate for semantic search.

The output is chunks.json with all the metadata - what section it came from, what repo, the original text - everything the LLM needs to generate an accurate answer.

We only ingest sources once, so this is computationally efficient."

---

## 🎬 Section 5: Live Demo - Web Interface (5:00-7:00)

**[SHOW: Streamlit app running at localhost:8501]**

"Now let me show you the system in action. Here's the Streamlit web interface.

**Demo 1: Knowledge Question**

[Type or paste a question like: 'What are your main skills?']

'I'll ask it a knowledge question. Watch what happens:
1. The question goes to the backend
2. Intent detection recognizes this is a knowledge question, not a booking
3. The RAG pipeline kicks in
4. It searches the FAISS index
5. Retrieves relevant chunks from the resume
6. Generates a response using GPT-4o-mini'

[Wait for response]

'See how it answered based on actual resume content? The sources are semantic - it found the most relevant skills section. This maintains conversation history too, so follow-up questions work perfectly.'

**Demo 2: Booking Intent**

[Type: 'I want to schedule an interview']

'Now let's trigger the booking workflow. Notice how the system recognized 'schedule an interview' and switched to booking mode.

[Show the multi-step flow:]
- First, it asks for a date
- [Enter: '2026-05-15']
- It validates the date format and checks availability
- Shows available slots
- [Select: '14:30']
- Asks for name, email, interview title, notes
- Finally confirms the booking'

This entire flow is stateful - the system remembers where you are in the process."

---

## 🎬 Section 6: API Endpoints Walkthrough (7:00-8:30)

**[SHOW: Terminal with backend running, then Postman/curl commands]**

"Let me show you the backend API. The FastAPI server is running on port 8001.

**Endpoint 1: /chat - Multi-turn chat with booking detection**
[Show curl or Postman request]
```
POST /chat
{
  "session_id": "user-123",
  "message": "What projects have you built?"
}
```
This endpoint handles both RAG and booking. It maintains conversation history.

**Endpoint 2: /availability - Check calendar availability**
[Show request/response]
This calls Make.com webhook to fetch busy slots and calculates available hours.

**Endpoint 3: /book-interview - Create booking**
[Show request]
Takes all collected information and creates a Google Meet invitation via Make.com.

**Endpoint 4: /voice-rag - For voice agents**
This is what Vapi and Twilio call. It processes voice transcriptions and returns text responses.

All endpoints use session IDs to maintain state across requests. The system supports concurrent users, each with their own conversation context."

---

## 🎬 Section 7: External Integrations (8:30-9:30)

**[SHOW: .env file with webhook URLs, or explain configuration]**

"The system integrates with three external services:

### **Make.com Webhooks**
We use two Make.com workflows:
1. **Availability Check** - When a user picks a date, we query this webhook to fetch calendar busy slots
2. **Booking Creation** - When interview details are confirmed, this webhook creates a Google Meet link

This decouples our application from calendar management - you can swap Make.com for any other calendar API.

### **Twilio**
Phone number: +18582640535
When someone texts or calls this number, it routes to our backend. The system responds via SMS or voice.

### **Vapi - Voice Agent**
Vapi handles voice call transcription and text-to-speech. When someone calls, Vapi:
1. Transcribes their voice to text
2. Sends it to our /voice-rag endpoint
3. Our AI responds with text
4. Vapi converts it back to speech

This architecture means we focus on the AI logic, while specialized services handle voice and SMS."

---

## 🎬 Section 8: Key Technologies (9:30-10:15)

**[SHOW: requirements.txt or architecture diagram]**

"Here are the key technologies powering this:

**FastAPI** - Modern, fast Python web framework
**Streamlit** - Rapid UI prototyping
**FAISS** - Vector similarity search (by Facebook AI)
**Sentence Transformers** - BGE embeddings model
**OpenAI** - GPT-4o-mini for LLM generation
**Make.com** - No-code automation
**Vapi & Twilio** - Voice and SMS

**Key Design Decisions:**

1. **Why FAISS?** - It's fast, scales to millions of vectors, and works great for semantic search
2. **Why BGE?** - It's one of the best open-source embedding models, 768 dimensions is good balance
3. **Why agentic?** - Multi-step workflows are complex; a state machine handles this elegantly
4. **Why Make.com?** - No-code calendaring without building calendar APIs ourselves
5. **Why multi-channel?** - Different users prefer different interfaces - chat, voice, or SMS

The system is production-ready because it handles errors gracefully, maintains state, supports concurrent users, and integrates with enterprise tools."

---

## 🎬 Section 9: Setup & Deployment (10:15-10:45)

**[SHOW: Installation steps from README]**

"Setting this up is straightforward:

1. **Clone the repo and create a virtual environment**
2. **Install dependencies** - pip install -r requirements.txt
3. **Index your sources** - Run ingest.py to create the FAISS index
4. **Configure Make.com** - Set webhook URLs in .env
5. **Start the backend** - uvicorn main:app --port 8001
6. **Start the frontend** - streamlit run app.py
7. **Configure Vapi and Twilio** - Point them to your backend

That's it! The system is now running and accepting requests from all channels.

For production, I'd recommend:
- Use Redis for distributed session management
- Move conversation history to a database
- Deploy FastAPI with a production ASGI server like Gunicorn
- Use environment-specific configurations"

---

## 🎬 Section 10: Conclusion & Use Cases (10:45-11:30)

**[SHOW: README or project summary]**

"This system demonstrates several advanced AI concepts working together:

**Use Cases:**
1. **HR Automation** - AI persona can screen candidates and schedule interviews
2. **Personal Branding** - Creates an AI version of yourself that answers questions 24/7
3. **Customer Support** - Similar approach can power support chatbots
4. **Knowledge Base Q&A** - Any organization can build this for their documentation
5. **Appointment Scheduling** - Autonomous booking agents

**What Makes This Production-Ready:**
- Error handling at every step
- Multi-turn conversation context
- State management for complex workflows
- Scalable architecture with external services
- Multi-channel support
- Easy to extend and customize

**Future Enhancements:**
- Add more knowledge sources
- Fine-tune embeddings for domain-specific language
- Integrate with more calendar systems
- Add feedback loops for continuous improvement
- Implement analytics dashboard

This project shows how to build enterprise-grade AI systems that are useful, scalable, and maintainable. Thank you for watching!"

---

## 📝 Speaking Tips for Loom

1. **Speak naturally** - Imagine explaining to a colleague
2. **Pace yourself** - Slow down when explaining technical concepts
3. **Use pauses** - Let complex ideas sink in
4. **Point and highlight** - Use Loom's drawing tools to highlight important code
5. **Show vs. tell** - Demo working features rather than just describing them
6. **Use analogies** - "State machine is like a form that remembers where you are"
7. **Don't rush** - Better to do 12 minutes than 8 minutes of unclear explanation

---

## ⏱️ Timing Breakdown

- Intro: 0:30s
- Project Structure: 1:00m
- Architecture: 1:30m
- Vector DB: 1:00m
- Web Demo: 2:00m
- API Walkthrough: 1:30m
- External Integrations: 1:00m
- Technologies: 0:45m
- Setup: 0:30m
- Conclusion: 0:45m

**Total: ~11:30 minutes**

---

## 🎯 Screen Recording Checklist

Before you start recording:

- [ ] Terminal 1: Backend running (`uvicorn main:app --reload --port 8001`)
- [ ] Terminal 2: Streamlit running (`streamlit run app.py`)
- [ ] Chrome/Browser: Streamlit app loaded at localhost:8501
- [ ] Editor: README.md, main.py, booking_workflow.py open
- [ ] .env file visible (blur sensitive keys)
- [ ] Zoom level: 125-150% for readability
- [ ] Clear desktop (close unnecessary windows)
- [ ] .env or .gitignore ready to hide sensitive info
- [ ] Test Loom recording settings (resolution 1080p+, audio quality high)

---

## 💡 Pro Tips for the Demo

1. **Pre-test all responses** - Run the chat before recording to ensure fast responses
2. **Have sample questions ready** - Paste them quickly to avoid long typing
3. **Use the chat history** - Show how follow-up questions use conversation context
4. **Demonstrate error handling** - Show what happens with invalid email or dates
5. **Highlight the state machine** - Show all 7 stages of booking workflow
6. **Show logs** - Terminal should display API calls and state transitions
7. **End with impact** - Show completed booking confirmation

Good luck with your Loom video! This script gives you a complete 11-minute walkthrough. 🎉
