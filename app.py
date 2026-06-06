import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import os
from prompt import get_review_prompt

# Load API Key
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# =====================
# PAGE CONFIG
# =====================
st.set_page_config(
    page_title="AI Code Reviewer",
    page_icon="🤖",
    layout="wide"
)

# =====================
# CUSTOM CSS
# =====================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Syne:wght@400;600;700;800&display=swap');

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
    background-color: #0a0a0f;
    color: #e2e8f0;
}

.stApp {
    background: #0a0a0f;
}

/* ── Hide default streamlit elements ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem; max-width: 1400px; }

/* ── Hero Header ── */
.hero {
    text-align: center;
    padding: 3rem 0 2rem 0;
    position: relative;
}

.hero-badge {
    display: inline-block;
    background: linear-gradient(135deg, #1a1a2e, #16213e);
    border: 1px solid #00d4ff33;
    color: #00d4ff;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    letter-spacing: 0.15em;
    padding: 0.4rem 1rem;
    border-radius: 999px;
    margin-bottom: 1.5rem;
}

.hero-title {
    font-size: 3.5rem;
    font-weight: 800;
    line-height: 1.1;
    background: linear-gradient(135deg, #ffffff 0%, #00d4ff 50%, #7c3aed 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 1rem;
}

.hero-subtitle {
    color: #64748b;
    font-size: 1.1rem;
    font-weight: 400;
    max-width: 500px;
    margin: 0 auto;
}

/* ── Divider ── */
.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, #00d4ff33, #7c3aed33, transparent);
    margin: 2rem 0;
}

/* ── Panel Cards ── */
.panel-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.2em;
    color: #00d4ff;
    text-transform: uppercase;
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.panel-label::before {
    content: '';
    display: inline-block;
    width: 6px;
    height: 6px;
    background: #00d4ff;
    border-radius: 50%;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.4; transform: scale(0.8); }
}

/* ── Text Area ── */
.stTextArea textarea {
    background: #0f0f1a !important;
    border: 1px solid #1e1e3a !important;
    border-radius: 12px !important;
    color: #e2e8f0 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.85rem !important;
    line-height: 1.7 !important;
    padding: 1.25rem !important;
    transition: border-color 0.3s ease !important;
    resize: none !important;
}

.stTextArea textarea:focus {
    border-color: #00d4ff66 !important;
    box-shadow: 0 0 0 3px #00d4ff11 !important;
    outline: none !important;
}

.stTextArea textarea::placeholder {
    color: #334155 !important;
}

/* ── Selectbox ── */
.stSelectbox > div > div {
    background: #0f0f1a !important;
    border: 1px solid #1e1e3a !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.85rem !important;
}

/* ── Button ── */
.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #00d4ff, #7c3aed) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.85rem 2rem !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    letter-spacing: 0.05em !important;
    cursor: pointer !important;
    transition: all 0.3s ease !important;
    margin-top: 0.75rem !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px #00d4ff33 !important;
}

.stButton > button:active {
    transform: translateY(0) !important;
}

/* ── Result Box ── */
.result-box {
    background: #0f0f1a;
    border: 1px solid #1e1e3a;
    border-radius: 12px;
    padding: 1.5rem;
    min-height: 460px;
    font-size: 0.9rem;
    line-height: 1.8;
}

.result-box h2 {
    font-family: 'Syne', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    color: #00d4ff;
    margin-top: 1.25rem;
    margin-bottom: 0.5rem;
    border-bottom: 1px solid #1e1e3a;
    padding-bottom: 0.4rem;
}

.result-box ul { padding-left: 1.25rem; }
.result-box li { margin-bottom: 0.4rem; color: #94a3b8; }
.result-box code {
    background: #1e1e3a;
    color: #00d4ff;
    padding: 0.1rem 0.4rem;
    border-radius: 4px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
}

/* ── Empty State ── */
.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 400px;
    gap: 1rem;
    color: #1e293b;
}

.empty-icon {
    font-size: 3rem;
    opacity: 0.3;
}

.empty-text {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    letter-spacing: 0.1em;
    color: #1e293b;
}

/* ── Stats Bar ── */
.stats-bar {
    display: flex;
    gap: 2rem;
    padding: 1rem 0;
    border-top: 1px solid #1e1e3a;
    margin-top: 1rem;
}

.stat-item {
    display: flex;
    flex-direction: column;
    gap: 0.2rem;
}

.stat-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.15em;
    color: #334155;
    text-transform: uppercase;
}

.stat-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.9rem;
    font-weight: 700;
    color: #00d4ff;
}

/* ── Warning / Error ── */
.stWarning, .stError {
    border-radius: 10px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.85rem !important;
}

