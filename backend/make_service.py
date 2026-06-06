import requests
import os
from dotenv import load_dotenv
from datetime import datetime
load_dotenv()

MAKE_AVAILABILITY_WEBHOOK = os.getenv("MAKE_AVAILABILITY_WEBHOOK")
BOOK_INTERVIEW_WEBHOOK = os.getenv("MAKE_BOOKING_WEBHOOK")

def calculate_available_slots(busy_slots):
    working_hours = [
        "09:00",
        "10:00",
        "11:00",
        "12:00",
        "13:00",
        "14:00",
        "15:00",
        "16:00",
        "17:00"
    ]

    busy_hours = []

    for slot in busy_slots:
        start = slot["start"]
        if not start:
            continue

        dt = datetime.fromisoformat(
            start.replace("Z", "+00:00")
        )

        busy_hours.append(
            dt.strftime("%H:00")
        )

    available = [
        hour
        for hour in working_hours
        if hour not in busy_hours
    ]

    return available

def get_available_slots(interview_date):
    response = requests.post(
        MAKE_AVAILABILITY_WEBHOOK,
        json={
            "interviewDate": interview_date
        },
        timeout=30
    )
    print("Status:", response.status_code)
    print("Raw Response:")
    print(response.text)

    
    if response.status_code != 200:
        return []

    data = response.json()

    busy_slots = data.get(
        "busySlots",
        []
    )

    return calculate_available_slots(
        busy_slots
    )


def create_booking(session):
    response = requests.post(
        BOOK_INTERVIEW_WEBHOOK,
        json={
            "candidateName": session["name"],
            "candidateEmail": session["email"],
            "interviewDate": session["date"],
            "startTime": session["slot"],
            "subject": session["subject"],
            "body": session["body"]
        },
        timeout=30
    )

    if response.status_code != 200:
        return None

    return response.json()