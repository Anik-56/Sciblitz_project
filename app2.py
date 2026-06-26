import streamlit as st
from groq import Groq
import json
import re
import base64
from datetime import datetime, timedelta
import random
from streamlit_mic_recorder import mic_recorder
import plotly.graph_objects as go

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="CampusZen AI",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Inject CSS ───────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Sora:wght@400;600;700&display=swap');

:root {
    --bg:        #0d1117;
    --surface:   #161b22;
    --surface2:  #1c2330;
    --border:    #30363d;
    --accent:    #7c6af7;
    --accent2:   #56cfb2;
    --accent3:   #f87171;
    --text:      #e6edf3;
    --muted:     #8b949e;
    --radius:    14px;
    --calm-accent: #60a5fa;
    --calm-surface: #0f1f35;
}

html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Inter', sans-serif;
}

[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }

#MainMenu, footer { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }

.zen-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
    transition: border-color .2s;
}
.zen-card:hover { border-color: var(--accent); }

.stat-grid { display: grid; grid-template-columns: repeat(4,1fr); gap: .8rem; margin-bottom:1.4rem; }
.stat-tile {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1rem 1.2rem;
    text-align: center;
}
.stat-tile .num  { font-family:'Sora',sans-serif; font-size:1.8rem; font-weight:700; }
.stat-tile .lbl  { font-size:.75rem; color:var(--muted); margin-top:.2rem; }
.stat-tile.purple .num { color: var(--accent); }
.stat-tile.teal  .num { color: var(--accent2); }
.stat-tile.red   .num { color: var(--accent3); }
.stat-tile.gold  .num { color: #f0a500; }

.hero {
    background: linear-gradient(135deg, #1a1145 0%, #0d2a22 100%);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 2rem 2.4rem;
    margin-bottom: 1.4rem;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content:'';
    position:absolute; top:-60px; right:-60px;
    width:220px; height:220px;
    background: radial-gradient(circle, rgba(124,106,247,.25) 0%, transparent 70%);
    border-radius:50%;
}
.hero h1 { font-family:'Sora',sans-serif; font-size:2rem; font-weight:700; margin:0; }
.hero p  { color:var(--muted); margin:.4rem 0 0; font-size:.95rem; }
.pill {
    display:inline-block;
    background: rgba(124,106,247,.15);
    border: 1px solid rgba(124,106,247,.4);
    color: var(--accent);
    border-radius:99px; padding:.2rem .8rem;
    font-size:.75rem; font-weight:600;
    margin-bottom:.6rem;
}

/* ── Normal chat bubbles ── */
.bubble-user {
    background: rgba(124,106,247,.15);
    border: 1px solid rgba(124,106,247,.3);
    border-radius: 14px 14px 4px 14px;
    padding: .75rem 1rem;
    margin: .5rem 0 .5rem 20%;
    color: var(--text);
    font-size:.92rem;
}
.bubble-ai {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 14px 14px 14px 4px;
    padding: .75rem 1rem;
    margin: .5rem 20% .5rem 0;
    color: var(--text);
    font-size:.92rem;
    line-height:1.6;
}

/* ── Calm mode chat bubbles (crisis detected) ── */
.bubble-user-calm {
    background: rgba(96,165,250,.12);
    border: 1px solid rgba(96,165,250,.25);
    border-radius: 14px 14px 4px 14px;
    padding: .75rem 1rem;
    margin: .5rem 0 .5rem 20%;
    color: var(--text);
    font-size:.92rem;
}
.bubble-ai-calm {
    background: #0f1f35;
    border: 1px solid rgba(96,165,250,.2);
    border-radius: 14px 14px 14px 4px;
    padding: .75rem 1rem;
    margin: .5rem 20% .5rem 0;
    color: #c9dff7;
    font-size:.92rem;
    line-height:1.6;
}

.bubble-label { font-size:.7rem; color:var(--muted); margin-bottom:.2rem; }

[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stSelectbox"] select {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(124,106,247,.15) !important;
}

button[kind="primary"], [data-testid="stButton"] > button {
    background: var(--accent) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: opacity .2s !important;
}
button[kind="primary"]:hover, [data-testid="stButton"] > button:hover {
    opacity: .85 !important;
}

.quiz-opt {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: .7rem 1rem;
    margin: .3rem 0;
    cursor: pointer;
    transition: border-color .2s, background .2s;
    color: var(--text);
    font-size: .9rem;
    width: 100%;
    text-align: left;
}
.quiz-opt:hover { border-color: var(--accent); background: rgba(124,106,247,.08); }
.quiz-opt.correct { border-color: var(--accent2); background: rgba(86,207,178,.1); }
.quiz-opt.wrong   { border-color: var(--accent3); background: rgba(248,113,113,.1); }

.section-head {
    font-family:'Sora',sans-serif;
    font-size:1.1rem; font-weight:600;
    margin: 1rem 0 .6rem;
    display:flex; align-items:center; gap:.5rem;
}

.chat-scroll { max-height:420px; overflow-y:auto; padding-right:.4rem; }
.chat-scroll::-webkit-scrollbar { width:4px; }
.chat-scroll::-webkit-scrollbar-track { background:transparent; }
.chat-scroll::-webkit-scrollbar-thumb { background:var(--border); border-radius:4px; }

.plan-row {
    display:grid; grid-template-columns: 100px 1fr 80px;
    gap:.6rem; padding:.6rem .8rem;
    border-bottom:1px solid var(--border);
    font-size:.87rem; align-items:center;
}
.plan-row:last-child { border-bottom:none; }
.plan-day { color:var(--accent); font-weight:600; }
.badge {
    display:inline-block;
    padding:.15rem .55rem; border-radius:99px;
    font-size:.72rem; font-weight:600;
}
.badge-high { background:rgba(248,113,113,.15); color:var(--accent3); }
.badge-med  { background:rgba(240,165,0,.15);   color:#f0a500; }
.badge-low  { background:rgba(86,207,178,.15);  color:var(--accent2); }

.feature-badge {
    display:inline-flex; align-items:center; gap:.3rem;
    background: rgba(86,207,178,.1);
    border: 1px solid rgba(86,207,178,.3);
    color: var(--accent2);
    border-radius:99px; padding:.2rem .7rem;
    font-size:.72rem; font-weight:600;
    margin-left:.5rem;
}

/* ── SOS / Crisis side panel ── */
.crisis-panel {
    background: linear-gradient(160deg, #0f1f35 0%, #0d1117 100%);
    border: 1px solid rgba(96,165,250,.3);
    border-radius: var(--radius);
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
    animation: fadeSlideIn .4s ease;
}
@keyframes fadeSlideIn {
    from { opacity:0; transform: translateX(12px); }
    to   { opacity:1; transform: translateX(0); }
}
.crisis-panel h4 {
    font-family:'Sora',sans-serif;
    color: #60a5fa;
    font-size:.95rem;
    margin:0 0 .5rem;
}
.crisis-panel p {
    font-size:.82rem;
    color:#94b8d8;
    margin:.3rem 0;
    line-height:1.5;
}
.helpline-item {
    background: rgba(96,165,250,.07);
    border: 1px solid rgba(96,165,250,.18);
    border-radius: 8px;
    padding: .45rem .7rem;
    font-size:.8rem;
    color: #c9dff7;
    margin: .35rem 0;
}

/* ── Breathing circle ── */
.breath-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: .8rem 0 .5rem;
}
.breath-circle {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(96,165,250,.5) 0%, rgba(96,165,250,.1) 70%);
    border: 2px solid rgba(96,165,250,.5);
    animation: breathe 8s ease-in-out infinite;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: .72rem;
    color: #60a5fa;
    font-weight: 600;
    text-align: center;
    letter-spacing: .02em;
}
@keyframes breathe {
    0%,100% { transform: scale(1);   opacity: .7; box-shadow: 0 0 0 0 rgba(96,165,250,.2); }
    40%      { transform: scale(1.5); opacity: 1;  box-shadow: 0 0 0 16px rgba(96,165,250,.0); }
    60%      { transform: scale(1.5); opacity: 1; }
}
.breath-label {
    margin-top:.6rem;
    font-size:.75rem;
    color:#60a5fa;
    font-weight:500;
    letter-spacing:.04em;
}
            
/* ── SOS Modal ── */
.sos-overlay {
    position: fixed; inset: 0;
    background: rgba(0,0,0,0.72);
    z-index: 9998;
    backdrop-filter: blur(4px);
}
.sos-modal {
    position: fixed; top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    z-index: 9999;
    width: min(480px, 92vw);
    background: linear-gradient(160deg, #0d1e35 0%, #0d1117 100%);
    border: 1px solid rgba(96,165,250,.35);
    border-radius: 20px;
    padding: 2rem 2rem 1.6rem;
    animation: modalIn .35s cubic-bezier(.22,1,.36,1);
    box-shadow: 0 24px 80px rgba(0,0,0,.7);
}
.sos-close {
    position: absolute; top: 1rem; right: 1rem;
    width: 28px; height: 28px;
    background: rgba(255,255,255,.07);
    border: 1px solid rgba(255,255,255,.12);
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    cursor: pointer;
    font-size: .85rem; color: #8b949e;
    transition: background .2s;
}
.sos-close:hover { background: rgba(255,255,255,.14); color: #e6edf3; }
@keyframes modalIn {
    from { opacity:0; transform: translate(-50%, -46%) scale(.96); }
    to   { opacity:1; transform: translate(-50%, -50%) scale(1); }
}
.sos-title {
    font-family: 'Sora', sans-serif;
    font-size: 1.25rem; font-weight: 700;
    color: #c9dff7; margin: 0 0 .5rem;
}
.sos-body {
    font-size: .9rem; color: #94b8d8;
    line-height: 1.65; margin-bottom: 1.1rem;
}
.sos-divider {
    border: none;
    border-top: 1px solid rgba(96,165,250,.12);
    margin: 1rem 0;
}
.sos-section-label {
    font-size: .7rem; font-weight: 700;
    color: #60a5fa; text-transform: uppercase;
    letter-spacing: .08em; margin-bottom: .5rem;
}
.sos-helpline {
    background: rgba(96,165,250,.07);
    border: 1px solid rgba(96,165,250,.16);
    border-radius: 9px; padding: .45rem .8rem;
    font-size: .8rem; color: #c9dff7;
    margin-bottom: .35rem;
    display: flex; justify-content: space-between; align-items: center;
}
.sos-helpline b { color: #93c5fd; }
.breath-mini {
    display: flex; align-items: center; gap: .9rem;
    background: rgba(96,165,250,.06);
    border: 1px solid rgba(96,165,250,.14);
    border-radius: 10px; padding: .6rem .9rem;
    margin-bottom: .8rem;
}
.breath-dot {
    width: 34px; height: 34px; border-radius: 50%;
    background: radial-gradient(circle, rgba(96,165,250,.5) 0%, rgba(96,165,250,.05) 80%);
    border: 1.5px solid rgba(96,165,250,.5);
    flex-shrink: 0;
    animation: breathe 8s ease-in-out infinite;
}
.breath-mini-text { font-size: .8rem; color: #93c5fd; line-height: 1.5; }
            
/* ── Normal side panel (non-crisis) ── */
.side-tip-card {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1rem 1.2rem;
    margin-bottom: .8rem;
}
.side-tip-card .tip-label {
    font-size:.7rem;
    color: var(--muted);
    font-weight:600;
    text-transform:uppercase;
    letter-spacing:.06em;
    margin-bottom:.4rem;
}
.side-tip-card p {
    font-size:.83rem;
    color: var(--text);
    line-height:1.5;
    margin:0;
}

/* ── Mental support zone on dashboard ── */
.mental-zone {
    background: linear-gradient(135deg, #0f1a2e 0%, #111827 100%);
    border: 1px solid rgba(96,165,250,.2);
    border-radius: var(--radius);
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
}
.mental-zone .zone-head {
    font-family:'Sora',sans-serif;
    font-size:1rem;
    font-weight:700;
    color:#60a5fa;
    margin:0 0 .9rem;
    display:flex; align-items:center; gap:.5rem;
}
.mental-feature-row {
    display:flex; gap:.7rem; flex-wrap:wrap; margin-bottom:.9rem;
}
.mental-feature-chip {
    background: rgba(96,165,250,.08);
    border: 1px solid rgba(96,165,250,.2);
    border-radius: 8px;
    padding: .45rem .85rem;
    font-size:.8rem;
    color: #93c5fd;
    font-weight:500;
    cursor:pointer;
    transition: background .2s;
}
.mental-feature-chip:hover { background: rgba(96,165,250,.15); }

/* ── Mood chart container ── */
.mood-chart-wrap {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: .8rem;
    margin-bottom:.8rem;
}
</style>
""", unsafe_allow_html=True)


# ── PDF text extractor ────────────────────────────────────────
def extract_pdf_text(uploaded_file) -> str:
    try:
        import fitz
        pdf_bytes = uploaded_file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = ""
        for page_num, page in enumerate(doc):
            text += f"\n--- Page {page_num + 1} ---\n"
            text += page.get_text()
        doc.close()
        return text.strip()
    except ImportError:
        return "__PYMUPDF_MISSING__"
    except Exception as e:
        return f"__ERROR__: {e}"


def extract_image_text(uploaded_file) -> str:
    try:
        img_bytes = uploaded_file.read()
        b64 = base64.b64encode(img_bytes).decode()
        mime = uploaded_file.type if uploaded_file.type else "image/jpeg"
        
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        resp = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
                    {"type": "text", "text": "Extract all text from this image of notes. Return only the raw text content, preserving structure. Do not add any commentary."}
                ]
            }],
            max_tokens=2048
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"__ERROR__: {e}"


# ── Crisis detection ──────────────────────────────────────────
def detect_crisis(text: str) -> bool:
    """Use AI to assess whether a message signals emotional crisis."""
    system = """You are a mental health triage assistant. 
You are a mental health safety classifier.

Your ONLY task is to determine whether a student's message indicates an immediate or potentially serious emotional or psychological crisis.
Respond with ONLY one word:
YES or NO

Return **YES** if the message expresses or strongly implies any of the following:

* Suicidal thoughts, wishes to die, or wanting to end their life.
* Thoughts, urges, or plans of self-harm.
* Feeling that others would be better off without them.
* Feeling trapped with no way out.
* Extreme hopelessness or believing life has no meaning.
* Wanting to disappear, not wake up, or stop existing.
* Severe emotional breakdown, panic, or inability to stay safe.
* Statements indicating they may harm themselves, even indirectly.
* Any wording that reasonably suggests an imminent mental health crisis, even if not stated explicitly.

Return **NO** if the message is primarily about:

* Exam stress or academic pressure.
* Anxiety about grades, deadlines, or presentations.
* Feeling tired, overwhelmed, lonely, frustrated, or sad without crisis indicators.
* Relationship problems, homesickness, or everyday emotional struggles.
* Requests for advice, motivation, study help, or emotional support that do not suggest immediate danger.

When uncertain, prioritize safety. If the message contains credible signs of a crisis, respond YES.

Output exactly one word:

YES or NO"""


    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": text}
            ],
            max_tokens=5,
            temperature=0.0,   # deterministic
        )
        answer = resp.choices[0].message.content.strip().upper()
        return answer.startswith("YES")
    except Exception:
        return False   # fail safe: don't trigger on API error


# ── Mood helpers ──────────────────────────────────────────────
MOOD_SCALE = {
    "😊 Great": 5,
    "😐 Okay": 3,
    "😔 Low": 2,
    "😰 Stressed": 1,
    "😤 Frustrated": 2,
}

def _seed_demo_mood_log():
    """Seed 7 days of demo mood data so chart is never empty in a demo."""
    sample_moods = ["😊 Great", "😐 Okay", "😔 Low", "😰 Stressed", "😤 Frustrated"]
    weights      = [0.25, 0.30, 0.15, 0.20, 0.10]
    log = []
    for i in range(7, 0, -1):
        day = datetime.now() - timedelta(days=i)
        mood = random.choices(sample_moods, weights=weights)[0]
        log.append({
            "mood": mood,
            "time": day.strftime("%H:%M"),
            "date": day.strftime("%b %d"),
            "datetime": day.isoformat(),
        })
    return log

def build_mood_chart(mood_log: list) -> go.Figure:
    if not mood_log:
        return None

    color_map = {5: "#56cfb2", 3: "#7c6af7", 2: "#f0a500", 1: "#f87171"}
    emoji_map = {"😊 Great": "😊", "😐 Okay": "😐", "😔 Low": "😔", "😰 Stressed": "😰", "😤 Frustrated": "😤"}

    entries = mood_log[-30:]  # last 30 entries regardless of day
    labels, scores, colors, hovers = [], [], [], []

    for entry in entries:
        score = MOOD_SCALE.get(entry["mood"], 3)
        # X axis label: show time if same day, else "Jun 27 14:32"
        if entry.get("datetime"):
            dt = datetime.fromisoformat(entry["datetime"])
            label = dt.strftime("%b %d %H:%M")
        else:
            label = f"{entry.get('date','')} {entry.get('time','')}"
        labels.append(label)
        scores.append(score)
        colors.append(color_map.get(score, "#7c6af7"))
        hovers.append(f"{entry['mood']}<br>{label}")

    fig = go.Figure()

    # Filled area
    fig.add_trace(go.Scatter(
        x=labels, y=scores,
        mode="lines+markers",
        line=dict(color="#60a5fa", width=2, shape="spline"),
        marker=dict(color=colors, size=9, line=dict(color="#0d1117", width=2)),
        fill="tozeroy",
        fillcolor="rgba(96,165,250,0.06)",
        hovertemplate="%{customdata}<extra></extra>",
        customdata=hovers,
    ))

    # Highlight last point
    fig.add_trace(go.Scatter(
        x=[labels[-1]], y=[scores[-1]],
        mode="markers",
        marker=dict(color=colors[-1], size=14, line=dict(color="#fff", width=2)),
        hoverinfo="skip",
        showlegend=False,
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=10, b=40),
        height=180,
        xaxis=dict(
            showgrid=False, zeroline=False,
            tickfont=dict(color="#8b949e", size=9),
            showline=False,
            tickangle=-35,
            # Only show max 6 ticks to avoid crowding
            nticks=6,
        ),
        yaxis=dict(
            showgrid=True, gridcolor="rgba(255,255,255,0.05)",
            zeroline=False, range=[0.5, 5.5],
            tickfont=dict(color="#8b949e", size=9),
            showline=False,
            tickvals=[1, 2, 3, 5],
            ticktext=["😰", "😔", "😐", "😊"],
        ),
        showlegend=False,
        hovermode="x unified",
    )
    return fig

# ── Session state ────────────────────────────────────────────
def init_state():
    defaults = {
        "page": "Dashboard",
        "mental_msgs": [],
        "academic_msgs": [],
        "quiz_data": None,
        "quiz_answered": {},
        "quiz_score": 0,
        "plan_result": "",
        "summary_result": "",
        "mood_today": None,
        "mood_log": [],
        "session_count": 0,
        "pdf_files": {},
        "pdf_active": [],
        # Mental Health chat input state
        "mental_input_counter": 0,
        "mental_voice_id": None,
        "academic_input_counter": 0,
        "academic_voice_id": None,
        # NEW — mental health enhancements
        "crisis_detected": False,
        "chat_theme": "normal",       # "normal" | "calm"
        "breathing_active": False,
        "demo_mood_seeded": False,    # ensures we only seed once
        "sos_popup_dismissed": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# Seed demo mood data once per session so chart always looks populated
if not st.session_state.demo_mood_seeded and not st.session_state.mood_log:
    st.session_state.mood_log = _seed_demo_mood_log()
    st.session_state.demo_mood_seeded = True


# ── AI helper ────────────────────────────────────────────────
def ai(system_prompt, user_prompt, max_tokens=1024):
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=max_tokens,
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"⚠️ AI service unavailable: {e}"


# ── Whisper transcription ────────────────────────────────────
def transcribe_audio(audio) -> str | None:
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        result = client.audio.transcriptions.create(
            file=("audio.wav", audio["bytes"]),
            model="whisper-large-v3"
        )
        return result.text
    except Exception as e:
        st.error(f"Transcription failed: {e}")
        return None


def get_active_pdf_text() -> str:
    if not st.session_state.pdf_active:
        return ""
    parts = []
    for name in st.session_state.pdf_active:
        text = st.session_state.pdf_files.get(name, "")
        parts.append(f"--- FILE: {name} ---\n{text}")
    return "\n\n".join(parts)


# ── Mental system prompt — switches tone in calm mode ────────
def get_mental_system(calm: bool = False) -> str:
    base = """You are CampusZen's compassionate mental health companion for university students.
Your role:
- Listen empathetically and validate feelings first before giving advice
- Help with stress, anxiety, academic pressure, loneliness, burnout, relationships
- Use warm, non-clinical language appropriate for a college student
- Offer practical coping strategies when appropriate
- Never diagnose. Never be dismissive. Always be kind.
"""
    if calm:
        base += """
RIGHT NOW, this student is in pain — possibly in crisis. This is the most important moment in the conversation.

Your entire approach shifts:
- DO NOT give advice, tips, or bullet points
- DO NOT ask multiple questions
- DO NOT minimize or rush past what they said
- First: acknowledge their pain directly. Use their words back to them. Make them feel truly heard.
- Then: say one thing that reminds them they are not alone — not a cliché, something human
- Then: offer one tiny, immediate anchor (e.g. "Can you take one slow breath with me right now?")
- End by gently opening the door: ask ONE simple question, like "Can you tell me a little more about what's been happening?"
- Your tone is: quiet, unhurried, present. Like a friend sitting beside them in a dark room.
- Never mention helplines yourself — the app has already shown them. Just be here.
"""
    return base


# ── Shared mental-health send logic ─────────────────────────
def _mental_send(user_message: str):
    """Append user msg → detect crisis → call AI → append reply."""
    st.session_state.mental_msgs.append({"role": "user", "content": user_message})

    # Crisis detection — runs on every user message
    if detect_crisis(user_message):
        st.session_state.crisis_detected = True
        st.session_state.chat_theme = "calm"

    calm = st.session_state.chat_theme == "calm"
    system_prompt = get_mental_system(calm=calm)

    history_str = "\n".join(
        f"{m['role']}: {m['content']}" for m in st.session_state.mental_msgs
    )
    with st.spinner("Thinking..."):
        reply = ai(system_prompt, history_str)
    st.session_state.mental_msgs.append({"role": "assistant", "content": reply})


# ── Sidebar nav ──────────────────────────────────────────────
pages = [
    ("🏠", "Dashboard"),
    ("💚", "Mental Health"),
    ("📚", "Academic Help"),
    ("🧩", "Quiz Generator"),
    ("📅", "Study Planner"),
    ("📝", "Note Summarizer"),
]

with st.sidebar:
    st.markdown("""
    <div style='padding:.6rem 0 1.2rem'>
        <div style='font-family:Sora,sans-serif;font-size:1.3rem;font-weight:700;color:#e6edf3'>
            🌿 CampusZen
        </div>
        <div style='font-size:.75rem;color:#8b949e;margin-top:.2rem'>AI Companion for Varsity Life</div>
    </div>
    """, unsafe_allow_html=True)

    for icon, name in pages:
        if st.button(f"{icon}  {name}", key=f"nav_{name}", use_container_width=True):
            st.session_state.page = name
            st.rerun()

    st.markdown("---")

    st.markdown(
    "<div style='font-size:.8rem;font-weight:600;color:#e6edf3;margin-bottom:.4rem'>📄 Upload Study Material</div>",
    unsafe_allow_html=True
    )
    sidebar_file = st.file_uploader(
        "PDF or image of notes",
        type=["pdf", "png", "jpg", "jpeg", "webp"],
        key="sidebar_upload",
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    if sidebar_file:
        for f in sidebar_file:
            if not hasattr(f, 'name'):
                continue
            if f.name not in st.session_state.pdf_files:
                with st.spinner(f"Reading {f.name}..."):
                    if f.type == "application/pdf":
                        extracted = extract_pdf_text(f)
                    else:
                        extracted = extract_image_text(f)

                    if extracted.startswith("__PYMUPDF_MISSING__"):
                        st.error("PyMuPDF not installed.")
                    elif extracted.startswith("__ERROR__"):
                        st.error(f"Could not read {f.name}: {extracted[9:]}")
                    else:
                        st.session_state.pdf_files[f.name] = extracted
                        st.success(f"✅ Loaded: {f.name}")

    if st.session_state.pdf_files:
        st.markdown(
            "<div style='font-size:.78rem;font-weight:600;color:#e6edf3;margin:.6rem 0 .3rem'>🎯 Ask AI from:</div>",
            unsafe_allow_html=True
        )
        st.session_state.pdf_active = st.multiselect(
            "Select files",
            options=list(st.session_state.pdf_files.keys()),
            default=st.session_state.pdf_active if st.session_state.pdf_active else list(st.session_state.pdf_files.keys()),
            label_visibility="collapsed"
        )

        total_chars = sum(len(v) for k, v in st.session_state.pdf_files.items() if k in st.session_state.pdf_active)
        active_count = len(st.session_state.pdf_active)
        st.markdown(f"""
        <div style='background:rgba(86,207,178,.08);border:1px solid rgba(86,207,178,.25);
            border-radius:8px;padding:.5rem .7rem;font-size:.75rem;color:#56cfb2;margin-top:.3rem'>
            {active_count} file(s) selected<br>
            <span style='color:#8b949e'>{total_chars:,} chars loaded</span>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🗑️ Remove All Files", key="remove_pdf"):
            st.session_state.pdf_files = {}
            st.session_state.pdf_active = []
            st.rerun()

    st.markdown("---")
    st.markdown(
        "<div style='font-size:.75rem;color:#8b949e;text-align:center'>Powered by LLaMA 3.3 70B<br>& Gemma 3 27B • Free Forever</div>",
        unsafe_allow_html=True
    )

page = st.session_state.page


# ══════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ══════════════════════════════════════════════════════════════
if page == "Dashboard":

    # Determine time of day for greeting
    hour = datetime.now().hour
    if hour < 12:
        greeting = "Good morning 🌤️"
        sub = "Start your day with intention. What's on the agenda?"
    elif hour < 17:
        greeting = "Good afternoon ☀️"
        sub = "Hope your study session is going well. How are you holding up?"
    elif hour < 21:
        greeting = "Good evening 🌙"
        sub = "Wrapping up the day? Remember to rest — you've earned it."
    else:
        greeting = "Still up? 🌌"
        sub = "It's late. Your wellbeing matters more than one more chapter."

    st.markdown(f"""
    <div class='hero'>
        <div class='pill'>✦ AI-Powered Campus Companion</div>
        <h1>{greeting}</h1>
        <p>{sub}</p>
    </div>
    """, unsafe_allow_html=True)

    mood_count = len(st.session_state.mood_log)
    quiz_count = len(st.session_state.quiz_answered)

    st.markdown(f"""
    <div class='stat-grid'>
        <div class='stat-tile purple'><div class='num'>{len(st.session_state.mental_msgs)//2}</div><div class='lbl'>Mental Health Chats</div></div>
        <div class='stat-tile teal'><div class='num'>{len(st.session_state.academic_msgs)//2}</div><div class='lbl'>Academic Questions</div></div>
        <div class='stat-tile gold'><div class='num'>{quiz_count}</div><div class='lbl'>Quiz Questions Done</div></div>
        <div class='stat-tile red'><div class='num'>{mood_count}</div><div class='lbl'>Mood Check-ins</div></div>
    </div>
    """, unsafe_allow_html=True)

    # ── Mental Support Zone ───────────────────────────────────
    st.markdown("""
    <div class='mental-zone'>
        <div class='zone-head'>💙 Mental Support Center</div>
    """, unsafe_allow_html=True)

    mz_col1, mz_col2 = st.columns([1.1, 1])

    with mz_col1:
        st.markdown("<div style='font-size:.78rem;color:#8b949e;font-weight:600;margin-bottom:.5rem;text-transform:uppercase;letter-spacing:.05em'>Your Mood This Week</div>", unsafe_allow_html=True)

        fig = build_mood_chart(st.session_state.mood_log)
        if fig:
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.markdown("<p style='color:#8b949e;font-size:.85rem'>Log your first mood to see your trend.</p>", unsafe_allow_html=True)

        # Mood streak
        streak = len([e for e in st.session_state.mood_log if e.get("date")])
        if streak > 0:
            st.markdown(f"<p style='font-size:.78rem;color:#60a5fa;margin-top:-.3rem'>🔥 {streak}-day mood streak — keep it up!</p>", unsafe_allow_html=True)

    with mz_col2:
        st.markdown("<div style='font-size:.78rem;color:#8b949e;font-weight:600;margin-bottom:.5rem;text-transform:uppercase;letter-spacing:.05em'>How Are You Feeling?</div>", unsafe_allow_html=True)

        moods = ["😊 Great", "😐 Okay", "😔 Low", "😰 Stressed", "😤 Frustrated"]
        mood_cols = st.columns(len(moods))
        for i, mood in enumerate(moods):
            with mood_cols[i]:
                if st.button(mood.split()[0], key=f"dash_mood_{i}", help=mood):
                    st.session_state.mood_today = mood
                    now = datetime.now()
                    st.session_state.mood_log.append({
                        "mood": mood,
                        "time": now.strftime("%H:%M"),
                        "date": now.strftime("%b %d"),
                        "datetime": now.isoformat(),
                    })
                    st.rerun()

        if st.session_state.mood_today:
            score = MOOD_SCALE.get(st.session_state.mood_today, 3)
            if score <= 2:
                mood_msg = "It's okay to not be okay. The chat is here for you. 💙"
                mood_color = "#60a5fa"
            elif score == 3:
                mood_msg = "Staying steady — that counts. 💚"
                mood_color = "#56cfb2"
            else:
                mood_msg = "Glad you're doing well! Keep that energy. ✨"
                mood_color = "#7c6af7"
            st.markdown(f"<p style='font-size:.82rem;color:{mood_color};margin-top:.4rem'>{mood_msg}</p>", unsafe_allow_html=True)

        st.markdown("<div style='margin-top:.7rem;font-size:.78rem;color:#8b949e;font-weight:600;margin-bottom:.4rem;text-transform:uppercase;letter-spacing:.05em'>Mental Health Tools</div>", unsafe_allow_html=True)

        if st.button("Open Mental Health Chat 💚", key="dash_mental_cta", use_container_width=True):
            st.session_state.page = "Mental Health"
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Academic Quick Actions ────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<div class='zen-card'><div class='section-head'>🚀 Academic Tools</div>", unsafe_allow_html=True)
        qa = [
            ("📚 Ask Academic Question", "Academic Help"),
            ("🧩 Take a Quiz", "Quiz Generator"),
            ("📅 Plan My Week", "Study Planner"),
            ("📝 Summarize Notes", "Note Summarizer"),
        ]
        for label, target in qa:
            if st.button(label, key=f"qa_{target}", use_container_width=True):
                st.session_state.page = target
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class='zen-card'>
            <div class='section-head'>✨ What's New</div>
            <div style='display:flex;gap:.7rem;flex-direction:column'>
                <div style='background:rgba(96,165,250,.07);border:1px solid rgba(96,165,250,.2);border-radius:10px;padding:.8rem 1rem'>
                    <div style='font-size:1.1rem'>💙</div>
                    <div style='font-weight:600;margin:.2rem 0 .1rem;font-size:.9rem'>Crisis Support</div>
                    <div style='font-size:.78rem;color:#8b949e'>Gentle support + breathing exercise when you need it most.</div>
                </div>
                <div style='background:rgba(86,207,178,.07);border:1px solid rgba(86,207,178,.2);border-radius:10px;padding:.8rem 1rem'>
                    <div style='font-size:1.1rem'>📈</div>
                    <div style='font-weight:600;margin:.2rem 0 .1rem;font-size:.9rem'>Mood Trends</div>
                    <div style='font-size:.78rem;color:#8b949e'>Track how your week is going with a live mood chart.</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div class='zen-card'><div class='section-head'>💡 Daily Wellness Tip</div>", unsafe_allow_html=True)
    tips = [
        "Take a 5-minute break every 45 minutes of study. Your brain retains more with rest.",
        "Drink water before your next study session — even mild dehydration affects focus.",
        "Write down 3 things you're grateful for today. It rewires your brain for positivity.",
        "A 20-minute walk boosts memory and reduces exam anxiety significantly.",
        "Sleep is when your brain consolidates memory. Don't sacrifice it before exams.",
    ]
    tip = tips[datetime.now().day % len(tips)]
    st.markdown(f"<p style='color:#8b949e;font-size:.92rem'>{tip}</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# PAGE: MENTAL HEALTH
# ══════════════════════════════════════════════════════════════
elif page == "Mental Health":

    calm_mode = st.session_state.chat_theme == "calm"

    # ── Crisis popup (modal overlay) ─────────────────────────
    if calm_mode and not st.session_state.get("sos_popup_dismissed", False):
        import streamlit.components.v1 as components
        
        components.html("""
        <!DOCTYPE html>
        <html>
        <head>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { background: transparent; font-family: 'Inter', sans-serif; }
            
            .overlay {
                position: fixed; inset: 0;
                background: rgba(0,0,0,0.75);
                backdrop-filter: blur(5px);
                z-index: 999;
            }
            .modal {
                position: fixed;
                top: 50%; left: 50%;
                transform: translate(-50%, -50%);
                z-index: 1000;
                width: min(460px, 90vw);
                background: linear-gradient(160deg, #0d1e35 0%, #0d1117 100%);
                border: 1px solid rgba(96,165,250,.4);
                border-radius: 20px;
                padding: 2rem;
                box-shadow: 0 24px 80px rgba(0,0,0,.8);
                animation: popIn .35s cubic-bezier(.22,1,.36,1);
            }
            @keyframes popIn {
                from { opacity:0; transform: translate(-50%,-46%) scale(.95); }
                to   { opacity:1; transform: translate(-50%,-50%) scale(1); }
            }
            
            .icon { font-size: 2rem; margin-bottom: .6rem; }
            .title {
                font-size: 1.2rem; font-weight: 700;
                color: #c9dff7; margin-bottom: .5rem;
            }
            .body-text {
                font-size: .88rem; color: #94b8d8;
                line-height: 1.7; margin-bottom: 1.1rem;
            }
            
            .breath-box {
                display: flex; align-items: center; gap: .9rem;
                background: rgba(96,165,250,.06);
                border: 1px solid rgba(96,165,250,.15);
                border-radius: 10px; padding: .7rem 1rem;
                margin-bottom: 1rem;
            }
            .breath-dot {
                width: 36px; height: 36px; border-radius: 50%; flex-shrink: 0;
                background: radial-gradient(circle, rgba(96,165,250,.6) 0%, rgba(96,165,250,.05) 80%);
                border: 2px solid rgba(96,165,250,.5);
                animation: breathe 8s ease-in-out infinite;
            }
            @keyframes breathe {
                0%,100% { transform: scale(1);   opacity: .6; }
                40%      { transform: scale(1.55); opacity: 1; }
                60%      { transform: scale(1.55); opacity: 1; }
            }
            .breath-text { font-size: .8rem; color: #93c5fd; line-height: 1.5; }
            .breath-text b { color: #c9dff7; display: block; margin-bottom: .1rem; }
            
            .divider {
                border: none; border-top: 1px solid rgba(96,165,250,.12);
                margin: .9rem 0;
            }
            .section-label {
                font-size: .68rem; font-weight: 700; color: #60a5fa;
                text-transform: uppercase; letter-spacing: .08em;
                margin-bottom: .5rem;
            }
            .helpline {
                background: rgba(96,165,250,.07);
                border: 1px solid rgba(96,165,250,.15);
                border-radius: 8px; padding: .45rem .8rem;
                font-size: .8rem; color: #c9dff7;
                margin-bottom: .3rem;
                display: flex; justify-content: space-between; align-items: center;
            }
            .helpline b { color: #93c5fd; }
            
            .footer-text {
                font-size: .78rem; color: #60a5fa;
                text-align: center; margin-top: .8rem;
                font-weight: 500;
            }
        </style>
        </head>
        <body>
            <div class="overlay" onclick="closeModal()"></div>
            <div class="modal" id="modal">
                <div class="icon">💙</div>
                <div class="title">Hey — I'm right here with you.</div>
                <div class="body-text">
                    What you're feeling is real, and it matters.<br>
                    You don't have to carry this alone — and you don't have to
                    figure everything out right now.<br><br>
                    Take one slow breath. I'm not going anywhere.
                </div>
                
                <div class="breath-box">
                    <div class="breath-dot"></div>
                    <div class="breath-text">
                        <b>Try this with me</b>
                        Breathe in 4s · Hold 4s · Out 4s. Repeat twice.
                    </div>
                </div>
                
                <hr class="divider">
                
                <div class="section-label">🆘 Talk to someone right now</div>
                <div class="helpline"><span>🇧🇩 Kaan Pete Roi</span><b>01779-554391</b></div>
                <div class="helpline"><span>🌍 Crisis Text Line</span><b>Text HOME → 741741</b></div>
                <div class="helpline"><span>🌐 International</span><b>findahelpline.com</b></div>
                
                <div class="footer-text">↓ Close this and keep talking — I'm listening</div>
            </div>
            
            <script>
                function closeModal() {
                    document.getElementById('modal').style.display = 'none';
                    document.querySelector('.overlay').style.display = 'none';
                }
            </script>
        </body>
        </html>
        """, height=520, scrolling=False)

        dcol1, dcol2, dcol3 = st.columns([1, 2, 1])
        with dcol2:
            if st.button("Continue the conversation 💙", key="dismiss_sos", use_container_width=True):
                st.session_state.sos_popup_dismissed = True
                st.rerun()
        st.stop()
    # ── Normal hero ───────────────────────────────────────────
    if not calm_mode:
        st.session_state.sos_popup_dismissed = False  # reset for next time

    st.markdown("""
    <div class='hero'>
        <div class='pill'>💚 Safe Space</div>
        <h1>Mental Health Support</h1>
        <p>Talk freely. Your AI counselor listens without judgment, 24/7.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Full-width chat (no side panel) ──────────────────────
    bubble_user = "bubble-user-calm" if calm_mode else "bubble-user"
    bubble_ai   = "bubble-ai-calm"   if calm_mode else "bubble-ai"
    label_ai    = "💙 CampusZen" if calm_mode else "🌿 CampusZen"

    st.markdown("<div class='chat-scroll'>", unsafe_allow_html=True)

    if not st.session_state.mental_msgs:
        st.markdown(f"""
        <div class='{bubble_ai}'>
            <div class='bubble-label'>{label_ai}</div>
            Hey, I'm here for you. Whether you're stressed about exams,
            feeling overwhelmed, or just need someone to talk to —
            this is a safe space. What's on your mind today? 💚
        </div>
        """, unsafe_allow_html=True)

    for msg in st.session_state.mental_msgs:
        if msg["role"] == "user":
            st.markdown(
                f"<div class='{bubble_user}'><div class='bubble-label'>You</div>{msg['content']}</div>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"<div class='{bubble_ai}'><div class='bubble-label'>{label_ai}</div>{msg['content']}</div>",
                unsafe_allow_html=True
            )

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Input bar ─────────────────────────────────────────────
    input_key = f"mental_text_{st.session_state.mental_input_counter}"
    col1, col2, col3 = st.columns([8.5, 0.75, 0.75])

    with col1:
        typed_text = st.text_input(
            "",
            placeholder="Share what's on your mind..." if not calm_mode else "I'm here. Take your time...",
            key=input_key,
        )
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        voice_audio = mic_recorder(
            start_prompt="🎤",
            stop_prompt="⏹",
            key="mental_mic",
        )
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        send_clicked = st.button("➤", key="mental_send")

    if voice_audio:
        clip_id = hash(bytes(voice_audio["bytes"]))
        if clip_id != st.session_state.mental_voice_id:
            st.session_state.mental_voice_id = clip_id
            with st.spinner("Transcribing..."):
                transcript = transcribe_audio(voice_audio)
            if transcript and transcript.strip():
                _mental_send(transcript.strip())
                st.rerun()

    if send_clicked and typed_text.strip():
        _mental_send(typed_text.strip())
        st.session_state.mental_input_counter += 1
        st.rerun()

    if st.button("🗑️ Clear Chat", key="clear_mental"):
        st.session_state.mental_msgs = []
        st.session_state.mental_voice_id = None
        st.session_state.mental_input_counter += 1
        st.session_state.crisis_detected = False
        st.session_state.chat_theme = "normal"
        st.session_state.sos_popup_dismissed = False
        st.rerun()

    st.markdown("""
    <div style='margin-top:1rem;padding:.8rem 1rem;
    background:rgba(248,113,113,.07);
    border:1px solid rgba(248,113,113,.2);
    border-radius:10px;
    font-size:.8rem;
    color:#8b949e'>
    ⚠️ CampusZen is an AI companion, not a licensed therapist.
    If you're in crisis, please contact a professional or a helpline above.
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# PAGE: ACADEMIC HELP  (unchanged)
# ══════════════════════════════════════════════════════════════
elif page == "Academic Help":
    st.markdown("""
    <div class='hero'>
        <div class='pill'>📚 Academic Assistant</div>
        <h1>Academic Q&A</h1>
        <p>Ask anything — physics, math, history, programming, economics. Get clear explanations.</p>
    </div>
    """, unsafe_allow_html=True)

    ACADEMIC_SYSTEM_BASE = """You are CampusZen's expert academic tutor for university students.
- Answer questions across all subjects: science, math, humanities, engineering, business, etc.
- Explain concepts clearly with examples, analogies, and step-by-step reasoning
- For math/science: show working step by step
- Adapt complexity to the question — don't over-explain simple things
- Be encouraging and help students understand, not just get answers
- Use markdown formatting for clarity (bold, code blocks, numbered lists where helpful)"""

    active_text = get_active_pdf_text()
    if active_text:
        loaded_names = ", ".join(st.session_state.pdf_active)
        ACADEMIC_SYSTEM = ACADEMIC_SYSTEM_BASE + f"""

    The student has uploaded {len(st.session_state.pdf_active)} file(s): {loaded_names}
    Each file is clearly separated below with its filename as a header.
    Use the correct file when the student refers to a specific filename.

    {active_text[:12000]}

    If the question mentions a specific filename, answer ONLY from that file.
    If no filename is mentioned, use all files as context.
    Otherwise answer from your knowledge."""
    else:
        ACADEMIC_SYSTEM = ACADEMIC_SYSTEM_BASE

    if "academic_input_counter" not in st.session_state:
        st.session_state.academic_input_counter = 0
    if "academic_voice_id" not in st.session_state:
        st.session_state.academic_voice_id = None

    def _academic_send(user_message: str, system_prompt: str):
        st.session_state.academic_msgs.append({"role": "user", "content": user_message})
        history_str = "\n".join(
            f"{m['role']}: {m['content']}" for m in st.session_state.academic_msgs
        )
        with st.spinner("Working on it..."):
            reply = ai(system_prompt, history_str)
        st.session_state.academic_msgs.append({"role": "assistant", "content": reply})

    if st.session_state.pdf_active:
        loaded_names = ", ".join(st.session_state.pdf_active)
        st.markdown(f"""
        <div style='background:rgba(86,207,178,.07);border:1px solid rgba(86,207,178,.25);
             border-radius:10px;padding:.7rem 1rem;margin-bottom:1rem;
             display:flex;align-items:center;gap:.7rem;font-size:.87rem'>
            <span style='font-size:1.2rem'>📄</span>
            <span>AI is reading from <b>{loaded_names}</b> — ask questions about it!</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div class='chat-scroll'>", unsafe_allow_html=True)

    if not st.session_state.academic_msgs:
        intro = "Hi! I'm your academic assistant. Ask me anything — from calculus to computer science, history to chemistry. I'll explain it clearly with examples."
        if st.session_state.pdf_active:
            loaded_names = ", ".join(st.session_state.pdf_active)
            intro += f" I can also see your uploaded file **{loaded_names}** — ask me anything about it!"
        st.markdown(f"""
        <div class='bubble-ai'>
            <div class='bubble-label'>📚 Academic Tutor</div>
            {intro} 🎓
        </div>
        """, unsafe_allow_html=True)

    for msg in st.session_state.academic_msgs:
        if msg["role"] == "user":
            st.markdown(
                f"<div class='bubble-user'><div class='bubble-label'>You</div>{msg['content']}</div>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"<div class='bubble-ai'><div class='bubble-label'>📚 Tutor</div>{msg['content']}</div>",
                unsafe_allow_html=True
            )

    st.markdown("</div>", unsafe_allow_html=True)

    academic_input_key = f"academic_text_{st.session_state.academic_input_counter}"
    col1, col2, col3 = st.columns([8.5, 0.75, 0.75])

    with col1:
        academic_typed = st.text_input(
            "",
            placeholder="Ask your academic question...",
            key=academic_input_key,
        )
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        academic_voice = mic_recorder(
            start_prompt="🎤",
            stop_prompt="⏹",
            key="academic_mic",
        )
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        academic_send = st.button("➤", key="academic_send")

    if academic_voice:
        clip_id = hash(bytes(academic_voice["bytes"]))
        if clip_id != st.session_state.academic_voice_id:
            st.session_state.academic_voice_id = clip_id
            with st.spinner("Transcribing..."):
                transcript = transcribe_audio(academic_voice)
            if transcript and transcript.strip():
                _academic_send(transcript.strip(), ACADEMIC_SYSTEM)
                st.rerun()

    if academic_send and academic_typed.strip():
        _academic_send(academic_typed.strip(), ACADEMIC_SYSTEM)
        st.session_state.academic_input_counter += 1
        st.rerun()

    if st.button("🗑️ Clear Chat", key="clear_academic"):
        st.session_state.academic_msgs = []
        st.session_state.academic_voice_id = None
        st.session_state.academic_input_counter += 1
        st.rerun()


# ══════════════════════════════════════════════════════════════
# PAGE: QUIZ GENERATOR  (unchanged)
# ══════════════════════════════════════════════════════════════
elif page == "Quiz Generator":
    st.markdown("""
    <div class='hero'>
        <div class='pill'>🧩 Test Yourself</div>
        <h1>Quiz Generator</h1>
        <p>Enter any topic — or quiz yourself from your uploaded PDF/notes.</p>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.pdf_active:
        loaded_names = ", ".join(st.session_state.pdf_active)
        st.markdown(f"""
        <div style='background:rgba(124,106,247,.07);border:1px solid rgba(124,106,247,.25);
             border-radius:10px;padding:.7rem 1rem;margin-bottom:1rem;font-size:.87rem;
             display:flex;align-items:center;gap:.7rem'>
            <span style='font-size:1.2rem'>📄</span>
            <span><b>{loaded_names}</b> is loaded — leave topic blank to quiz from your document!</span>
        </div>
        """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        placeholder_text = "e.g. Photosynthesis, World War 2, Python functions… (or leave blank to use uploaded file)"
        topic = st.text_input("Quiz topic", placeholder=placeholder_text)
    with col2:
        num_q = st.selectbox("Questions", [3, 5, 7, 10], index=1)
    with col3:
        difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])

    if st.button("Generate Quiz ⚡", use_container_width=True):
        if not topic and not get_active_pdf_text():
            st.warning("Please enter a topic or upload a PDF/image first.")
        else:
            active_text = get_active_pdf_text()
            if active_text and not topic:
                loaded_names = ", ".join(st.session_state.pdf_active)
                source_desc = f"the following {len(st.session_state.pdf_active)} uploaded file(s): {loaded_names}"
                doc_context = f"\n\nEach file is separated by its filename header. Generate questions from all files or the specific file if mentioned:\n{active_text[:12000]}"
                topic_label = loaded_names
            else:
                source_desc = f'the topic: "{topic}"'
                doc_context = ""
                topic_label = topic

            QUIZ_SYSTEM = f"""Generate a {num_q}-question multiple choice quiz on {source_desc}.
Difficulty: {difficulty}.{doc_context}
Return ONLY valid JSON in this exact format, no extra text:
{{
  "title": "Quiz title here",
  "questions": [
    {{
      "q": "Question text",
      "options": ["A) option1", "B) option2", "C) option3", "D) option4"],
      "answer": "A",
      "explanation": "Brief explanation of correct answer"
    }}
  ]
}}"""
            with st.spinner("Generating your quiz..."):
                raw = ai(QUIZ_SYSTEM, f"Generate quiz on: {topic_label}")
                try:
                    clean = re.sub(r"```json|```", "", raw).strip()
                    data = json.loads(clean)
                    st.session_state.quiz_data = data
                    st.session_state.quiz_answered = {}
                    st.session_state.quiz_score = 0
                    st.rerun()
                except Exception:
                    st.error("Couldn't parse quiz. Try a different topic.")

    if st.session_state.quiz_data:
        qd = st.session_state.quiz_data
        st.markdown(f"<div class='section-head'>🧩 {qd.get('title','Quiz')}</div>", unsafe_allow_html=True)

        total = len(qd["questions"])
        answered = len(st.session_state.quiz_answered)
        score = st.session_state.quiz_score
        st.progress(answered / total if total else 0)
        st.markdown(f"<p style='color:#8b949e;font-size:.85rem'>{answered}/{total} answered · Score: {score}/{answered if answered else '?'}</p>", unsafe_allow_html=True)

        for i, q in enumerate(qd["questions"]):
            with st.container():
                st.markdown(f"<div class='zen-card'><b>Q{i+1}. {q['q']}</b>", unsafe_allow_html=True)
                for opt in q["options"]:
                    letter = opt[0]
                    is_answered = i in st.session_state.quiz_answered
                    chosen = st.session_state.quiz_answered.get(i)
                    correct = q["answer"]

                    if is_answered:
                        if letter == correct:
                            style = "border-color:#56cfb2;background:rgba(86,207,178,.1)"
                        elif letter == chosen:
                            style = "border-color:#f87171;background:rgba(248,113,113,.1)"
                        else:
                            style = ""
                        st.markdown(f"<div class='quiz-opt' style='{style}'>{opt}</div>", unsafe_allow_html=True)
                    else:
                        if st.button(opt, key=f"q{i}_{letter}"):
                            st.session_state.quiz_answered[i] = letter
                            if letter == correct:
                                st.session_state.quiz_score += 1
                            st.rerun()

                if i in st.session_state.quiz_answered:
                    chosen = st.session_state.quiz_answered[i]
                    correct = q["answer"]
                    if chosen == correct:
                        st.markdown(f"<p style='color:#56cfb2;font-size:.85rem'>✅ Correct! {q['explanation']}</p>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<p style='color:#f87171;font-size:.85rem'>❌ Wrong. Correct: {correct}. {q['explanation']}</p>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

        if answered == total:
            pct = int(score / total * 100)
            color = "#56cfb2" if pct >= 70 else "#f0a500" if pct >= 50 else "#f87171"
            st.markdown(f"""
            <div class='zen-card' style='text-align:center;border-color:{color}'>
                <div style='font-size:2.5rem;font-weight:700;color:{color}'>{pct}%</div>
                <div style='color:#8b949e'>You scored {score} out of {total}</div>
                <div style='margin-top:.5rem'>{'🏆 Excellent!' if pct>=80 else '👍 Good effort!' if pct>=60 else '📖 Keep studying!'}</div>
            </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# PAGE: STUDY PLANNER  (unchanged)
# ══════════════════════════════════════════════════════════════
elif page == "Study Planner":
    st.markdown("""
    <div class='hero'>
        <div class='pill'>📅 Plan Smart</div>
        <h1>AI Study Planner</h1>
        <p>Tell us your subjects and deadline — get a personalised weekly study schedule.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        subjects = st.text_area(
            "Your subjects / topics",
            placeholder="e.g.\nCalculus - Chapter 5,6\nOrganic Chemistry\nData Structures\nMicroeconomics",
            height=140
        )
        exam_date = st.text_input("Exam / deadline", placeholder="e.g. In 2 weeks, July 15, Next Monday")
    with col2:
        hours = st.selectbox("Study hours available per day", ["1-2 hours", "2-3 hours", "3-4 hours", "4-5 hours", "5+ hours"])
        goal = st.text_input("Your main goal", placeholder="e.g. Pass with A grade, Cover all chapters")
        weak = st.text_input("Weakest subjects (optional)", placeholder="e.g. Calculus, Organic Chemistry")

    if get_active_pdf_text() and not subjects:
        loaded_names = ", ".join(st.session_state.pdf_active)
        st.markdown(f"""
        <div style='background:rgba(124,106,247,.07);border:1px solid rgba(124,106,247,.2);
             border-radius:10px;padding:.7rem 1rem;margin:.5rem 0;font-size:.85rem'>
            💡 You have <b>{loaded_names}</b> uploaded. The AI will consider its topics when building your plan.
        </div>
        """, unsafe_allow_html=True)

    if st.button("Generate My Study Plan 📅", use_container_width=True):
        if not subjects and not get_active_pdf_text():
            st.warning("Please enter your subjects first.")
        else:
            active_text = get_active_pdf_text()
            if active_text:
                loaded_names = ", ".join(st.session_state.pdf_active)
                pdf_note = f"\nThe student has uploaded {len(st.session_state.pdf_active)} file(s): {loaded_names}\nUse the topics and content from these files to build a relevant study plan:\n{active_text[:12000]}"
            else:
                pdf_note = ""
            PLAN_SYSTEM = f"""You are an expert academic advisor creating a personalised study plan for a university student.
Create a detailed and smart study schedule based on:
- Subjects: {subjects}
- Deadline: {exam_date}
- Available hours/day: {hours}
- Goal: {goal}
- Weak areas: {weak}
{pdf_note}

Format the plan as a clear day-by-day schedule according deadline.
Use this structure:
**DAY 1 - [Day Name]**
- [Time slot]: [Subject] - [Specific topic/task] [Priority: HIGH/MED/LOW]

Include:
- Morning/evening study split recommendations
- Short breaks (Pomodoro technique)
- Revision days
- One rest day
- Motivational tip at the end

Be specific and realistic based on hours available and dont be blind about the day count. keep day counts in mind then give a proper plan"""

            with st.spinner("Creating your personalised plan..."):
                plan = ai(PLAN_SYSTEM, f"Create study plan for: {subjects}")
                st.session_state.plan_result = plan
                st.rerun()

    if st.session_state.plan_result:
        st.markdown("<div class='zen-card'>", unsafe_allow_html=True)
        st.markdown(st.session_state.plan_result)
        st.markdown("</div>", unsafe_allow_html=True)
        st.download_button(
            "⬇️ Download Plan",
            st.session_state.plan_result,
            file_name="campuszen_study_plan.txt",
            mime="text/plain"
        )
        if st.button("🔄 Generate New Plan"):
            st.session_state.plan_result = ""
            st.rerun()


# ══════════════════════════════════════════════════════════════
# PAGE: NOTE SUMMARIZER  (unchanged)
# ══════════════════════════════════════════════════════════════
elif page == "Note Summarizer":
    st.markdown("""
    <div class='hero'>
        <div class='pill'>📝 Smart Notes</div>
        <h1>Note Summarizer</h1>
        <p>Paste notes, or upload a PDF/image — get a clean structured summary instantly.</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["✍️ Paste Notes", "📄 From Uploaded File"])

    with tab1:
        col1, col2 = st.columns([3, 1])
        with col1:
            notes = st.text_area(
                "Paste your notes here",
                height=220,
                placeholder="Paste lecture notes, textbook paragraphs, or any study material here..."
            )
        with col2:
            style = st.selectbox("Summary style", ["Bullet Points", "Short Paragraph", "Key Concepts Only", "Q&A Format", "Mind Map Text"])
            length = st.selectbox("Length", ["Concise (short)", "Balanced", "Detailed"])
            subject = st.text_input("Subject (optional)", placeholder="e.g. Biology")

        if st.button("Summarize Notes ✨", use_container_width=True, key="sum_paste"):
            if not notes or len(notes.strip()) < 50:
                st.warning("Please paste at least some notes (50+ characters).")
            else:
                SUM_SYSTEM = f"""You are an expert academic note summarizer for university students.
Summarize the provided notes with these specifications:
- Style: {style}
- Length: {length}
- Subject context: {subject if subject else 'General'}

Guidelines:
- Capture ALL key concepts, definitions, formulas, and important points
- Use clear headers to organize content
- Highlight the most important points
- For Q&A format: create likely exam questions with answers
- For Mind Map: use indented hierarchical text
- Make it easy to revise from quickly before an exam"""

                with st.spinner("Summarizing your notes..."):
                    summary = ai(SUM_SYSTEM, f"Summarize these notes:\n\n{notes}", max_tokens=1500)
                    st.session_state.summary_result = summary
                    st.rerun()

    with tab2:
        st.markdown("<div class='section-head'>📄 Summarize from Uploaded File <span class='feature-badge'>NEW</span></div>", unsafe_allow_html=True)

        source_text = get_active_pdf_text()
        source_name = ", ".join(st.session_state.pdf_active) if st.session_state.pdf_active else ""

        if not source_text:
            st.markdown("""
            <div style='color:#8b949e;font-size:.88rem;padding:1rem;text-align:center'>
                📄 Upload files from the sidebar to summarize them here.
            </div>
            """, unsafe_allow_html=True)

        if source_text:
            st.info(f"Summarizing from: **{source_name}**")

            col1, col2 = st.columns(2)
            with col1:
                style2 = st.selectbox("Summary style", ["Bullet Points", "Short Paragraph", "Key Concepts Only", "Q&A Format", "Mind Map Text"], key="style2")
                length2 = st.selectbox("Length", ["Concise (short)", "Balanced", "Detailed"], key="length2")
            with col2:
                subject2 = st.text_input("Subject context (optional)", placeholder="e.g. Biology, History", key="subject2")
                st.markdown("<br>", unsafe_allow_html=True)
                summarize_pdf = st.button("Summarize File ✨", use_container_width=True, key="sum_pdf")

            if summarize_pdf:
                SUM_SYSTEM2 = f"""You are an expert academic note summarizer for university students.
                The student has uploaded {len(st.session_state.pdf_active)} file(s): {source_name}
                Each file is separated by its filename header below.
                Summarize the content with these specifications:
                - Style: {style2}
                - Length: {length2}
                - Subject context: {subject2 if subject2 else 'General'}
                If the student mentions a specific filename, summarize only that file.
                Otherwise summarize all uploaded files.

Guidelines:
- Capture ALL key concepts, definitions, formulas, dates, and important points
- Use clear headers to organize content
- Highlight the most important points
- For Q&A format: create likely exam questions with answers
- For Mind Map: use indented hierarchical text
- Make it easy to revise from quickly before an exam"""

                with st.spinner(f"Summarizing {source_name}..."):
                    summary = ai(SUM_SYSTEM2, f"Summarize this:\n\n{source_text[:12000]}", max_tokens=1800)
                    st.session_state.summary_result = summary
                    st.rerun()

if st.session_state.summary_result:
    st.markdown("<div class='zen-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-head'>✨ Your Summary</div>", unsafe_allow_html=True)
    st.markdown(st.session_state.summary_result)
    st.markdown("</div>", unsafe_allow_html=True)
    st.download_button(
        "⬇️ Download Summary",
        st.session_state.summary_result,
        file_name="campuszen_summary.txt",
        mime="text/plain"
    )
    if st.button("🗑️ Clear"):
        st.session_state.summary_result = ""
        st.rerun()
