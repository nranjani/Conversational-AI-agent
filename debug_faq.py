# debug_faq.py
from dotenv import load_dotenv
load_dotenv()

import gspread
from google.oauth2.service_account import (
    Credentials
)
import os

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_file(
    'credentials.json',
    scopes=scope
)

client = gspread.authorize(creds)
sheet = client.open(os.getenv("SHEET_NAME"))
faq_tab = sheet.worksheet("FAQ")

# Show ALL rows
print("ALL FAQ DATA:")
print("-" * 50)
all_data = faq_tab.get_all_records()
for i, row in enumerate(all_data):
    print(f"Row {i+1}:")
    print(f"  intent: {row['intent_name']}")
    print(f"  question: {row['question']}")
    print(f"  answer: {row['answer'][:50]}...")
    print()