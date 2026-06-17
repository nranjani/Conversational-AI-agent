import streamlit as st
import streamlit.components.v1 as components
from agent import create_agent

st.set_page_config(
    page_title="Conversational AI Agent",
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

st.title("Conversational AI Agent")
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


# ─── VOICE BUTTONS ───────────────────────
st.markdown("""
    <style>
    .btn-container {
        position: fixed;
        bottom: 80px;
        right: 20px;
        z-index: 999999;
        display: flex;
        flex-direction: column;
        gap: 10px;
    }
    .call-btn {
        background: #25D366;
        color: white;
        padding: 12px 18px;
        border-radius: 50px;
        text-decoration: none;
        font-weight: bold;
        font-size: 14px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        text-align: center;
        display: block;
    }
    .vapi-btn {
        background: #4A90D9;
        color: white;
        padding: 12px 18px;
        border-radius: 50px;
        text-decoration: none;
        font-weight: bold;
        font-size: 14px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        text-align: center;
        display: block;
        cursor: pointer;
        border: none;
    }
    .call-btn:hover { background: #128C7E; }
    .vapi-btn:hover { background: #357ABD; }
    
    /* Modal overlay */
    .vapi-modal {
        display: none;
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.7);
        z-index: 9999999;
        justify-content: center;
        align-items: center;
    }
    .vapi-modal.active {
        display: flex;
    }
    .vapi-modal-content {
        background: white;
        border-radius: 15px;
        width: 90%;
        max-width: 500px;
        height: 80vh;
        position: relative;
        overflow: hidden;
    }
    .vapi-modal-close {
        position: absolute;
        top: 10px;
        right: 15px;
        font-size: 24px;
        cursor: pointer;
        z-index: 99999999;
        background: rgba(0,0,0,0.5);
        color: white;
        border: none;
        border-radius: 50%;
        width: 35px;
        height: 35px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .vapi-iframe {
        width: 100%;
        height: 100%;
        border: none;
    }
    </style>

    <div class="btn-container">
        <a href="tel:+19032074408"
           class="call-btn">
           📞 Call Us
        </a>
        <button 
            class="vapi-btn"
            onclick="openVapi()">
           🎤 Talk to AI
        </button>
    </div>

    <!-- Vapi Modal -->
    <div class="vapi-modal" id="vapiModal">
        <div class="vapi-modal-content">
            <button 
                class="vapi-modal-close"
                onclick="closeVapi()">
                ✕
            </button>
            <iframe
                id="vapiFrame"
                class="vapi-iframe"
                src=""
                allow="microphone; camera"
                allowfullscreen>
            </iframe>
        </div>
    </div>

    <script>
    function openVapi() {
        var modal = document.getElementById('vapiModal');
        var frame = document.getElementById('vapiFrame');
        frame.src = "https://vapi.ai?demo=true&shareKey=a8210a46-6c59-450b-bdab-34eb816d7e2b&assistantId=972d86e7-b499-4e3d-a013-06648c2d4e7f";
        modal.classList.add('active');
    }
    function closeVapi() {
        var modal = document.getElementById('vapiModal');
        var frame = document.getElementById('vapiFrame');
        frame.src = "";
        modal.classList.remove('active');
    }
    </script>
""", unsafe_allow_html=True)