# 🐾 Conversational AI Agent for Small Business

> A 24/7 AI receptionist deployed for a real pet resort. It answers questions, takes bookings, handles cancellations and reschedules, and captures after-hours requests.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://conversational-ai-agent-uj3hvlnpvewonwm48kyvy6.streamlit.app/)

---

## 📌 Overview

Built for **PlayStayTion Pet Resort** in Sadler, Texas. Before this agent, the business had no way to respond after hours, and every booking was taken manually by phone.

**What the agent does:**
- Answers common questions about hours, pricing and services from a FAQ database
- Takes bookings in conversation and saves them to PostgreSQL
- Cancels and reschedules existing bookings
- Collects contact details after hours so staff can call back
- Emails the admin about every booking, change and after-hours request

---

## 🏗️ Architecture

```
Customer
   ↓
Streamlit web chat
   ↓
Agent (agent.py)
   ├── FAQ match? ──► PostgreSQL faq table ──► answer
   └── otherwise ──► Groq LLM (gpt-oss-120b)
                        ↓ emits a structured command
          ┌─────────────┼──────────────┬──────────────┐
        BOOK:      CANCEL / REBOOK   RECEPTIONIST_CHECK / LOG
          ↓             ↓                  ↓
      bookings      bookings      receptionist_requests
          └─────────────┴──────────────────┘
                        ↓
              Gmail notification to admin
```

The LLM never writes to the database directly. It replies with a structured command such as `BOOK: Max, Grooming, June 6, 10am, 5551234`. The agent parses that command and calls the matching Python tool, which validates the input and runs a parameterized SQL query.

---

## 🛠️ Tech Stack

| Category       | Technology                          |
| -------------- | ----------------------------------- |
| LLM            | Groq (`openai/gpt-oss-120b`)        |
| Backend        | Python 3.11                         |
| Frontend       | Streamlit                           |
| Database       | PostgreSQL (Supabase)               |
| DB driver      | psycopg 3                           |
| Notifications  | Gmail SMTP                          |
| Hosting        | Streamlit Community Cloud           |

---

## ✨ Features

### 1. FAQ answering
- Keyword-based intent matching, then a scoring step that picks the best answer within the matched intent
- FAQ content lives in the `faq` table, so the business can edit answers without touching code
- Results are cached for 5 minutes to avoid querying the database on every message
- Anything without a FAQ match goes to the LLM

### 2. Booking
- Collects pet name, service, date, time and phone number in conversation
- Understands dates like "tomorrow", "Friday", "June 6" and "Apr 05, 2026", and stores them as real `DATE` values
- Asks the customer to rephrase if a date can't be understood, so it never saves an unreadable date

### 3. Cancel and reschedule
- Finds bookings by phone number, pet name and date
- If the same date has several services, asks which one to change
- Status is tracked as `confirmed`, `cancelled` or `rebooked`. Rows are never deleted, so the history is kept.

### 4. After-hours receptionist
- Checks office hours in the resort's time zone
- During hours, gives the phone number and email
- After hours, collects name, phone and question, saves them, and emails the admin

---

## 🗄️ Database Schema

| Table                   | Key columns                                                                                  |
| ----------------------- | -------------------------------------------------------------------------------------------- |
| `bookings`              | `pet_name`, `service_type`, `booking_date` (DATE), `booking_time`, `phone_number`, `status`, `created_at`, `updated_at` |
| `faq`                   | `intent_name`, `question`, `answer`                                                          |
| `receptionist_requests` | `customer_name`, `phone_number`, `query_text`, `created_at`                                  |

See [`schema.sql`](schema.sql) for the full definitions, constraints and indexes. Row Level Security is enabled, so Supabase's public API can't read customer data. The app connects as the table owner.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- A PostgreSQL database (Supabase or Neon free tier works)
- A Groq API key
- A Gmail account with an app password

### Setup
```bash
git clone https://github.com/nranjani/Conversational-AI-agent.git
cd Conversational-AI-agent

python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

pip install -r requirements.txt
```

Create the tables by running `schema.sql` in your database's SQL editor.

### Environment variables
Create a `.env` file:
```
GROQ_API_KEY=your_groq_api_key
DATABASE_URL=postgresql://user:password@host:5432/postgres
EMAIL_ADDRESS=your_gmail
EMAIL_PASSWORD=your_gmail_app_password
ADMIN_EMAIL=where_notifications_go
```

On Streamlit Cloud, add the same keys under **Settings → Secrets**. Put top-level keys such as `DATABASE_URL` above any `[section]` header. On Supabase, use the **Session pooler** connection string.

### Run locally
```bash
streamlit run app.py
```

---

## 📁 Project Structure

```
Conversational-AI-agent/
├── app.py                         # Streamlit chat UI
├── agent.py                       # LLM calls + command routing
├── schema.sql                     # PostgreSQL tables and indexes
├── migrate_sheets_to_postgres.py  # One-time Sheets → Postgres migration
├── requirements.txt
└── tools/
    ├── __init__.py
    ├── db.py                      # Connection handling (commit / rollback)
    ├── booking_tool.py            # Book, cancel, reschedule
    ├── faq_tool.py                # Intent matching + FAQ lookup
    ├── receptionist_tool.py       # Office-hours check + after-hours log
    └── email_tool.py              # Admin notifications
```

---

## 💡 Example Conversations

| Customer says                | Handled by        | Result                               |
| ---------------------------- | ----------------- | ------------------------------------ |
| "What are your hours?"       | FAQ table         | Hours returned instantly             |
| "How much is the king suite?"| FAQ table         | Price returned                       |
| "I want to book grooming"    | LLM → BOOK        | Details collected, row saved, admin emailed |
| "Cancel Max's booking on Friday" | LLM → CANCEL  | Booking found and marked cancelled   |
| "Talk to a person"           | Receptionist tool | Phone number, or after-hours details collected |
| "Do you accept exotic pets?" | LLM               | Answered from the business context in the system prompt |

---

## ⚠️ Limitations and Next Steps

- **Command parsing uses regex.** The LLM's structured replies are parsed with regular expressions. Native tool calling (function calling) would be more reliable.
- **No availability check.** Bookings are recorded without checking capacity, so staff confirm each one.
- **Conversation memory is per session.** Chat history is lost when the page is refreshed.
- **LLM answers outside the FAQ** are limited to the business facts in the system prompt, but they aren't verified against a source.

**Roadmap:** switch to native tool calling, add automated tests for every intent, check capacity before booking, and add SMS or WhatsApp as a second channel.
