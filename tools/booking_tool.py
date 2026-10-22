# tools/booking_tool.py

from datetime import datetime, timedelta
import re

from tools.db import get_conn

ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def format_date(date_str: str) -> str:
    """
    Convert natural language date
    to formatted date string (YYYY-MM-DD).
    Returns the input unchanged if it can't be parsed.
    """
    date_str = date_str.strip().lower()
    today = datetime.now()

    # Handle relative dates
    if date_str == "today":
        return today.strftime("%Y-%m-%d")

    if date_str == "tomorrow":
        return (
            today + timedelta(days=1)
        ).strftime("%Y-%m-%d")

    # Handle day names
    days = {
        "monday": 0, "tuesday": 1,
        "wednesday": 2, "thursday": 3,
        "friday": 4, "saturday": 5,
        "sunday": 6
    }
    for day, day_num in days.items():
        if day in date_str:
            days_ahead = (day_num - today.weekday()) % 7
            if days_ahead == 0:
                days_ahead = 7
            return (
                today + timedelta(days=days_ahead)
            ).strftime("%Y-%m-%d")

    # Handle formats like "6th June", "June 6", "06/06/2025"
    formats = [
        "%Y-%m-%d",      # 2025-06-06
        "%d %B %Y",      # 06 June 2025
        "%B %d %Y",      # June 06 2025
        "%B %d, %Y",     # June 6, 2025
        "%m/%d/%Y",      # 06/06/2025 (US first)
        "%d/%m/%Y",      # 06/06/2025
        "%b %d, %Y",     # Apr 05, 2026
        "%b %d %Y",      # Apr 05 2026
        "%d %b %Y",      # 05 Apr 2026
        "%d %B",         # 6 June
        "%B %d",         # June 6
        "%b %d",         # Apr 5
        "%d %b",         # 5 Apr
    ]

    # Clean ordinal suffixes (6th -> 6)
    clean_date = re.sub(
        r'(\d+)(st|nd|rd|th)', r'\1', date_str
    ).title()

    for fmt in formats:
        try:
            parsed = datetime.strptime(clean_date, fmt)
            # Add current year if missing
            if parsed.year == 1900:
                parsed = parsed.replace(year=today.year)
            return parsed.strftime("%Y-%m-%d")
        except ValueError:
            continue

    # Return as is if cannot parse
    return date_str


def parse_date_or_none(date_str: str):
    formatted = format_date(date_str)
    return formatted if ISO_DATE.match(formatted) else None


DATE_HELP = (
    "Sorry, I couldn't understand that date. "
    "Could you give it like 'June 6' or '2026-06-06'?"
)


