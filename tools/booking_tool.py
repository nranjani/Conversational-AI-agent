# tools/booking_tool.py

import gspread
from google.oauth2.service_account import (
    Credentials
)
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

def get_credentials():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    # Check if running on Streamlit Cloud
    # by checking environment variable
    is_cloud = os.path.exists(
        "/mount/src"
    )

    if is_cloud:
        # Running on Streamlit Cloud
        import streamlit as st
        creds = (
            Credentials.from_service_account_info(
                dict(
                    st.secrets["gcp_service_account"]
                ),
                scopes=scope
            )
        )
        sheet_name = st.secrets["SHEET_NAME"]
    else:
        # Running locally
        base_dir = os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )
        creds_path = os.path.join(
            base_dir, "credentials.json"
        )
        creds = (
            Credentials.from_service_account_file(
                creds_path,
                scopes=scope
            )
        )
        sheet_name = os.getenv("SHEET_NAME")

    return creds, sheet_name

def get_sheet():
    creds, sheet_name = get_credentials()
    client = gspread.authorize(creds)
    print(f"Connecting to: {sheet_name}")
    return client.open(sheet_name)

def book_appointment(details: str) -> str:
    try:
        parts = [
            p.strip()
            for p in details.split(",")
        ]

        if len(parts) < 5:
            return (
                "I need a few more details. "
                "Please provide: pet name, "
                "service type, date, time, "
                "and phone number."
            )

        pet_name     = parts[0]
        service_type = parts[1]
        date         = parts[2]
        time         = parts[3]
        phone_number = parts[4]
        timestamp    = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        print("Connecting to Google Sheets...")
        sheet = get_sheet()

        print("Getting booking tab...")
        bookings_tab = sheet.worksheet("booking")

        print("Writing booking to sheet...")
        bookings_tab.append_row([
            timestamp,
            pet_name,
            service_type,
            date,
            time,
            phone_number
        ])

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
            f"Booking failed. "
            f"Error Type: {type(e).__name__} "
            f"Error: {str(e)}"
        )
 def cancel_booking(
    phone_number: str,
    pet_name: str,
    booking_date: str,
    service_type: str = None
) -> str:
    try:
        sheet = get_sheet()
        tab = sheet.worksheet("booking")
        records = tab.get_all_records()

        # Find all matching rows
        matches = []

        for i, row in enumerate(records):
            phone_match = str(
                row.get("phone_number", "")
            ).strip() == str(
                phone_number
            ).strip()

            pet_match = str(
                row.get("pet_name", "")
            ).lower().strip() == str(
                pet_name
            ).lower().strip()

            date_match = booking_date.lower() in (
                str(row.get("date", "")).lower()
            )

            if phone_match and pet_match and date_match:
                matches.append({
                    "row_index": i + 2,
                    "service": row.get(
                        "service_type", ""
                    ),
                    "date": row.get("date", ""),
                    "time": row.get("time", "")
                })

        # No match found
        if not matches:
            return (
                f"No booking found for "
                f"{pet_name} on {booking_date} "
                f"with phone {phone_number}. "
                f"Please check and try again."
            )

        # Multiple services on same date
        if len(matches) > 1 and not service_type:
            service_list = "\n".join([
                f"{i+1}. {m['service']}"
                for i, m in enumerate(matches)
            ])
            return (
                f"MULTIPLE_SERVICES: "
                f"I found {len(matches)} "
                f"bookings for {pet_name} "
                f"on {booking_date}:\n"
                f"{service_list}\n\n"
                f"Which service would you "
                f"like to cancel?"
            )

        # Find target by service
        target = None
        if service_type:
            for match in matches:
                if service_type.lower() in (
                    match["service"].lower()
                ):
                    target = match
                    break
        else:
            target = matches[0]

        if not target:
            return (
                f"Could not find "
                f"{service_type} booking "
                f"for {pet_name} on "
                f"{booking_date}."
            )

        # Cancel the booking
        tab.update_cell(
            target["row_index"], 7,
            "cancelled"
        )
        tab.update_cell(
            target["row_index"], 8,
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )

        # Send email
        from tools.email_tool import (
            send_email_notification
        )
        send_email_notification(
            f"Booking Cancelled\n\n"
            f"Pet: {pet_name}\n"
            f"Service: {target['service']}\n"
            f"Date: {booking_date}\n"
            f"Phone: {phone_number}"
        )

        return (
            f"Your booking for {pet_name} "
            f"({target['service']} on "
            f"{booking_date}) has been "
            f"cancelled successfully. "
            f"Would you like to reschedule "
            f"for another date?"
        )

    except Exception as e:
        print(f"❌ Cancel error: {e}")
        return f"Cancellation failed: {str(e)}"


def rebook_appointment(
    phone_number: str,
    pet_name: str,
    old_date: str,
    new_date: str,
    new_time: str,
    service_type: str = None
) -> str:
    try:
        sheet = get_sheet()
        tab = sheet.worksheet("booking")
        records = tab.get_all_records()

        found = False

        for i, row in enumerate(records):
            phone_match = str(
                row.get("phone_number", "")
            ).strip() == str(
                phone_number
            ).strip()

            pet_match = str(
                row.get("pet_name", "")
            ).lower().strip() == str(
                pet_name
            ).lower().strip()

            date_match = old_date.lower() in (
                str(row.get("date", "")).lower()
            )

            service_match = True
            if service_type:
                service_match = (
                    service_type.lower() in
                    str(row.get(
                        "service_type", ""
                    )).lower()
                )

            if (
                phone_match and
                pet_match and
                date_match and
                service_match
            ):
                row_index = i + 2

                # Update date
                tab.update_cell(
                    row_index, 4, new_date
                )
                # Update time
                tab.update_cell(
                    row_index, 5, new_time
                )
                # Update status
                tab.update_cell(
                    row_index, 7, "rebooked"
                )
                # Update timestamp
                tab.update_cell(
                    row_index, 8,
                    datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                )
                found = True

                # Send email
                from tools.email_tool import (
                    send_email_notification
                )
                send_email_notification(
                    f"Booking Rescheduled\n\n"
                    f"Pet: {pet_name}\n"
                    f"Service: "
                    f"{row.get('service_type')}\n"
                    f"Old Date: {old_date}\n"
                    f"New Date: {new_date}\n"
                    f"New Time: {new_time}\n"
                    f"Phone: {phone_number}"
                )

                return (
                    f"Your booking for "
                    f"{pet_name} has been "
                    f"rescheduled to "
                    f"{new_date} at {new_time}. "
                    f"See you then!"
                )

        if not found:
            return (
                f"Could not find booking "
                f"for {pet_name} on {old_date}. "
                f"Please check and try again."
            )

    except Exception as e:
        print(f"❌ Rebook error: {e}")
        return f"Rebooking failed: {str(e)}"   