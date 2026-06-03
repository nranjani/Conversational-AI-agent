# test_groq.py
from openai import OpenAI
import httpx

client = OpenAI(
    api_key="GROQ_API_KEY",
    base_url="https://api.groq.com/openai/v1",
    http_client=httpx.Client()
)

try:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": "Say hello"
            }
        ],
        max_tokens=50
    )
    print("✅ Key works!")
    print(response.choices[0].message.content)

except Exception as e:
    print(f"❌ Error: {e}")