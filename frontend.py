import streamlit as st
import requests
import time
import re

# ---------- CSS Styling ----------
def local_css():
    css = """
    html, body, .stApp {
        min-height: 100vh;
        height: 100vh;
        width: 100vw;
        margin: 0 !important;
        padding: 0 !important;
        box-sizing: border-box;
        font-size: 25px;
        background: none !important;
        overflow-x: hidden;
    }

    /* Background Image Fix */
    [data-testid="stAppViewContainer"] {
        background-image: url("https://www.shutterstock.com/image-photo/bible-cross-on-gray-wooden-600nw-2473532869.jpg");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    /* Optional parchment overlay */
    [data-testid="stAppViewContainer"]::before {
        content: "";
        position: absolute;
        top: 0; left: 0;
        width: 100%;
        height: 100%;
        background-image: url("https://www.shutterstock.com/image-photo/bible-cross-on-gray-wooden-600nw-2473532869.jpg");
        background-size: cover;
        opacity: 0.08;
        z-index: -1;
    }

    /* Header (st.header) Styling */
    h1 {
        font-family: 'Georgia', serif;
        color: #4c3762;
        font-weight: bold;
        font-size: 3.5em;
        text-shadow:
            1px 1px 8px rgba(255, 255, 240, 0.7),
            0px 0px 16px rgba(190, 170, 120, 0.6);
        margin-top: 20px;
    }

    /* Subheader (st.subheader) Styling */
    h3 {
        font-family: 'Georgia', serif;
        color: #A9A9A9;
        font-size: 2em;
        font-weight: bold;
        padding: 10px 0;
        border-bottom: 2px solid rgba(255,255,255,0.3);
        text-shadow: 0px 0px 6px rgba(255, 255, 255, 0.4);
    }

    /* Custom title styling */
    .title {
        font-family: 'Georgia', serif;
        color: #4c3762;
        font-weight: bold;
        font-size: 7vw;
        margin: 36px 0;
        text-align: center;
        letter-spacing: 2px;
        text-shadow:
            2px 2px 16px #e9d9b1,
            0px 0px 28px #bfcbe7,
            0px 2px 15px #fff;
        animation: slideDown 0.9s ease-out, glowText 2.8s ease-in-out infinite alternate;
    }
    @keyframes slideDown {
        from { transform: translateY(-20px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    @keyframes glowText {
        from {text-shadow: 2px 2px 16px #dbc786;}
        to {text-shadow: 4px 4px 26px #fffadc;}
    }

    /* Expander styling – Weekly Spiritual Program */
    .stExpander {
        background: rgba(250, 245, 224, 0.35) !important;
        border: 2px solid rgba(255, 255, 255, 0.5);
        border-radius: 12px !important;
        padding: 10px 15px 5px 15px !important;
        box-shadow: 0 4px 16px rgba(80, 70, 50, 0.2);
    }
    .stExpander > div[role="button"] {
        font-family: 'Georgia', serif;
        font-size: 1.3em;
        font-weight: bold;
        color: #4c3762;
    }
    .stExpander > div[role="button"]:hover {
        background-color: rgba(255, 255, 255, 0.2);
    }
    /* Grey text for program info */
    .stExpander label, .stExpander p, .stExpander span {
        color: grey !important;
    }

    /* Chat container (wraps bubbles) */
    .chat-container {
        width: 97vw;
        max-width: 1400px;
        margin: 0 auto;
        display: flex;
        flex-direction: column;
        padding: 3vw 4vw;
        background: rgba(245, 245, 255, 0.37);
        border-radius: 24px;
        box-shadow: 0 6px 26px 0 rgba(80, 63, 114, 0.07);
    }

    /* Message Bubbles */
    .user-msg, .bot-msg {
        padding: 16px 24px;
        margin: 10px 0;
        border-radius: 18px;
        font-size: 1.2em;
        line-height: 1.5;
        max-width: 90%;
    }
    .user-msg {
        background: #d0e6fa;
        align-self: flex-end;
        color: #233466;
    }
    .bot-msg {
        background: #fff5d7;
        align-self: flex-start;
        color: #4c3762;
    }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #d8cbd9 23%, #f7e7a0 100%);
        color: #3a3454;
        font-size: 1.2em;
        font-weight: bold;
        border-radius: 30px;
        border: none;
        padding: 10px 20px;
        cursor: pointer;
    }
    .stButton>button:hover {
        transform: translateY(-2px) scale(1.03);
        background: linear-gradient(90deg,#ded8e8 20%, #fbf5c6 100%);
    }

    .stExpander label, .stExpander p, .stExpander span {
        color: white !important;
    }

    /* Inputs */
    .stSelectbox, .stTextInput {
        font-size: 1.16em !important;
        background: rgba(230,238,255,0.10);
        border-radius: 14px !important;
    }
    """
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


