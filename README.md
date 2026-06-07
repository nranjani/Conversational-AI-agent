# 🐾 Omnichannel Conversational AI Agent

> AI-powered 24/7 customer engagement system deployed for small businesses — eliminating missed calls, manual bookings, and after-hours service gaps.


---

## 🚀 Live Demo

👉 **streamlit app**
 
---

## 📌 Overview

This project is a **production-deployed agentic AI agent** built for a real small business — PlayStayTion Pet Resort in Sadler, Texas. The system handles customer queries, automates bookings, and provides 24/7 support through an intelligent conversational interface.

### Business Problems Solved:
- ❌ Missed calls after hours
- ❌ Manual booking process
- ❌ No 24/7 customer support
- ❌ After hours service gaps
- ❌ High infrastructure costs

### Solution:
- ✅ 24/7 AI-powered chat interface
- ✅ Automated booking intake
- ✅ FAQ answering from live database
- ✅ After hours receptionist
- ✅ Zero infrastructure cost

---

## 🏗️ Architecture
Customer
↓
Streamlit Web Chat (24/7)
↓
Groq LLM (Llama 3.3 70B)
↓
┌─────────────────────────────┐
│         Use Cases           │
├─────────────────────────────┤
│ 📅 Booking Intake           │
│ ❓ FAQ Lookup               │
│  After Hours Receptionist │
│ 📞 Office Hours Check       │
│ 🚨 Emergency Handling       │
└─────────────────────────────┘
↓
┌─────────────────────────────┐
│         Data Layer          │
│ Google Sheets (booking)     │
│ Google Sheets (FAQ)         │
│ Google Sheets (receptionist)│
└─────────────────────────────┘
↓
Gmail Notifications (admin)

---

## 🛠️ Tech Stack

| Category | Technology |
|---|---|
| **AI/LLM** | Groq LLM (Llama 3.3 70B) |
| **Backend** | Python 3.11 |
| **Frontend** | Streamlit |
| **Database** | Google Sheets API |
| **Notifications** | Gmail API |
| **Hosting** | Streamlit Cloud |
| **Auth** | Google Service Account |
| **Version Control** | GitHub |

---

## ✨ Features

### 1. 🤖 Intelligent Query Handling
- Groq LLM (Llama 3.3 70B) as primary AI brain
- FAQ sheet lookup for known questions
- Automatic fallback to LLM for unknown queries
- 100% query coverage 24/7

### 2. 📅 Automated Booking Intake
- Conversational booking flow
- Collects pet name, service, date, time, phone
- Real time Google Sheets logging
- Instant Gmail notification to admin
- Zero missed bookings

### 3. ❓ FAQ System
- FAQ database stored in Google Sheets
- Intent based matching
- Covers hours, pricing, services, activities,
  pickup, training, boarding, grooming
- Easy to update without code changes

### 4. 🌙 After Hours Receptionist
- Checks office hours automatically
- During hours: connects to staff
- After hours: collects customer details
- Logs to Google Sheets receptionist tab
- Sends admin email notification

### 5. 💰 Zero Infrastructure Cost
- Runs entirely on free tiers
- Google Sheets as database
- Gmail for notifications
- Streamlit Cloud for hosting

---

## 📊 Google Sheets Structure

| Tab | Columns | Purpose |
|---|---|---|
| **booking** | timestamp, pet_name, service_type, date, time, phone_number | Booking logs |
| **FAQ** | intent_name, question, answer | FAQ database |
| **receptionist** | timestamp, name, phone, query | After hours requests |

---

## 🚀 Getting Started

### Prerequisites
```bash
Python 3.11+
Google Cloud Service Account
Groq API Key
Gmail Account with App Password
```

### Installation

```bash
# Clone repo
git clone https://github.com/nranjani/Conversational-AI-agent.git
cd Conversational-AI-agent

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Create `.env` file:

```bash
GROQ_API_KEY=your_groq_api_key
SHEET_NAME=your_google_sheet_name
GMAIL_USER=your_gmail
GMAIL_PASSWORD=your_app_password
```

### Run Locally

```bash
streamlit run app.py
```

---

## 📁 Project Structure

Conversational-AI-agent/
├── app.py                  # Streamlit UI
├── agent.py                # Main AI agent
├── requirements.txt        # Dependencies
├── tools/
│   ├── init.py
│   ├── booking_tool.py     # Booking handler
│   ├── email_tool.py       # Email notifications
│   ├── faq_tool.py         # FAQ lookup
│   └── receptionist_tool.py # Receptionist handler
└── README.md


---

## 💡 Use Cases

| Query | Handler | Result |
|---|---|---|
| "I want to book my dog" | Groq LLM | Booking flow starts |
| "What are your hours?" | FAQ Sheet | Hours returned |
| "How much is king suite?" | FAQ Sheet | Price returned |
| "Do you offer pickup?" | FAQ Sheet | Pickup info returned |
| "Talk to receptionist" | Receptionist | Hours check |
| "Do you accept exotic pets?" | Groq LLM | Intelligent answer |

---

## 📈 Business Impact

| Metric | Result |
|---|---|
| Query coverage | 100% |
| Availability | 24/7 |
| Missed bookings | Zero |
| Infrastructure cost | Zero |
| Response time | < 2 seconds |

---

## 🔮 Future Roadmap

- [ ] Amazon Connect for enterprise voice
- [ ] Amazon Lex V2 for auto intent detection
- [ ] AWS Lambda for serverless logic
- [ ] Twilio WhatsApp integration
- [ ] Power BI analytics dashboard
- [ ] Salesforce CRM integration
- [ ] Multi language support



