# agent.py

from openai import OpenAI
import httpx
from tools.booking_tool import book_appointment
from tools.email_tool import send_email_notification
from tools.faq_tool import answer_faq
from tools.receptionist_tool import (
    check_receptionist,
    log_receptionist_request
)
from dotenv import load_dotenv
import os
import re

load_dotenv(override=True)

# ─── GET GROQ API KEY ────────────────────
try:
    import streamlit as st
    groq_key = st.secrets["GROQ_API_KEY"]
except Exception:
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

Grooming Services Include:
- Full bath and blow dry
- Haircut and styling
- Nail trimming and filing
- Ear cleaning
- Teeth brushing
- Coat trimming
- Sanitary trim
- Skin and coat check
- All breeds welcome
- Custom styles available
- Session takes 1.5 to 2 hours

BOOKING INSTRUCTIONS:
When customer wants to book:
1. Collect pet name, service,
   date, time and phone number
2. When you have all details
   respond with exactly:
   BOOK: pet_name, service, date, time, phone
3. Then confirm the booking

RECEPTIONIST INSTRUCTIONS:
When customer EXPLICITLY says:
- talk to receptionist
- speak to human
- talk to staff
- speak to someone
- talk to a person
ONLY THEN respond with: RECEPTIONIST_CHECK

When customer provides their details
after being told office is closed
respond with exactly:
RECEPTIONIST_LOG: name, phone, query

CANCEL/RESCHEDULE INSTRUCTIONS:
When customer wants to cancel:
1. Ask for phone number and pet name
2. Ask for booking date
3. Respond with:
   CANCEL: phone_number, pet_name, date
4. If system shows multiple services
   ask which service to cancel
5. Then respond with:
   CANCEL: phone_number, pet_name,
           date, service_type
6. After cancellation ask:
   Would you like to reschedule?
7. If yes collect new date and time
   respond with:
   REBOOK: phone_number, pet_name,
           old_date, new_date,
           new_time, service_type

When customer wants to reschedule:
1. Ask phone number and pet name
2. Ask current booking date
3. If multiple services ask which one
4. Ask new date and time
5. Respond with:
   RESCHEDULE: phone_number, pet_name,
               old_date, new_date,
               new_time, service_type

Rules:
- Be warm and friendly always
- Keep responses short and clear
- Always use $ for prices not backticks
- Never use markdown backticks for prices
- Always offer to help further
- For receptionist use RECEPTIONIST_CHECK
- Collect name phone query after hours
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

