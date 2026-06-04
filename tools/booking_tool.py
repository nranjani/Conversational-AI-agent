# tools/booking_tool.py

import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dotenv import load_dotenv
import os

import streamlit as st
load_dotenv()

def get_sheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    try:
        # Streamlit Cloud secrets
        import streamlit as st
        creds_dict = dict(
            st.secrets["gcp_service_account"]
        )
        creds = (
            Credentials.from_service_account_info(
                creds_dict,
                scopes=scope
            )
        )
    except Exception:
        # Local credentials.json
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

    client     = gspread.authorize(creds)
    
    try:
        import streamlit as st
        sheet_name = st.secrets["SHEET_NAME"]
    except Exception:
        sheet_name = os.getenv("SHEET_NAME")
    
    print(f"Connecting to sheet: {sheet_name}")
    return client.open(sheet_name)


def book_appointment(details: str) -> str:
    try:
        parts = [p.strip() for p in details.split(",")]
        
        if len(parts) < 5:
            return (
                "I need a few more details to complete "
                "your booking. Please provide: "
                "pet name, service type, date, "
                "time, and phone number."
            )
        
        pet_name       = parts[0]
        service_type   = parts[1]
        date           = parts[2]
        time           = parts[3]
        phone_number   = parts[4]
        timestamp      = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        print("Connecting to Google Sheets...")
        sheet        = get_sheet()
        
        print("Getting Bookings tab...")
        bookings_tab = sheet.worksheet("booking")
        
        print("Writing booking to sheet...")
        bookings_tab.append_row([
            timestamp,
            pet_name, 
            service_type, 
            date, 
            time, 
            phone_number, 
            
        ])

        return (
            f"Booking confirmed! "
            f"{pet_name} is booked for "
            f"{service_type} on {date} "
            f"at {time}. "
            f"We will contact you at "
            f"{phone_number}."
        )

    except gspread.exceptions.SpreadsheetNotFound:
        return (
            "ERROR: Spreadsheet not found. "
            "Check SHEET_NAME in .env matches "
            "your Google Sheet name exactly"
        )
    
    except gspread.exceptions.WorksheetNotFound:
        return (
            "ERROR: Worksheet Bookings not found. "
            "Make sure tab is named exactly Bookings"
        )
    
    except Exception as e:
        return (
            f"Booking failed. "
            f"Error Type: {type(e).__name__} "
            f"Error: {str(e)}"
        )