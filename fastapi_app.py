# fastapi_app.py

from fastapi import FastAPI, Request
from fastapi.middleware.cors import (
    CORSMiddleware
)
from langchain_agent import process_message
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "status": "PawConnect AI running"
    }

@app.post("/chat")
async def chat_endpoint(request: Request):
    try:
        data = await request.json()
        messages = data.get("messages", [])

        user_message = ""
        conversation_history = []

        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content", "")

            if isinstance(content, list):
                for c in content:
                    if c.get("type") == "text":
                        content = c.get(
                            "text", ""
                        )
                        break

            if role == "user":
                user_message = content
            elif role in ["assistant", "user"]:
                conversation_history.append({
                    "role": role,
                    "content": content
                })

        print(f"User: {user_message}")

        if not user_message:
            return {
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": (
                            "Welcome to PlayStayTion "
                            "Pet Resort! How can I "
                            "help you today?"
                        )
                    }
                }]
            }

        response = process_message(
            user_message,
            conversation_history
        )

        print(f"Agent: {response}")

        return {
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": response
                }
            }]
        }

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return {
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": (
                        "Sorry I ran into an issue. "
                        "Please call us at 903-207-4408!"
                    )
                }
            }]
        }

# ✅ NEW ENDPOINT FOR VAPI
@app.post("/chat/completions")
async def chat_completions(request: Request):
    return await chat_endpoint(request)