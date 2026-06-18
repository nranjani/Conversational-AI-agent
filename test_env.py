# test_env.py
from dotenv import load_dotenv
load_dotenv()
import os

groq = os.getenv('GROQ_API_KEY')
sheet = os.getenv('SHEET_NAME')

print(f"GROQ key: {groq[:10] if groq else 'NOT FOUND'}")
print(f"SHEET: {sheet}")