/* ── Spinner ── */
.stSpinner > div {
    border-top-color: #00d4ff !important;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #0a0a0f !important;
    border-right: 1px solid #1e1e3a !important;
}

section[data-testid="stSidebar"] .block-container {
    padding: 2rem 1.5rem;
}

.sidebar-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.2em;
    color: #334155;
    text-transform: uppercase;
    margin-bottom: 1.5rem;
}

.sidebar-section {
    background: #0f0f1a;
    border: 1px solid #1e1e3a;
    border-radius: 10px;
    padding: 1rem;
    margin-bottom: 1rem;
}

.sidebar-section-title {
    font-size: 0.75rem;
    font-weight: 700;
    color: #7c3aed;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 0.75rem;
}

.guide-step {
    display: flex;
    gap: 0.75rem;
    align-items: flex-start;
    margin-bottom: 0.6rem;
}

.guide-num {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: #00d4ff;
    background: #00d4ff11;
    border: 1px solid #00d4ff33;
    border-radius: 4px;
    padding: 0.1rem 0.4rem;
    min-width: 24px;
    text-align: center;
}

.guide-text {
    font-size: 0.8rem;
    color: #64748b;
    line-height: 1.4;
}

.model-badge {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    background: #7c3aed22;
    border: 1px solid #7c3aed44;
    color: #a78bfa;
    padding: 0.3rem 0.6rem;
    border-radius: 6px;
    display: inline-block;
    margin-top: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

# =====================
# SIDEBAR
# =====================
with st.sidebar:
    st.markdown('<div class="sidebar-title">// Configuration</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section"><div class="sidebar-section-title">Language</div>', unsafe_allow_html=True)
    language = st.selectbox(
        "Language",
        ["Python", "JavaScript", "TypeScript", "Java", "C++", "PHP", "Go", "Rust", "Kotlin", "Swift"],
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="sidebar-section">
        <div class="sidebar-section-title">How to use</div>
        <div class="guide-step">
            <span class="guide-num">01</span>
            <span class="guide-text">Pilih bahasa pemrograman</span>
        </div>
        <div class="guide-step">
            <span class="guide-num">02</span>
            <span class="guide-text">Paste kode kamu di panel kiri</span>
        </div>
        <div class="guide-step">
            <span class="guide-num">03</span>
            <span class="guide-text">Klik Review dan tunggu hasilnya</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="sidebar-section">
        <div class="sidebar-section-title">Model</div>
        <div class="guide-text">Powered by</div>
        <div class="model-badge">llama-3.3-70b-versatile</div>
    </div>
    """, unsafe_allow_html=True)

# =====================
# HERO HEADER
# =====================
st.markdown("""
<div class="hero">
    <div class="hero-badge">// AI-POWERED CODE ANALYSIS</div>
    <div class="hero-title">AI Code Reviewer</div>
    <div class="hero-subtitle">Dapatkan feedback mendalam dari senior developer AI — bugs, security, performance, dan lebih.</div>
</div>
<div class="divider"></div>
""", unsafe_allow_html=True)

# =====================
# MAIN LAYOUT
# =====================
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown('<div class="panel-label">Input Kode</div>', unsafe_allow_html=True)
    code_input = st.text_area(
        label="code",
        height=420,
        placeholder="# Paste kode kamu di sini...\n# Supports Python, JS, TS, Java, C++, dan lainnya",
        label_visibility="collapsed"
    )

    # Stats bar
    lines = len(code_input.splitlines()) if code_input.strip() else 0
    chars = len(code_input) if code_input.strip() else 0
    st.markdown(f"""
    <div class="stats-bar">
        <div class="stat-item">
            <span class="stat-label">Lines</span>
            <span class="stat-value">{lines}</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">Characters</span>
            <span class="stat-value">{chars}</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">Language</span>
            <span class="stat-value">{language}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    review_button = st.button("🔍 Review My Code", type="primary", use_container_width=True)

with col2:
    st.markdown('<div class="panel-label">Hasil Review</div>', unsafe_allow_html=True)

    if review_button:
        if not code_input.strip():
            st.warning("⚠️ Kode tidak boleh kosong!")
        else:
            with st.spinner("Menganalisis kode kamu..."):
                try:
                    prompt = get_review_prompt(code_input, language)
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "user", "content": prompt}]
                    )
                    result = response.choices[0].message.content
                    st.markdown(result)
                except Exception as e:
                    st.error(f"❌ Terjadi error: {str(e)}")
    else:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">⬡</div>
            <div class="empty-text">// awaiting input</div>
        </div>
        """, unsafe_allow_html=True)