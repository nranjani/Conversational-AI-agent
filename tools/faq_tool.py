# tools/faq_tool.py

import gspread
import re
from google.oauth2.service_account import (
    Credentials
)
from dotenv import load_dotenv
import os
import streamlit as st

load_dotenv()

# ─── INTENT KEYWORDS ─────────────────────
INTENT_KEYWORDS = {
    "FAQ_Hours": [
        "what are your hours",
        "when are you open",
        "what time do you open",
        "what time do you close",
        "check in time",
        "check out time",
        "what is check in time",
    "what is check out time",
        "are you open on holiday",
        "how do i contact",
        "opening hours",
        "closing time"
    ],
    "FAQ_Grooming_Services": [
        "what grooming services",
        "list your grooming",
        "list grooming services",
        "grooming services list",
        "grooming includes",         
        "what is included in grooming",
        "do you offer grooming",
        "do you groom",
        "full grooming",
        "grooming include",
        "haircut style",
        "long haired breeds",
        "skin or coat",
        "how long does grooming"
    ],
    "FAQ_KingSuite": [
        "king suite",
        "king room",
        "how much is king",
        "king suite price",
        "king suite cost",
        "king suite size"
    ],
    "FAQ_StandardBoarding": [
        "standard room",
        "standard boarding",
        "how much is standard",
        "standard price",
        "standard cost"
    ],
    "FAQ_Boarding": [
        "how much does boarding cost",
        "how much is boarding",
        "boarding cost",
        "boarding price",
        "do you require vaccination",
        "what vaccinations",
        "do you board all breeds",
        "peak season pricing",
        "can i bring my dog food",
        "can i bring bedding",
        "what is included in boarding"
    ],
    "FAQ_Activities": [
        "what activities do you",
        "are activities included",
        "is there outdoor access",
        "is there a swimming pool",
        "do you have a pool",
        "what activities",
        "agility lessons",
        "dock diving"
    ],
    "FAQ_Pickup": [
        "do you offer pickup",
        "pickup and delivery",
        "pet taxi service",
        "how much is pickup",
        "do you provide pet taxi",
        "which areas do you pick"
    ],
    "FAQ_Training": [
        "do you offer dog training",
        "what is your dog training",
        "how do i book training",
        "what training methods",
        "are you kennel free",
        "training program"
    ],
    "FAQ_Services": [
        "what services do you provide",
        "what services do you offer",
        "what do you offer",
        "what do you provide"
    ]
}

# ─── FIX PRICES ──────────────────────────
def fix_prices(text: str) -> str:
    text = text.replace('`', '$')
    text = re.sub(
        r'(?<!\$)\b(\d+)\b'
        r'(?=\s*(per|night|day|mile))',
        r'$\1',
        text
    )
    return text
# ─── GET SHEET ───────────────────────────
def get_sheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    is_cloud = os.path.exists("/mount/src")

    if is_cloud:
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

    client = gspread.authorize(creds)
    return client.open(sheet_name)
# ─── GET INTENT ──────────────────────────
def get_intent(question: str) -> str:
    question_lower = question.lower().strip()
    for intent, keywords in (
        INTENT_KEYWORDS.items()
    ):
        for kw in keywords:
            if kw in question_lower:
                print(
                    f"Intent: {intent} "
                    f"via '{kw}'"
                )
                return intent
    return None

# ─── ANSWER FAQ ──────────────────────────
def answer_faq(question: str) -> str:
    try:
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]

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

        client  = gspread.authorize(creds)
        sheet   = client.open
        try:
             sheet_name = st.secrets["SHEET_NAME"]
        except Exception:
             sheet_name = os.getenv("SHEET_NAME")
              
        faq_tab  = sheet.worksheet("FAQ")
        faq_data = faq_tab.get_all_records()

        question_lower = question.lower()

        # ─── STEP 1: Match intent ─────────
        matched_intent = get_intent(question)

        if matched_intent:
            all_answers = []
            best_answer = None
            best_score  = 0

            for row in faq_data:
                # Skip empty rows
                if not row.get("intent_name"):
                    continue

                if (
                    row["intent_name"]
                    == matched_intent
                ):
                    all_answers.append(
                        row["answer"]
                    )

                    faq_q = (
                        row["question"].lower()
                    )
                    faq_words = [
                        w for w in faq_q.split()
                        if len(w) > 3
                    ]

                    score = sum(
                        1 for w in faq_words
                        if w in question_lower
                    )
                    # Boost checkout questions
                    if (
                        "check out" in question_lower
                         and "check out" in faq_q
                    ):
                        score += 10

                    # Boost checkin questions
                    if (
                        "check in" in question_lower
                         and "check in" in faq_q
                         and "check out" not in question_lower
                     ):
                        score += 10
                    # Boost price questions
                    if (
                        "how much" in question_lower
                        and (
                            "price" in faq_q
                            or "how much" in faq_q
                            or "cost" in faq_q
                        )
                    ):
                        score += 10

                    if score > best_score:
                        best_score  = score
                        best_answer = row["answer"]

                    if best_answer is None:
                        best_answer = row["answer"]

            # Return best matched answer
            if best_answer:
                return fix_prices(best_answer)

            # Fallback to first answer
            if all_answers:
                return fix_prices(all_answers[0])

        # ─── STEP 2: No match → Groq ──────
        print("No FAQ match → Groq handles")
        return None

    except Exception as e:
        print(f"FAQ error: {e}")
        return None