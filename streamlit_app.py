import streamlit as st
import requests
import base64
import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ──────────────────────────────────────────────
# Page Config
# ──────────────────────────────────────────────
st.set_page_config(page_title="Cerebro AI", page_icon="🧠", layout="wide")

# Configuration — set API_URL and API_TOKEN in .env or environment
API_URL = os.environ.get("API_URL", "")
API_TOKEN = os.environ.get("API_TOKEN", "")

AVATAR_USER = "👤"
AVATAR_ASSISTANT = "🧠"


# ──────────────────────────────────────────────
# Cached Asset & Style Loading
# Decorated with @st.cache_data so disk reads and string building
# happen once per app process, not on every rerun.
# ──────────────────────────────────────────────
@st.cache_data
def load_base64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


@st.cache_data
def build_stylesheet() -> str:
    bg_b64 = load_base64("hacker_bg.png")
    return """
    <style>
    /* ── Google Fonts & Material Icons ── */
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@300;400;500;600;700&display=swap');

    /* ── Root variables ── */
    :root {
        --hacker-green: #00ff00;
        --hacker-green-dim: #00aa00;
        --hacker-bg: #050505;
        --border-color: #004400;
        --bubble-bg-user: #0a0a0a;
        --bubble-bg-assistant: #000000;
        --font-mono: 'Fira Code', 'Courier New', Courier, monospace;
    }

    /* ── Global ── */
    .stApp, .stApp * {
        font-family: var(--font-mono) !important;
        color: var(--hacker-green);
    }

    /* Make containers transparent to see background */
    [data-testid="stAppViewContainer"],
    [data-testid="stHeader"],
    .stApp {
        background: transparent !important;
    }

    .stApp {
        background-color: var(--hacker-bg) !important;
        background-image: linear-gradient(rgba(5, 5, 5, 0.85), rgba(5, 5, 5, 0.85)), url("data:image/png;base64,B64_PLACEHOLDER") !important;
        background-size: 400px;
        background-repeat: repeat;
        background-position: top left;
        background-attachment: fixed !important;
    }

    /* ── Fix Streamlit Material Icons font override ── */
    .stApp .material-symbols-rounded,
    .stApp .material-symbols-outlined,
    .stApp [class*="material-symbols"] {
        font-family: 'Material Symbols Rounded' !important;
        color: var(--hacker-green) !important;
    }

    /* ── Title ── */
    .stApp h1 {
        font-weight: 700 !important;
        font-size: 2rem !important;
        color: var(--hacker-green) !important;
        text-align: center;
        padding: 1rem 0 0.5rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        text-shadow: 0 0 5px rgba(0, 255, 0, 0.5);
    }

    /* ── Subtitle ── */
    .subtitle-text {
        text-align: center;
        color: var(--hacker-green-dim) !important;
        font-size: 0.95rem !important;
        font-weight: 400;
        margin-bottom: 2rem;
    }

    /* ── Main container ── */
    .stMainBlockContainer {
        max-width: 800px;
        margin: 0 auto;
        padding: 2rem !important;
    }

    /* ── Avatar overrides ── */
    .stChatMessage .stAvatar {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    .stChatMessage .stAvatar > div,
    .stChatMessage .stAvatar svg,
    .stChatMessage .stAvatar img {
        display: none !important;
    }
    .stChatMessage .stAvatar::after {
        font-size: 1.2rem;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .stChatMessage[data-testid="stChatMessage-user"] .stAvatar {
        background: transparent !important;
        border: 1px solid var(--hacker-green-dim) !important;
        border-radius: 0 !important;
    }
    .stChatMessage[data-testid="stChatMessage-user"] .stAvatar::after {
        content: ">_";
        color: var(--hacker-green);
        font-family: var(--font-mono);
        font-size: 1rem;
        font-weight: bold;
    }

    .stChatMessage[data-testid="stChatMessage-assistant"] .stAvatar {
        background: transparent !important;
        border: 1px dashed var(--hacker-green) !important;
        border-radius: 0 !important;
    }
    .stChatMessage[data-testid="stChatMessage-assistant"] .stAvatar::after {
        content: "AI";
        color: var(--hacker-green);
        font-family: var(--font-mono);
        font-size: 1rem;
        font-weight: bold;
    }

    /* ── Chat message containers ── */
    .stChatMessage {
        background: var(--bubble-bg-assistant) !important;
        border-radius: 0 !important;
        padding: 1rem 1.2rem !important;
        margin-bottom: 1rem !important;
        border: 1px solid var(--border-color) !important;
        box-shadow: none !important;

        display: flex;
        flex-direction: column !important;
        align-items: center !important;
        text-align: center;
    }

    .stChatMessage[data-testid="stChatMessage-user"] {
        background: var(--bubble-bg-user) !important;
        border-color: var(--border-color) !important;
    }

    /* ── Chat text ── */
    .stChatMessage .stMarkdown p {
        text-align: center !important;
        color: var(--hacker-green) !important;
        font-size: 0.95rem;
        line-height: 1.6;
        font-weight: 400;
        margin: 0;
        width: 100%;
    }

    /* ── Timestamp under messages ── */
    .msg-time {
        font-size: 0.7rem;
        color: var(--hacker-green-dim);
        font-family: var(--font-mono);
        margin-top: 0.8rem;
        text-align: center;
        opacity: 0.7;
        width: 100%;
    }

    /* ── Chat input ── */
    .stChatInput {
        background: transparent !important;
    }
    .stChatInput > div {
        background: var(--hacker-bg) !important;
        border: 1px solid var(--hacker-green) !important;
        border-radius: 0 !important;
        box-shadow: none !important;
        padding-right: 0.5rem;
    }
    .stChatInput > div:focus-within {
        border-color: var(--hacker-green) !important;
        box-shadow: inset 0 0 10px rgba(0, 255, 0, 0.2) !important;
    }
    .stChatInput textarea {
        background: transparent !important;
        color: var(--hacker-green) !important;
        font-family: var(--font-mono) !important;
        font-size: 0.95rem !important;
        text-align: center !important;
    }
    .stChatInput textarea::placeholder {
        color: var(--hacker-green-dim) !important;
        opacity: 0.5;
        text-align: center !important;
    }
    .stChatInput button {
        background: var(--hacker-bg) !important;
        border: 1px solid var(--hacker-green) !important;
        border-radius: 0 !important;
        width: 36px !important;
        height: 36px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: none;
    }
    .stChatInput button:hover {
        background: var(--hacker-green) !important;
        color: var(--hacker-bg) !important;
    }
    .stChatInput button svg {
        display: none !important;
    }
    .stChatInput button::after {
        content: '>>';
        color: inherit;
        font-family: var(--font-mono);
        font-size: 1rem;
        font-weight: bold;
    }
    .stChatInput button:hover::after {
        color: var(--hacker-bg);
    }

    /* ── Buttons (general) ── */
    .stButton > button {
        background: var(--hacker-bg) !important;
        border: 1px solid var(--hacker-green) !important;
        color: var(--hacker-green) !important;
        border-radius: 0 !important;
        font-family: var(--font-mono) !important;
        font-weight: bold !important;
        font-size: 0.85rem !important;
        padding: 0.4rem 1rem;
        text-transform: uppercase;
        transition: none;
    }
    .stButton > button:hover {
        background: var(--hacker-green) !important;
        color: var(--hacker-bg) !important;
    }

    /* ── Spinner ── */
    .stSpinner > div > span {
        color: var(--hacker-green-dim) !important;
        font-family: var(--font-mono) !important;
    }

    /* ── Alerts ── */
    .stAlert {
        border-radius: 0 !important;
        border: 1px solid var(--hacker-green) !important;
        background-color: rgba(0, 50, 0, 0.3) !important;
        color: var(--hacker-green) !important;
    }
    </style>
    """.replace("B64_PLACEHOLDER", bg_b64)


