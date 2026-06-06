import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from booking_workflow import handle_booking, is_booking_intent, start_booking
from rag_retrieve import ask, load_pipeline
from make_service import get_available_slots, create_booking



app = FastAPI(title="Arpit AI Persona")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Loading RAG pipeline...")
pipeline = load_pipeline(r"C:\Users\Admin\Desktop\sclaer\index1")
print("Pipeline loaded")


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    answer: str


@app.get("/")
def health():
    return {"status": "healthy", "persona": "Arpit AI"}


# In-memory dictionary to hold multi-turn scheduling states
conversation_state = {}
conversation_history = {}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    session = conversation_state.get(req.session_id)

    # 1. Handle an ongoing multi-step scheduling sequence
    if session and session.get("intent") == "booking":
        answer = handle_booking(session, req.message)

        # CRITICAL FIX: Explicitly write back modified state to state store
        conversation_state[req.session_id] = session

        # If the booking flow is fully completed or threw a fallback error, clear the state
        if session.get("stage") == "completed":
            del conversation_state[req.session_id]

        return ChatResponse(answer=answer)

    # 2. Intercept query if user intends to initialize a new booking session
    if is_booking_intent(req.message):
        conversation_state[req.session_id] = {
            "intent": "booking",
            "stage": "awaiting_date",
        }
        return ChatResponse(answer=start_booking())

    # 3. Fallback to standard context-aware RAG pipeline logic
    history = conversation_history.get(req.session_id, [])

    answer = ask(
        question=req.message,
        pipeline=pipeline,
        history=history,
        source_filter="auto",
        verbose=False,
    )

    history.append({
        "role":"user",
        "content" : req.message 
    })

    history.append({
        "role":"assistant",
        "content": answer
    })

    conversation_history[req.session_id] = history[-20:]
    return ChatResponse(answer=answer)

voice_history = {}
@app.post("/voice-rag")
def voice_rag(payload: dict):

    session_id = payload.get("session_id", "default")

    history = voice_history.get(session_id, [])

    answer = ask(
        question=payload["question"],
        pipeline=pipeline,
        history=history,
        source_filter="auto",
        verbose=False,
    )

    history.append({
        "role": "user",
        "content": payload["question"]
    })

    history.append({
        "role": "assistant",
        "content": answer
    })

    voice_history[session_id] = history[-20:]

    return {
        "answer": answer
    }

@app.post("/availability")
def availability(payload: dict):

    print("PAYLOAD RECEIVED:", payload)

    try:
        slots = get_available_slots(payload["date"])

        print("SLOTS:", slots)

        return {
            "slots": slots
        }

    except Exception as e:
        print("ERROR:", str(e))

        return {
            "error": str(e)
        }

@app.post("/book-interview")
def book_interview(payload: dict):

    booking = create_booking({
        "name": payload["name"],
        "email": payload["email"],
        "date": payload["date"],
        "slot": payload["time"],
        "subject": payload.get("subject", "Interview"),
        "body": payload.get("body", "")
    })

    return {
        "success": booking is not None
    }
