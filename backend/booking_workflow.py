import os
import re
import requests
from dotenv import load_dotenv
from backend.make_service import create_booking, get_available_slots


BOOKING_KEYWORDS = [
    "interview",
    "availability",
    "available",
    "slot",
    "call",
    "meeting",
    "chat",
    "discuss",
    "talk",
    "connect",
    "schedule",
    "book",
    "schedule interview",
    "book interview",
    "check availability",
    "available slots",
    "schedule a meeting",
    "book a meeting",
]


# ==========================================================
# INTENT DETECTION
# ==========================================================
def is_booking_intent(query: str) -> bool:
    query = query.lower()

    return any(
        phrase in query
        for phrase in BOOKING_KEYWORDS
    )


# ==========================================================
# START BOOKING
# ==========================================================
def start_booking():
    return (
        "I'd be happy to help schedule an interview.\n\n"
        "Which day would you prefer for the interview?"
    )


# ==========================================================
# HANDLE BOOKING FLOW
# ==========================================================
def handle_booking(session: dict, message: str):
    stage = session.get("stage")

    # --------------------------------------------------
    # STAGE 1: Waiting for Date
    # --------------------------------------------------
    if stage == "awaiting_date":
        date_match = re.search(r"(\d{4}-\d{2}-\d{2})|(\d{1,2}-\d{1,2}-\d{4})", message)
        
        if not date_match:
            return (
                "I couldn't recognize that date format.\n\n"
                "Please provide the date clearly, such as 2026-05-09 or 09-05-2026."
            )
        
        raw_date = date_match.group(0)
        
        if "-" in raw_date and raw_date.split("-")[0].isdigit() and len(raw_date.split("-")[0]) <= 2:
            day, month, year = raw_date.split("-")
            normalized_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        else:
            normalized_date = raw_date

        session["date"] = normalized_date
        print("DATE RECEIVED:", normalized_date)
        try:
            raw_slots = get_available_slots(normalized_date)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return f"Availability lookup failed: {str(e)}"
        if not raw_slots:
            return (
                f"Sorry, there are no available slots for {normalized_date}.\n\n"
                "Please choose another date."
            )

        # Store the raw ISO slots for API submission later
        session["available_slots"] = raw_slots
        session["stage"] = "awaiting_slot"
        
        # Clean timestamps (e.g., "2026-05-09T14:30:00.000Z" -> "14:30") for display
        display_slots = raw_slots

        slot_text = "\n".join([f"• {t}" for t in display_slots[:10]])

        return (
            f"Available slots for {normalized_date}:\n\n"
            f"{slot_text}\n\n"
            "Please select a time slot for the interview (e.g., 14:30)."
        )
   # --------------------------------------------------
    # STAGE 2: Waiting for Slot
    # --------------------------------------------------
    elif stage == "awaiting_slot":

        available_slots = session.get(
            "available_slots",
            []
        )

        if message not in available_slots:
            return (
                f"Sorry, '{message}' is not an available slot.\n\n"
                "Please choose from the listed available slots."
            )

        session["slot"] = message
        session["stage"] = "awaiting_name"

        return (
            f"Perfect! You've selected {message} on {session['date']}.\n\n"
            "Could you please provide your full name for the interview invitation?"
        )

    # --------------------------------------------------
    # STAGE 3: Waiting for Name
    # --------------------------------------------------
    elif stage == "awaiting_name":
        session["name"] = message
        session["stage"] = "awaiting_email"
        return (
            "Thank you.\n\n"
            "Please provide your email address for the interview invitation."
        )

    elif stage == "awaiting_email":
        email_pattern = r"^[^@]+@[^@]+\.[^@]+$"
        if not re.match(email_pattern, message):
            return (
                "That doesn't look like a valid email address.\n\n"
                "Please enter a correct email (e.g., abc.xyz@example.com)."
            )

        session["email"] = message
        session["stage"] = "awaiting_subject"

        return (
            "Please provide the interview title.\n\n"
            "Example: AI Engineer Interview - Round 1"
        )

    elif stage == "awaiting_subject":
        session["subject"] = message
        session["stage"] = "awaiting_body"

        return (
            "Got it.\n\n"
            "Finally, please provide any additional notes or agenda for the interview (or type 'No notes')."
        )
    
    elif stage == "awaiting_body":
        if message.lower() in ["no notes", "no note", "none", "nothing", "n/a"]:
            session["body"] = ""
        else:
            session["body"] = message
        booking = create_booking(session)

        if not booking:
            return (
                "There was an error while booking your interview.\n\n"
                "Please try again later"
            )
        
        session["stage"] = "completed"

        return (
            "Interview scheduled successfully.\n\n"
            f"Title: {session['subject']}\n"
            f"Candidate: {session['name']}\n"
            f"Email: {session['email']}\n"
            f"Date: {session['date']}\n"
            f"Time: {session['slot']}\n\n"
            "Google Meet invitation has been created."
        )

    # --------------------------------------------------
    # COMPLETED
    # --------------------------------------------------
    elif stage == "completed":
        return (
            "Your interview has already been booked.\n\n"
            "If you want to book another interview, please start a new conversation."
        )

    return "Something went wrong during the booking process."


# ==========================================================
# RESET BOOKING
# ==========================================================
def reset_booking(session_id, conversation_state):
    if session_id in conversation_state:
        del conversation_state[session_id]