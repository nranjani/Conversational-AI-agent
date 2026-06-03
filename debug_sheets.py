# debug_sheets.py

from dotenv import load_dotenv
load_dotenv()

import gspread
from google.oauth2.service_account import (
    Credentials
)
import os

print("=" * 50)
print("GOOGLE SHEETS DEBUG TEST")
print("=" * 50)

# Step 1
print("\nSTEP 1 - Checking .env...")
sheet_name = os.getenv("SHEET_NAME")
print(f"SHEET_NAME = '{sheet_name}'")

# Step 2
print("\nSTEP 2 - Checking credentials.json...")
if os.path.exists("credentials.json"):
    print("✅ credentials.json found")
else:
    print("❌ credentials.json NOT found!")
    exit()

# Step 3
print("\nSTEP 3 - Connecting...")
try:
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_file(
        "credentials.json",
        scopes=scope
    )
    client = gspread.authorize(creds)
    sheet = client.open(sheet_name)
    print(f"✅ Sheet opened: '{sheet.title}'")

except gspread.exceptions.SpreadsheetNotFound:
    print(f"❌ Sheet '{sheet_name}' NOT found!")
    print("Share sheet with service account email")
    exit()

except Exception as e:
    print(f"❌ Error: {e}")
    exit()

# Step 4
print("\nSTEP 4 - Listing tabs...")
for ws in sheet.worksheets():
    print(f"  → '{ws.title}'")

# Step 5
print("\nSTEP 5 - Testing booking tab...")
try:
    booking_tab = sheet.worksheet("booking")
    print("✅ booking tab found!")

except Exception as e:
    print(f"❌ booking tab error: {e}")
    exit()

# Step 6
print("\nSTEP 6 - Writing test row...")
try:
    booking_tab.append_row([
        "2024-01-01 00:00:00",
        "TestPet",
        "TestService",
        "2024-01-01",
        "10:00 AM",
        "1234567890"
    ])
    print("✅ Test row written!")
    print("Check Google Sheet now!")

except Exception as e:
    print(f"❌ Write error: {e}")

print("\nDEBUG COMPLETE")