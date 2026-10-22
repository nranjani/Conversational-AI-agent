# web_api.py
# FastAPI backend for the website chat widget.
# Uses the same agent (agent.py) and tools as the Streamlit demo.
#
# Run locally:  uvicorn web_api:app --reload
# Then open:    http://localhost:8000

import os
import re
import threading
import time
import uuid
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from agent import create_agent

load_dotenv()

WIDGET_DIR = Path(__file__).parent / "widget"

SESSION_TTL_SECONDS = 60 * 60   # forget a chat after 1 hour idle
MAX_SESSIONS = 500              # cap memory use

# Comma-separated list, e.g.
# ALLOWED_ORIGINS=https://playstaytionpetresort.com,https://www.playstaytionpetresort.com
ALLOWED_ORIGINS = [
    o.strip()
    for o in os.getenv("ALLOWED_ORIGINS", "*").split(",")
    if o.strip()
]

app = FastAPI(title="PawConnect Chat API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

# ─── SESSIONS ────────────────────────────
# Each browser tab gets its own agent, so one customer's
# booking details never leak into another's conversation.
_sessions: dict[str, dict] = {}
_lock = threading.Lock()
SESSION_ID = re.compile(r"^[A-Za-z0-9-]{8,64}$")


def _get_session(session_id: str) -> dict:
    now = time.time()
    with _lock:
        # Drop idle sessions
        for sid in [
            s for s, v in _sessions.items()
            if now - v["last_seen"] > SESSION_TTL_SECONDS
        ]:
            del _sessions[sid]

        # Drop the oldest if we're at the cap
        if session_id not in _sessions and len(_sessions) >= MAX_SESSIONS:
            oldest = min(_sessions, key=lambda s: _sessions[s]["last_seen"])
            del _sessions[oldest]

        session = _sessions.setdefault(
            session_id,
            {"chat": create_agent(), "lock": threading.Lock()},
        )
        session["last_seen"] = now
        return session


# ─── API ─────────────────────────────────
class ChatRequest(BaseModel):
    session_id: str | None = None
    message: str = Field(min_length=1, max_length=1000)


class ChatResponse(BaseModel):
    session_id: str
    reply: str


@app.get("/health")
@app.head("/health")
def health():
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    # Plain `def` (not async): FastAPI runs it in a thread pool,
    # so a slow LLM or DB call doesn't block other customers.
    session_id = req.session_id or str(uuid.uuid4())
    if not SESSION_ID.match(session_id):
        raise HTTPException(400, "Invalid session_id")

    session = _get_session(session_id)
    try:
        # One message at a time per session keeps history in order
        with session["lock"]:
            reply = session["chat"](req.message.strip())
    except Exception as e:
        print(f"❌ Chat error: {e}")
        reply = (
            "Sorry I ran into an issue. "
            "Please call us at 903-207-4408!"
        )
    return ChatResponse(session_id=session_id, reply=reply)


# ─── WIDGET FILES ────────────────────────
app.mount("/widget", StaticFiles(directory=WIDGET_DIR), name="widget")


@app.get("/")
def demo_page():
    return FileResponse(WIDGET_DIR / "demo.html")