st.markdown(build_stylesheet(), unsafe_allow_html=True)


# ──────────────────────────────────────────────
# Auto-scroll JS (scrolls to latest message)
# ──────────────────────────────────────────────
AUTOSCROLL_JS = """
<script>
document.addEventListener('DOMContentLoaded', () => {
    const observer = new MutationObserver(() => {
        const messages = document.querySelectorAll('[data-testid^="stChatMessage"]');
        if (messages.length > 0) {
            messages[messages.length - 1].scrollIntoView({ behavior: 'smooth', block: 'end' });
        }
    });
    const target = document.querySelector('.stMainBlockContainer');
    if (target) {
        observer.observe(target, { childList: true, subtree: true });
    }
});
// Fallback immediate scroll
setTimeout(() => {
    const msgs = document.querySelectorAll('[data-testid^="stChatMessage"]');
    if (msgs.length > 0) {
        msgs[msgs.length - 1].scrollIntoView({ behavior: 'smooth', block: 'end' });
    }
}, 500);
</script>
"""
st.markdown(AUTOSCROLL_JS, unsafe_allow_html=True)


# ──────────────────────────────────────────────
# API Response Parsing
# ──────────────────────────────────────────────
def parse_api_response(data) -> str:
    if isinstance(data, str):
        return data
    if isinstance(data, dict):
        text = (
            data.get("response")
            or data.get("body")
            or data.get("message")
            or data.get("answer")
            or str(data)
        )
        if isinstance(text, str):
            try:
                inner = json.loads(text)
                if isinstance(inner, dict):
                    return (
                        inner.get("response")
                        or inner.get("message")
                        or inner.get("answer")
                        or str(inner)
                    )
            except (json.JSONDecodeError, TypeError):
                pass
        return text
    return str(data)


