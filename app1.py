import streamlit as st
from groq import Groq
from google import genai
from google.genai import types as genai_types
import json
import re
from datetime import datetime

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

/* ── Root ── */
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
}

html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Inter', sans-serif;
}

/* sidebar */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }

/* hide default streamlit chrome */
#MainMenu, footer { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }

/* ── Cards ── */
.zen-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
    transition: border-color .2s;
}
.zen-card:hover { border-color: var(--accent); }

/* ── Stat tiles ── */
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

/* ── Hero header ── */
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

/* ── Chat bubbles ── */
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
.bubble-label { font-size:.7rem; color:var(--muted); margin-bottom:.2rem; }

/* ── Inputs & buttons ── */
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

/* quiz option buttons */
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

/* nav pills */
.nav-pill {
    display:flex; align-items:center; gap:.5rem;
    padding:.55rem .9rem; border-radius:9px;
    font-size:.88rem; font-weight:500;
    cursor:pointer; transition: background .15s;
    margin-bottom:.25rem; color:var(--muted);
    border: 1px solid transparent;
}
.nav-pill.active {
    background: rgba(124,106,247,.15);
    border-color: rgba(124,106,247,.35);
    color: var(--accent);
}
.nav-pill:hover:not(.active) { background: var(--surface2); color:var(--text); }

/* mood selector */
.mood-row { display:flex; gap:.6rem; flex-wrap:wrap; margin:.5rem 0; }
.mood-btn {
    background: var(--surface2); border:1px solid var(--border);
    border-radius:99px; padding:.35rem .9rem;
    font-size:.85rem; cursor:pointer; transition: all .15s;
    color:var(--text);
}
.mood-btn.selected { border-color:var(--accent); background:rgba(124,106,247,.15); color:var(--accent); }

/* section headers */
.section-head {
    font-family:'Sora',sans-serif;
    font-size:1.1rem; font-weight:600;
    margin: 1rem 0 .6rem;
    display:flex; align-items:center; gap:.5rem;
}

/* scrollable chat */
.chat-scroll { max-height:420px; overflow-y:auto; padding-right:.4rem; }
.chat-scroll::-webkit-scrollbar { width:4px; }
.chat-scroll::-webkit-scrollbar-track { background:transparent; }
.chat-scroll::-webkit-scrollbar-thumb { background:var(--border); border-radius:4px; }

