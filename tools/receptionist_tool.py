# tools/receptionist_tool.py

from datetime import datetime
import pytz

from tools.db import get_conn

# ─── OFFICE HOURS ─────────────────────────
# OFFICE_START_HOUR = 8
# OFFICE_END_HOUR = 10
# Weekdays only (Mon-Fri)
OFFICE_START = 8
OFFICE_END   = 17  # Updated to 5pm
TIMEZONE     = "America/Chicago"

def is_office_open() -> bool:
    tz  = pytz.timezone(TIMEZONE)
    now = datetime.now(tz)
    hour    = now.hour
    weekday = now.weekday()

    # Monday=0 Sunday=6
    is_weekday = weekday <= 4
    is_hours   = OFFICE_START <= hour < OFFICE_END

    return is_weekday and is_hours

def check_receptionist() -> str:
    if is_office_open():
        return (
            "OFFICE_OPEN: "
            "Our receptionist is available now. "
            "Please call us at 903-207-4408 "
            "or email info@playstaytionpetresort.com"
        )
    return (
        "OFFICE_CLOSED: "
        "Sorry we are closed right now. "
        "Would you like to leave your details? "
        "Please share your name, phone number "
        "and your query."
    )

def log_receptionist_request(
    customer_name: str,
    phone_number: str,
    query_text: str
) -> str:
    try:
        # Log to receptionist_requests table
        with get_conn() as conn:
            conn.execute(
                """
                INSERT INTO receptionist_requests
                    (customer_name, phone_number, query_text)
                VALUES (%s, %s, %s)
                """,
                (customer_name, phone_number, query_text),
            )
        print("✅ Receptionist request logged")

        # Send email notification
        from tools.email_tool import send_email_notification
        send_email_notification(
            f"After Hours Receptionist Request\n\n"
            f"Name: {customer_name}\n"
            f"Phone: {phone_number}\n"
            f"Query: {query_text}"
        )

        return (
            f"Thank you {customer_name}! "
            f"We have recorded your request. "
            f"Our team will contact you at "
            f"{phone_number} during office hours "
            f"8am to 5pm Monday to Friday."
        )

    except Exception as e:
        print(f"❌ Receptionist log error: {e}")
        return (
            "Thank you! We have noted your request. "
            "Please call us at 903-207-4408 "
            "during office hours."
        )