# ---------- Helper to format text ----------
def linkify_and_html(text: str):
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    lines = text.splitlines()
    html = ""
    for ln in lines:
        if ln.strip().startswith("•"):
            if "<ul>" not in html:
                html += "<ul>"
            html += f"<li>{ln.strip('• ').strip()}</li>"
        else:
            html += f"<div>{ln}</div>"
    if "<ul>" in html and not html.endswith("</ul>"):
        html += "</ul>"
    return html


# ---------- Load CSS ----------
local_css()

# ---------- Title ----------
st.markdown("<h1 class='title'>DSCPL – Spiritual AI Companion</h1>", unsafe_allow_html=True)

# ---------- Session State ----------
st.session_state.setdefault("chat_history", [])
st.session_state.setdefault("loading", False)
st.session_state.setdefault("last_message", None)
st.session_state.setdefault("current_program_length", 7)

# ---------- Options ----------
category_options = [
    "Devotion", "Watch Video Verses", "Recreate Bible with Video",
    "Prayer", "Meditation", "Accountability", "Just Chat, Scripture"
]

devotion_topics = [
    "Dealing with Stress", "Overcoming Fear", "Conquering Depression", "Relationships",
    "Healing", "Purpose & Calling", "Anxiety", "Something else..."
]
prayer_topics = [
    "Personal Growth", "Healing", "Family&Friends", "Forgiveness",
    "Finances", "Work&Career", "Something else..."
]
meditation_topics = [
    "Peace", "God's Presence", "Strength", "Wisdom", "Faith", "Something else..."
]
accountability_topics = [
    "Pornography", "Alcohol", "Drugs", "Sex", "Addiction", "Laziness", "Something else..."
]
scripture_topics = [
    "bible"
]

# ---------- UI Layout ----------
st.subheader("Please select your needs:")
col1, col2 = st.columns([1, 1])

with col1:
    category = st.selectbox("Category", category_options)

with col2:
    if category == "Devotion":
        topic = st.selectbox("Choose a Devotion Topic:", devotion_topics)
    elif category == "Watch Video Verses":
        topic = st.text_input("Type a Bible verse/theme for video suggestion:")
    elif category == "Recreate Bible with Video":
        topic = st.text_input("Type a Bible chapter or passage to recreate in video:")
    elif category == "Prayer":
        topic = st.selectbox("Choose a Prayer Topic:", prayer_topics)
    elif category == "Meditation":
        topic = st.selectbox("Choose a Meditation Topic:", meditation_topics)
    elif category == "Accountability":
        topic = st.selectbox("Choose an Accountability Area:", accountability_topics)
    else:
        topic = st.text_input("Just Chat: What's on your mind?")

program_start = False
if category in ["Devotion", "Prayer", "Meditation", "Accountability"]:
    with st.expander("Weekly Spiritual Program (Optional)"):
        program_start = st.checkbox("Start weekly spiritual program for this topic?")
        if program_start:
            days = st.selectbox("Program length (days):", [7, 14, 30], index=0)
            st.session_state["current_program_length"] = days
            st.info("You'll be guided through daily content and reminders.")

send_disabled = not topic.strip() or st.session_state.loading

# ---------- Send Request ----------
def send_request():
    st.session_state.loading = True
    payload = {
        "category": category,
        "topic": topic,
        "start_program": program_start,
        "program_length": st.session_state["current_program_length"],
        "chat_history": st.session_state.chat_history,
    }
    st.session_state.chat_history.append({"role": "user", "content": f"{category}: {topic}"})
    try:
        response = requests.post("http://localhost:8000/chat/", json=payload, timeout=60)
        response.raise_for_status()
        answer = response.json().get("answer", "Sorry, no response.")
        st.session_state.chat_history.append({"role": "AI", "content": answer})
        st.session_state.last_message = answer
    except requests.exceptions.RequestException as e:
        st.session_state.chat_history.append({"role": "AI", "content": f"Error: {e}"})
    finally:
        st.session_state.loading = False

# ---------- Buttons ----------
if st.button("Send", disabled=send_disabled):
    send_request()

if st.button("Clear Chat"):
    st.session_state.chat_history.clear()
    st.session_state.last_message = None

# ---------- Chat Rendering ----------
with st.container():
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f'<div class="user-msg">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bot-msg">{linkify_and_html(msg["content"])}</div>', unsafe_allow_html=True)