/* planner table */
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
</style>
""", unsafe_allow_html=True)

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
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ── AI helper ────────────────────────────────────────────────
def ai(system_prompt, user_prompt, max_tokens=1024, json_mode=False):
    """Call Groq first, fallback to Gemini Gemma 3 27B."""
    messages = [{"role": "user", "content": user_prompt}]
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": system_prompt}] + messages,
            max_tokens=max_tokens,
        )
        return resp.choices[0].message.content
    except Exception:
        try:
            gclient = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
            response = gclient.models.generate_content(
                model="gemma-3-27b-it",
                contents=system_prompt + "\n\n" + user_prompt,
            )
            return response.text
        except Exception as e:
            return f"⚠️ Both AI services unavailable: {e}"

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
        active = "active" if st.session_state.page == name else ""
        if st.button(f"{icon}  {name}", key=f"nav_{name}", use_container_width=True):
            st.session_state.page = name
            st.rerun()

    st.markdown("---")
    st.markdown(f"<div style='font-size:.75rem;color:#8b949e;text-align:center'>Powered by LLaMA 3.3 70B<br>& Gemma 3 27B • Free Forever</div>", unsafe_allow_html=True)

page = st.session_state.page

# ══════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ══════════════════════════════════════════════════════════════
if page == "Dashboard":
    st.markdown("""
    <div class='hero'>
        <div class='pill'>✦ AI-Powered Campus Companion</div>
        <h1>Good to see you 👋</h1>
        <p>Your mental health & academic assistant — available 24/7, completely free.</p>
    </div>
    """, unsafe_allow_html=True)

    # Stats
    mood_count = len(st.session_state.mood_log)
    quiz_count = len(st.session_state.quiz_answered)
    plan_done  = 1 if st.session_state.plan_result else 0
    sum_done   = 1 if st.session_state.summary_result else 0

    st.markdown(f"""
    <div class='stat-grid'>
        <div class='stat-tile purple'><div class='num'>{len(st.session_state.mental_msgs)//2}</div><div class='lbl'>Mental Health Chats</div></div>
        <div class='stat-tile teal'><div class='num'>{len(st.session_state.academic_msgs)//2}</div><div class='lbl'>Academic Questions</div></div>
        <div class='stat-tile gold'><div class='num'>{quiz_count}</div><div class='lbl'>Quiz Questions Done</div></div>
        <div class='stat-tile red'><div class='num'>{mood_count}</div><div class='lbl'>Mood Check-ins</div></div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='zen-card'><div class='section-head'>💚 Quick Mood Check</div>", unsafe_allow_html=True)
        st.markdown("How are you feeling right now?")
        moods = ["😊 Great", "😐 Okay", "😔 Low", "😰 Stressed", "😤 Frustrated"]
        cols = st.columns(len(moods))
        for i, mood in enumerate(moods):
            with cols[i]:
                if st.button(mood, key=f"mood_{i}"):
                    st.session_state.mood_today = mood
                    st.session_state.mood_log.append({"mood": mood, "time": datetime.now().strftime("%H:%M")})
                    st.rerun()
        if st.session_state.mood_today:
            st.success(f"Logged: {st.session_state.mood_today}")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='zen-card'><div class='section-head'>🚀 Quick Actions</div>", unsafe_allow_html=True)
        qa = [("💬 Talk to AI Counselor", "Mental Health"),
              ("📚 Ask Academic Question", "Academic Help"),
              ("🧩 Take a Quiz", "Quiz Generator"),
              ("📅 Plan My Week", "Study Planner")]
        for label, target in qa:
            if st.button(label, key=f"qa_{target}", use_container_width=True):
                st.session_state.page = target
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # Tips
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
    st.markdown("""
    <div class='hero'>
        <div class='pill'>💚 Safe Space</div>
        <h1>Mental Health Support</h1>
        <p>Talk freely. Your AI counselor listens without judgment, 24/7.</p>
    </div>
    """, unsafe_allow_html=True)

    MENTAL_SYSTEM = """You are CampusZen's compassionate mental health companion for university students.
Your role:
- Listen empathetically and validate feelings first before giving advice
- Help with stress, anxiety, academic pressure, loneliness, burnout, relationships
- Use warm, non-clinical language appropriate for a college student
- Offer practical coping strategies when appropriate
- If someone shows signs of serious mental health crisis or suicidal thoughts, gently encourage them to seek professional help and provide crisis resources
- Never diagnose. Never be dismissive. Always be kind.
- Keep responses focused and not too long (3-5 sentences usually enough unless they need more)"""

    # Display chat
    st.markdown("<div class='chat-scroll'>", unsafe_allow_html=True)
    if not st.session_state.mental_msgs:
        st.markdown("""
        <div class='bubble-ai'>
            <div class='bubble-label'>🌿 CampusZen Counselor</div>
            Hey, I'm here for you. Whether you're stressed about exams, feeling overwhelmed, 
            or just need someone to talk to — this is a safe space. What's on your mind today? 💚
        </div>
        """, unsafe_allow_html=True)
    for msg in st.session_state.mental_msgs:
        if msg["role"] == "user":
            st.markdown(f"<div class='bubble-user'><div class='bubble-label'>You</div>{msg['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='bubble-ai'><div class='bubble-label'>🌿 CampusZen</div>{msg['content']}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    user_input = st.text_input("Share what's on your mind...", key="mental_input", placeholder="Type here and press Enter")
    col1, col2 = st.columns([4,1])
    with col2:
        send = st.button("Send 💬", use_container_width=True)

    if (user_input and send) or (user_input and st.session_state.get("_mental_enter")):
        st.session_state.mental_msgs.append({"role": "user", "content": user_input})
        history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.mental_msgs]
        with st.spinner("Thinking..."):
            reply = ai(MENTAL_SYSTEM, "\n".join([f"{m['role']}: {m['content']}" for m in history]))
        st.session_state.mental_msgs.append({"role": "assistant", "content": reply})
        st.session_state["mental_input"] = ""
        st.rerun()

    if st.button("🗑️ Clear Chat", key="clear_mental"):
        st.session_state.mental_msgs = []
        st.rerun()

    st.markdown("""
    <div style='margin-top:1rem;padding:.8rem 1rem;background:rgba(248,113,113,.07);border:1px solid rgba(248,113,113,.2);border-radius:10px;font-size:.8rem;color:#8b949e'>
    ⚠️ CampusZen is an AI companion, not a licensed therapist. If you're in crisis, please contact a mental health professional or helpline immediately.
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# PAGE: ACADEMIC HELP
# ══════════════════════════════════════════════════════════════
elif page == "Academic Help":
    st.markdown("""
    <div class='hero'>
        <div class='pill'>📚 Academic Assistant</div>
        <h1>Academic Q&A</h1>
        <p>Ask anything — physics, math, history, programming, economics. Get clear explanations.</p>
    </div>
    """, unsafe_allow_html=True)

    ACADEMIC_SYSTEM = """You are CampusZen's expert academic tutor for university students.
- Answer questions across all subjects: science, math, humanities, engineering, business, etc.
- Explain concepts clearly with examples, analogies, and step-by-step reasoning
- For math/science: show working step by step
- Adapt complexity to the question — don't over-explain simple things
- Be encouraging and help students understand, not just get answers
- Use markdown formatting for clarity (bold, code blocks, numbered lists where helpful)"""

    st.markdown("<div class='chat-scroll'>", unsafe_allow_html=True)
    if not st.session_state.academic_msgs:
        st.markdown("""
        <div class='bubble-ai'>
            <div class='bubble-label'>📚 Academic Tutor</div>
            Hi! I'm your academic assistant. Ask me anything — from calculus to computer science, 
            history to chemistry. I'll explain it clearly with examples. What are you studying? 🎓
        </div>
        """, unsafe_allow_html=True)
    for msg in st.session_state.academic_msgs:
        if msg["role"] == "user":
            st.markdown(f"<div class='bubble-user'><div class='bubble-label'>You</div>{msg['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='bubble-ai'><div class='bubble-label'>📚 Tutor</div>{msg['content']}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    user_input = st.text_input("Ask your academic question...", key="academic_input", placeholder="e.g. Explain Newton's second law with examples")
    col1, col2 = st.columns([4,1])
    with col2:
        send = st.button("Ask 🎓", use_container_width=True)

    if user_input and send:
        st.session_state.academic_msgs.append({"role": "user", "content": user_input})
        history = st.session_state.academic_msgs
        with st.spinner("Working on it..."):
            reply = ai(ACADEMIC_SYSTEM, "\n".join([f"{m['role']}: {m['content']}" for m in history]))
        st.session_state.academic_msgs.append({"role": "assistant", "content": reply})
        st.session_state["academic_input"] = ""
        st.rerun()

    if st.button("🗑️ Clear Chat", key="clear_academic"):
        st.session_state.academic_msgs = []
        st.rerun()

# ══════════════════════════════════════════════════════════════
# PAGE: QUIZ GENERATOR
# ══════════════════════════════════════════════════════════════
elif page == "Quiz Generator":
    st.markdown("""
    <div class='hero'>
        <div class='pill'>🧩 Test Yourself</div>
        <h1>Quiz Generator</h1>
        <p>Enter any topic — get an instant multiple choice quiz to test your knowledge.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([3,1,1])
    with col1:
        topic = st.text_input("Quiz topic", placeholder="e.g. Photosynthesis, World War 2, Python functions...")
    with col2:
        num_q = st.selectbox("Questions", [3, 5, 7, 10], index=1)
    with col3:
        difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])

    if st.button("Generate Quiz ⚡", use_container_width=True):
        if not topic:
            st.warning("Please enter a topic first.")
        else:
            QUIZ_SYSTEM = f"""Generate a {num_q}-question multiple choice quiz on the topic: "{topic}".
Difficulty: {difficulty}.
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
                raw = ai(QUIZ_SYSTEM, f"Generate quiz on: {topic}")
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
# PAGE: STUDY PLANNER
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
        subjects = st.text_area("Your subjects / topics", placeholder="e.g.\nCalculus - Chapter 5,6\nOrganic Chemistry\nData Structures\nMicroeconomics", height=140)
        exam_date = st.text_input("Exam / deadline", placeholder="e.g. In 2 weeks, July 15, Next Monday")
    with col2:
        hours = st.selectbox("Study hours available per day", ["1-2 hours", "2-3 hours", "3-4 hours", "4-5 hours", "5+ hours"])
        goal = st.text_input("Your main goal", placeholder="e.g. Pass with A grade, Cover all chapters")
        weak = st.text_input("Weakest subjects (optional)", placeholder="e.g. Calculus, Organic Chemistry")

    if st.button("Generate My Study Plan 📅", use_container_width=True):
        if not subjects:
            st.warning("Please enter your subjects first.")
        else:
            PLAN_SYSTEM = f"""You are an expert academic advisor creating a personalised study plan for a university student.
Create a detailed weekly study schedule based on:
- Subjects: {subjects}
- Deadline: {exam_date}
- Available hours/day: {hours}
- Goal: {goal}
- Weak areas: {weak}

Format the plan as a clear day-by-day schedule for 7 days.
Use this structure:
**DAY 1 - [Day Name]**
- [Time slot]: [Subject] - [Specific topic/task] [Priority: HIGH/MED/LOW]

Include:
- Morning/evening study split recommendations
- Short breaks (Pomodoro technique)
- Revision days
- One rest day
- Motivational tip at the end

Be specific and realistic based on hours available."""

            with st.spinner("Creating your personalised plan..."):
                plan = ai(PLAN_SYSTEM, f"Create study plan for: {subjects}")
                st.session_state.plan_result = plan
                st.rerun()

    if st.session_state.plan_result:
        st.markdown("<div class='zen-card'>", unsafe_allow_html=True)
        st.markdown(st.session_state.plan_result)
        st.markdown("</div>", unsafe_allow_html=True)
        if st.button("🔄 Generate New Plan"):
            st.session_state.plan_result = ""
            st.rerun()

# ══════════════════════════════════════════════════════════════
# PAGE: NOTE SUMMARIZER
# ══════════════════════════════════════════════════════════════
elif page == "Note Summarizer":
    st.markdown("""
    <div class='hero'>
        <div class='pill'>📝 Smart Notes</div>
        <h1>Note Summarizer</h1>
        <p>Paste your lecture notes or textbook content — get a clean, structured summary instantly.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([3,1])
    with col1:
        notes = st.text_area("Paste your notes here", height=220, placeholder="Paste lecture notes, textbook paragraphs, or any study material here...")
    with col2:
        style = st.selectbox("Summary style", ["Bullet Points", "Short Paragraph", "Key Concepts Only", "Q&A Format", "Mind Map Text"])
        length = st.selectbox("Length", ["Concise (short)", "Balanced", "Detailed"])
        subject = st.text_input("Subject (optional)", placeholder="e.g. Biology")

    if st.button("Summarize Notes ✨", use_container_width=True):
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
