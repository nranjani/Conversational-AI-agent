import streamlit as st
from agent import create_agent

st.set_page_config(
    page_title="Paw Connect AI",
    page_icon="🐾",
    layout="centered"
)

st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stChatMessage {
        border-radius: 10px;
        padding: 10px;
        margin: 5px 0;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🐾 Paw Connect AI")
st.caption(
    "PlayStayTion Pet Resort — "
    "Available 24/7 for bookings "
    "and questions"
)

st.divider()

with st.sidebar:
    st.image(
        "https://img.icons8.com/color/96/dog.png",
        width=80
    )
    st.header("PlayStayTion Pet Resort")
    st.markdown("""
    **Services:**
    - Grooming
    - Boarding
    - Daycare
    - Training
    - Lifetime Care

    **Hours:**
    - 8am to 5pm Daily
    - Open 365 days a year

    **Location:**
    - 150 E Greer Road
    - Sadler TX 76264

    **Contact:**
    - 903-207-4408
    - info@playstaytionpetresort.com
    """)
    st.divider()
    if st.button("Clear Chat"):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "Hi! Welcome to PlayStayTion "
                    "Pet Resort! How can I help?"
                )
            }
        ]
        st.session_state.chat = create_agent()
        st.rerun()
    st.caption("Powered by Paw Connect AI")

if "chat" not in st.session_state:
    with st.spinner(
        "Starting Paw Connect AI..."
    ):
        st.session_state.chat = create_agent()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hi! Welcome to PlayStayTion "
                "Pet Resort!\n\n"
                "I can help you with:\n"
                "- Booking grooming, "
                "boarding or daycare\n"
                "- Questions about services\n"
                "- Hours and pricing info\n\n"
                "How can I help you today?"
            )
        }
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if prompt := st.chat_input(
    "Type your message here..."
):
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner(
            "Paw Connect is thinking..."
        ):
            try:
                response = (
                    st.session_state.chat(
                        prompt
                    )
                )
            except Exception as e:
                response = (
                    "Sorry I ran into an issue. "
                    "Please call us directly at "
                    "903-207-4408!"
                )
        st.write(response)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })