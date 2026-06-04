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