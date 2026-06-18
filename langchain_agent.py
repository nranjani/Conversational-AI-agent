# langchain_agent.py
# This is separate from agent.py
# Used only by FastAPI for Vapi

from tools.booking_tool import book_appointment
from tools.email_tool import send_email_notification
from tools.faq_tool import answer_faq
from tools.receptionist_tool import (
    check_receptionist,
    log_receptionist_request
)
from tools.booking_tool import (
    cancel_booking,
    rebook_appointment
)
from openai import OpenAI
import httpx
import re
import os
from dotenv import load_dotenv

load_dotenv(override=True)

groq_key = os.getenv("GROQ_API_KEY")

client = OpenAI(
    api_key=groq_key,
    base_url="https://api.groq.com/openai/v1",
    http_client=httpx.Client()
)

SYSTEM_MESSAGE = """
You are a Conversational AI Agent for
PlayStayTion Pet Resort in Sadler Texas.

Contact Info:
Phone: 903-207-4408
Email: info@playstaytionpetresort.com
Address: 150 E Greer Road Sadler TX 76264
Hours: 8am to 5pm 7 days a week
Open 365 days a year

Services:
- Standard Boarding: $79 per night
- King Suite: $114 per night
- Peak Standard: $89 per night
- Peak King Suite: $124 per night
- Grooming: Full service available
- Training: Positive reinforcement
- Daycare: Available daily
- Lifetime Care: Available

Grooming Services Include:
- Full bath and blow dry
- Haircut and styling
- Nail trimming and filing
- Ear cleaning
- Teeth brushing
- Coat trimming
- Session takes 1.5 to 2 hours

Key Features:
- Kennel free private rooms
- 24 hour residential supervision
- All activities included free
- No extra charge for medications
- No extra charge for holidays

Activities ALL FREE:
Agility, arts and crafts, dock diving,
doggy puzzles, K9 massage, lure course,
nature hikes, train rides, splash time

Pet Taxi: $1 per mile round trip
Additional pets ride free

Dog Acceptance:
All breeds and ages welcome
Senior dogs welcome
Must have current vaccinations

Check in: 3pm Check out: noon

BOOKING INSTRUCTIONS:
When customer wants to book:
1. Collect pet name, service,
   date, time and phone number
2. When you have all details
   respond with exactly:
   BOOK: pet_name, service, date, time, phone
3. Then confirm the booking

Rules:
- Be warm and friendly always
- Keep responses short and clear
- Always use $ for prices
- Always offer to help further
"""

def extract_booking(text):
    pattern = (
        r"BOOK:\s*([^,]+),\s*([^,]+),"
        r"\s*([^,]+),\s*([^,]+),\s*([^\n]+)"
    )
    match = re.search(pattern, text)
    if match:
        return (
            f"{match.group(1).strip()}, "
            f"{match.group(2).strip()}, "
            f"{match.group(3).strip()}, "
            f"{match.group(4).strip()}, "
            f"{match.group(5).strip()}"
        )
    return None

def process_message(
    user_message: str,
    conversation_history: list = None
) -> str:
    if not conversation_history:
        conversation_history = []

    messages = [
        {
            "role": "system",
            "content": SYSTEM_MESSAGE
        }
    ]

    messages.extend(conversation_history)
    messages.append({
        "role": "user",
        "content": user_message
    })

    try:
        # Try FAQ first
        try:
            faq_answer = answer_faq(user_message)
            if (
                faq_answer and
                "don't have" not in faq_answer
            ):
                return faq_answer
        except Exception as faq_err:
            print(f"FAQ skipped: {faq_err}")

        # Call Groq LLM
        response = (
            client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
        )
        reply = (
            response.choices[0].message.content
        )

        # Check for booking
        booking_details = extract_booking(reply)
        if booking_details:
            try:
                booking_result = book_appointment(
                    booking_details
                )
                send_email_notification(
                    booking_details
                )
                clean_reply = re.sub(
                    r"BOOK:.*", "", reply
                ).strip()
                return (
                    f"{clean_reply}\n\n"
                    f"{booking_result}"
                    if clean_reply
                    else booking_result
                )
            except Exception as book_err:
                print(f"Booking error: {book_err}")
                return reply

        # Check for receptionist
        if "RECEPTIONIST_CHECK" in reply:
            try:
                result = check_receptionist()
                if "OFFICE_OPEN" in result:
                    return result.replace(
                        "OFFICE_OPEN: ", ""
                    )
                return result.replace(
                    "OFFICE_CLOSED: ", ""
                )
            except Exception as rec_err:
                print(f"Receptionist error: {rec_err}")

        # Check for receptionist log
        if "RECEPTIONIST_LOG:" in reply:
            try:
                pattern = (
                    r"RECEPTIONIST_LOG:\s*"
                    r"([^,]+),\s*([^,]+),\s*(.+)"
                )
                match = re.search(pattern, reply)
                if match:
                    result = log_receptionist_request(
                        match.group(1).strip(),
                        match.group(2).strip(),
                        match.group(3).strip()
                    )
                    clean_reply = re.sub(
                        r"RECEPTIONIST_LOG:.*",
                        "",
                        reply
                    ).strip()
                    return (
                        f"{clean_reply}\n\n{result}"
                        if clean_reply
                        else result
                    )
            except Exception as log_err:
                print(f"Log error: {log_err}")

        return reply

    except Exception as e:
        print(f"❌ Error: {e}")
        return (
            "Sorry I ran into an issue. "
            "Please call us at 903-207-4408!"
        )