def book_appointment(details: str) -> str:
    try:
        parts = [p.strip() for p in details.split(",")]

        if len(parts) < 5:
            return (
                "I need a few more details. "
                "Please provide: pet name, "
                "service type, date, time, "
                "and phone number."
            )

        pet_name     = parts[0]
        service_type = parts[1]
        date         = parse_date_or_none(parts[2])
        time         = parts[3]
        phone_number = parts[4]

        if not date:
            return DATE_HELP

        with get_conn() as conn:
            conn.execute(
                """
                INSERT INTO bookings
                    (pet_name, service_type, booking_date,
                     booking_time, phone_number)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (pet_name, service_type, date,
                 time, phone_number),
            )

        print("✅ Booking logged!")

        return (
            f"Booking confirmed! "
            f"{pet_name} is booked for "
            f"{service_type} on {date} "
            f"at {time}. "
            f"We will contact you at "
            f"{phone_number}."
        )

    except Exception as e:
        print(f"❌ Booking error: {e}")
        return (
            "Sorry, I couldn't save your booking. "
            "Please call us at 903-207-4408!"
        )


def _find_active_bookings(conn, phone_number, pet_name, date):
    return conn.execute(
        """
        SELECT id, service_type, booking_date, booking_time
        FROM bookings
        WHERE phone_number = %s
          AND lower(pet_name) = lower(%s)
          AND booking_date = %s
          AND status <> 'cancelled'
        ORDER BY created_at
        """,
        (phone_number.strip(), pet_name.strip(), date),
    ).fetchall()


def cancel_booking(
    phone_number: str,
    pet_name: str,
    booking_date: str,
    service_type: str = None
) -> str:
    try:
        date = parse_date_or_none(booking_date)
        if not date:
            return DATE_HELP

        with get_conn() as conn:
            matches = _find_active_bookings(
                conn, phone_number, pet_name, date
            )

            # No match found
            if not matches:
                return (
                    f"No booking found for "
                    f"{pet_name} on {date} "
                    f"with phone {phone_number}. "
                    f"Please check and try again."
                )

            # Multiple services on same date
            if len(matches) > 1 and not service_type:
                service_list = "\n".join(
                    f"{i+1}. {m['service_type']}"
                    for i, m in enumerate(matches)
                )
                return (
                    f"MULTIPLE_SERVICES: "
                    f"I found {len(matches)} "
                    f"bookings for {pet_name} "
                    f"on {date}:\n"
                    f"{service_list}\n\n"
                    f"Which service would you "
                    f"like to cancel?"
                )

            # Find target by service
            if service_type:
                target = next(
                    (m for m in matches
                     if service_type.lower()
                     in m["service_type"].lower()),
                    None,
                )
            else:
                target = matches[0]

            if not target:
                return (
                    f"Could not find "
                    f"{service_type} booking "
                    f"for {pet_name} on {date}."
                )

            # Cancel the booking
            conn.execute(
                """
                UPDATE bookings
                SET status = 'cancelled', updated_at = now()
                WHERE id = %s
                """,
                (target["id"],),
            )

        # Send email (after the DB change is committed)
        from tools.email_tool import send_email_notification
        send_email_notification(
            f"Booking Cancelled\n\n"
            f"Pet: {pet_name}\n"
            f"Service: {target['service_type']}\n"
            f"Date: {date}\n"
            f"Phone: {phone_number}"
        )

        return (
            f"Your booking for {pet_name} "
            f"({target['service_type']} on "
            f"{date}) has been "
            f"cancelled successfully. "
            f"Would you like to reschedule "
            f"for another date?"
        )

    except Exception as e:
        print(f"❌ Cancel error: {e}")
        return (
            "Sorry, I couldn't cancel that booking. "
            "Please call us at 903-207-4408!"
        )


def rebook_appointment(
    phone_number: str,
    pet_name: str,
    old_date: str,
    new_date: str,
    new_time: str,
    service_type: str = None
) -> str:
    try:
        old = parse_date_or_none(old_date)
        new = parse_date_or_none(new_date)
        if not old or not new:
            return DATE_HELP

        with get_conn() as conn:
            matches = _find_active_bookings(
                conn, phone_number, pet_name, old
            )
            if service_type:
                matches = [
                    m for m in matches
                    if service_type.lower()
                    in m["service_type"].lower()
                ]

            if not matches:
                return (
                    f"Could not find booking "
                    f"for {pet_name} on {old}. "
                    f"Please check and try again."
                )

            target = matches[0]
            conn.execute(
                """
                UPDATE bookings
                SET booking_date = %s,
                    booking_time = %s,
                    status       = 'rebooked',
                    updated_at   = now()
                WHERE id = %s
                """,
                (new, new_time, target["id"]),
            )

        # Send email
        from tools.email_tool import send_email_notification
        send_email_notification(
            f"Booking Rescheduled\n\n"
            f"Pet: {pet_name}\n"
            f"Service: {target['service_type']}\n"
            f"Old Date: {old}\n"
            f"New Date: {new}\n"
            f"New Time: {new_time}\n"
            f"Phone: {phone_number}"
        )

        return (
            f"Your booking for "
            f"{pet_name} has been "
            f"rescheduled to "
            f"{new} at {new_time}. "
            f"See you then!"
        )

    except Exception as e:
        print(f"❌ Rebook error: {e}")
        return (
            "Sorry, I couldn't reschedule that booking. "
            "Please call us at 903-207-4408!"
        )