def create_agent():
    history = [
        {
            "role": "system",
            "content": SYSTEM_MESSAGE
        }
    ]

    def chat(user_message: str) -> str:
        history.append({
            "role": "user",
            "content": user_message
        })

        # ─── FAQ CHECK ────────────────────
        faq_answer = answer_faq(user_message)
        if (
            faq_answer and
            "don't have" not in faq_answer
        ):
            history.append({
                "role": "assistant",
                "content": faq_answer
            })
            return faq_answer

        # ─── GROQ LLM ─────────────────────
        try:
            response = (
                client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=history,
                    max_tokens=500,
                    temperature=0.7
                )
            )
            reply = (
                response.choices[0].message.content
            )
        except Exception as e:
            print(f"❌ Groq error: {e}")
            return (
                "Sorry I ran into an issue. "
                "Please call us at 903-207-4408!"
            )

        # ─── RECEPTIONIST CHECK ───────────
        if "RECEPTIONIST_CHECK" in reply:
            result = check_receptionist()
            if "OFFICE_OPEN" in result:
                final_reply = result.replace(
                    "OFFICE_OPEN: ", ""
                )
            else:
                final_reply = result.replace(
                    "OFFICE_CLOSED: ", ""
                )
            history.append({
                "role": "assistant",
                "content": final_reply
            })
            return final_reply

        # ─── RECEPTIONIST LOG ─────────────
        if "RECEPTIONIST_LOG:" in reply:
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
                final_reply = (
                    f"{clean_reply}\n\n{result}"
                    if clean_reply
                    else result
                )
                history.append({
                    "role": "assistant",
                    "content": final_reply
                })
                return final_reply

        # ─── CANCEL CHECK ────────────────
        if "CANCEL:" in reply:
            pattern_with_service = (
                r"CANCEL:\s*([^,]+),\s*"
                r"([^,]+),\s*([^,]+),\s*(.+)"
            )
            pattern_no_service = (
                r"CANCEL:\s*([^,]+),\s*"
                r"([^,]+),\s*([^\n,]+)"
            )
            match = re.search(
                pattern_with_service, reply
            )
            if match:
                from tools.booking_tool import (
                    cancel_booking
                )
                result = cancel_booking(
                    match.group(1).strip(),
                    match.group(2).strip(),
                    match.group(3).strip(),
                    match.group(4).strip()
                )
            else:
                match = re.search(
                    pattern_no_service, reply
                )
                if match:
                    from tools.booking_tool import (
                        cancel_booking
                    )
                    result = cancel_booking(
                        match.group(1).strip(),
                        match.group(2).strip(),
                        match.group(3).strip()
                    )
                else:
                    result = (
                        "Could not process "
                        "cancellation."
                    )

            if "MULTIPLE_SERVICES:" in result:
                clean_result = result.replace(
                    "MULTIPLE_SERVICES: ", ""
                )
                history.append({
                    "role": "assistant",
                    "content": clean_result
                })
                return clean_result

            clean_reply = re.sub(
                r"CANCEL:.*", "", reply
            ).strip()
            final_reply = (
                f"{clean_reply}\n\n{result}"
                if clean_reply
                else result
            )
            history.append({
                "role": "assistant",
                "content": final_reply
            })
            return final_reply

        # ─── REBOOK CHECK ────────────────
        if "REBOOK:" in reply:
            pattern = (
                r"REBOOK:\s*([^,]+),\s*"
                r"([^,]+),\s*([^,]+),\s*"
                r"([^,]+),\s*([^,\n]+)"
                r"(?:,\s*(.+))?"
            )
            match = re.search(pattern, reply)
            if match:
                from tools.booking_tool import (
                    rebook_appointment
                )
                result = rebook_appointment(
                    match.group(1).strip(),
                    match.group(2).strip(),
                    match.group(3).strip(),
                    match.group(4).strip(),
                    match.group(5).strip(),
                    match.group(6).strip()
                    if match.group(6) else None
                )
                clean_reply = re.sub(
                    r"REBOOK:.*", "", reply
                ).strip()
                final_reply = (
                    f"{clean_reply}\n\n{result}"
                    if clean_reply
                    else result
                )
                history.append({
                    "role": "assistant",
                    "content": final_reply
                })
                return final_reply

        # ─── RESCHEDULE CHECK ────────────
        if "RESCHEDULE:" in reply:
            pattern = (
                r"RESCHEDULE:\s*([^,]+),\s*"
                r"([^,]+),\s*([^,]+),\s*"
                r"([^,]+),\s*([^,\n]+)"
                r"(?:,\s*(.+))?"
            )
            match = re.search(pattern, reply)
            if match:
                from tools.booking_tool import (
                    rebook_appointment
                )
                result = rebook_appointment(
                    match.group(1).strip(),
                    match.group(2).strip(),
                    match.group(3).strip(),
                    match.group(4).strip(),
                    match.group(5).strip(),
                    match.group(6).strip()
                    if match.group(6) else None
                )
                clean_reply = re.sub(
                    r"RESCHEDULE:.*", "", reply
                ).strip()
                final_reply = (
                    f"{clean_reply}\n\n{result}"
                    if clean_reply
                    else result
                )
                history.append({
                    "role": "assistant",
                    "content": final_reply
                })
                return final_reply

        # ─── BOOKING CHECK ────────────────
        booking_details = extract_booking(reply)
        if booking_details:
            booking_result = book_appointment(
                booking_details
            )
            send_email_notification(
                booking_details
            )
            clean_reply = re.sub(
                r"BOOK:.*", "", reply
            ).strip()
            final_reply = (
                f"{clean_reply}\n\n"
                f"{booking_result}"
            )
            history.append({
                "role": "assistant",
                "content": final_reply
            })
            return final_reply

        history.append({
            "role": "assistant",
            "content": reply
        })
        return reply

    return chat