# ──────────────────────────────────────────────
# Header
# ──────────────────────────────────────────────
icon_b64 = load_base64("cerebro_icon.png")
st.markdown(
    f'<div style="display: flex; justify-content: center; margin-bottom: 10px;">'
    f'<img src="data:image/png;base64,{icon_b64}" width="120" '
    f'style="border-radius: 50%; border: 2px solid var(--hacker-green); box-shadow: 0 0 15px rgba(0, 255, 0, 0.4);">'
    f'</div>',
    unsafe_allow_html=True,
)
st.title("Cerebro")
st.markdown(
    '<p class="subtitle-text">Neural interface powered by AWS Bedrock — ask anything.</p>',
    unsafe_allow_html=True,
)


# ──────────────────────────────────────────────
# Chat State
# ──────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    avatar = AVATAR_USER if message["role"] == "user" else AVATAR_ASSISTANT
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])
        ts = message.get("timestamp", "")
        if ts:
            st.markdown(f'<div class="msg-time">{ts}</div>', unsafe_allow_html=True)


# ──────────────────────────────────────────────
# Chat Input & Response
# ──────────────────────────────────────────────
if prompt := st.chat_input("Enter your query..."):
    now = datetime.now().strftime("%I:%M %p")

    st.session_state.messages.append({"role": "user", "content": prompt, "timestamp": now})
    with st.chat_message("user", avatar=AVATAR_USER):
        st.markdown(prompt)
        st.markdown(f'<div class="msg-time">{now}</div>', unsafe_allow_html=True)

    assistant_message = ""
    with st.chat_message("assistant", avatar=AVATAR_ASSISTANT):
        with st.spinner("⚡ Processing neural query..."):
            try:
                headers = {"Content-Type": "application/json"}
                if API_TOKEN:
                    headers["x-api-key"] = API_TOKEN

                response = requests.post(
                    API_URL,
                    json={"prompt": prompt},
                    headers=headers,
                    timeout=60,
                )
                response.raise_for_status()
                assistant_message = parse_api_response(response.json())
                st.markdown(assistant_message)

            except requests.exceptions.Timeout:
                assistant_message = "⏱️ The request timed out. Please try again."
                st.error(assistant_message)
            except requests.exceptions.ConnectionError:
                assistant_message = "🔌 Could not connect to the server. Please check your connection."
                st.error(assistant_message)
            except requests.exceptions.HTTPError as e:
                assistant_message = f"❌ API error: {e.response.status_code} — {e.response.text}"
                st.error(assistant_message)
            except Exception as e:
                assistant_message = f"⚠️ An unexpected error occurred: {str(e)}"
                st.error(assistant_message)

        resp_time = datetime.now().strftime("%I:%M %p")
        st.markdown(f'<div class="msg-time">{resp_time}</div>', unsafe_allow_html=True)

    st.session_state.messages.append({
        "role": "assistant", "content": assistant_message, "timestamp": resp_time,
    })
