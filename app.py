import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import os
from prompt import get_review_prompt

LANGUAGE_PATTERNS = {
    "Python": [r"\bdef\b", r"\bimport\b", r"\bclass\s+\w+.*:", r"\bprint\s*\(", r"\bself\b", r"\blambda\b", r"\belif\b", r"\bNone\b", r"#.*", r"\bfrom\s+\w+\s+import\b"],
    "JavaScript": [r"\bconst\b", r"\blet\b", r"\bvar\b", r"\bfunction\b", r"\bconsole\.log\b", r"=>", r"\bdocument\.", r"\bwindow\.", r"\baddEventListener\b", r"\btypeof\b"],
    "TypeScript": [r":\s*(string|number|boolean|void|any)\b", r"\binterface\b", r"\btype\s+\w+\s*=", r"\benum\b", r"\bas\s+\w+", r"\bimplements\b"],
    "Java": [r"\bpublic\s+(static\s+)?(void|class|int|String)\b", r"\bSystem\.out\b", r"\bpackage\s+\w+", r"\bimport\s+java\.", r"\b@Override\b", r"\bnew\s+\w+\s*\("],
    "C++": [r"#include\s*[<\"].*[>\"]", r"\bstd::", r"\bcout\b", r"\bcin\b", r"\bint\s+main\b", r"\bvector\b", r"\bnamespace\b", r"\bnullptr\b"],
    "PHP": [r"<\?php", r"\$\w+", r"\becho\b", r"\bfunction\s+\w+\s*\(.*\$", r"\b\$this\b", r"\bforeach\b.*\$"],
    "Go": [r"\bpackage\s+main\b", r"\bfunc\s+main\b", r"\bfmt\.", r"\bgo\s+func\b", r":=\s*", r"\bchan\b", r"\bdefer\b", r"\bgoroutine\b"],
    "Rust": [r"\bfn\s+main\b", r"\blet\s+mut\b", r"::", r"\bprintln!\b", r"\bprintln!\b", r"\bSome\b", r"\bNone\b", r"\bOk\b", r"\bErr\b"],
    "Kotlin": [r"\bfun\s+\w+\s*\(", r"\bval\b", r"\bvar\b", r"\bprintln\b", r"\bwhen\b", r"\bdata\s+class\b", r"\.\.\."],
    "Swift": [r"\bvar\b", r"\blet\b", r"\bfunc\b", r"\bimport\s+Foundation\b", r"\bimport\s+UIKit\b", r"\bguard\b", r"\boptional\b", r":\s*\[.*\]\s*{", r"\bstring\b"],
}

def detect_language_mismatch(code: str, selected_language: str) -> list[str]:
    if not code.strip():
        return []
    patterns = LANGUAGE_PATTERNS.get(selected_language, [])
    if not patterns:
        return []
    import re
    matches = sum(1 for p in patterns if re.search(p, code, re.IGNORECASE))
    if matches == 0:
        return [f"Kode ini tidak terdeteksi sebagai {selected_language}. Pastikan kode sesuai dengan bahasa yang dipilih."]
    return []

# Load API Key
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.set_page_config(
    page_title="AI Code Reviewer",
    page_icon="◆",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=SF+Mono&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background: #000000;
    color: #f5f5f7;
    -webkit-font-smoothing: antialiased;
}

.stApp { background: #000000; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 2.5rem 4rem; max-width: 1200px; margin: 0 auto; position: relative; z-index: 2; }
section[data-testid="stSidebar"] > div { position: relative; z-index: 2; }

/* ── Animated Background Glow ── */
.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    pointer-events: none;
    z-index: 0;
    background:
        radial-gradient(ellipse at 60% 10%, rgba(99,102,241,0.08) 0%, transparent 50%),
        radial-gradient(ellipse at 10% 70%, rgba(34,211,238,0.06) 0%, transparent 50%),
        radial-gradient(ellipse at 80% 60%, rgba(168,85,247,0.06) 0%, transparent 50%),
        radial-gradient(ellipse at 30% 30%, rgba(52,211,153,0.04) 0%, transparent 40%);
    animation: bgGlow 12s ease-in-out infinite alternate;
}

@keyframes bgGlow {
    0% {
        opacity: 0.6;
        transform: scale(1) translate(0, 0);
    }
    33% {
        opacity: 1;
        transform: scale(1.08) translate(1%, -1%);
    }
    66% {
        opacity: 0.7;
        transform: scale(1.04) translate(-1%, 1%);
    }
    100% {
        opacity: 0.9;
        transform: scale(1.06) translate(0.5%, -0.5%);
    }
}

/* ── Animated Grid ── */
.stApp::after {
    content: '';
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    pointer-events: none;
    z-index: 0;
    background-image:
        linear-gradient(rgba(255,255,255,0.015) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.015) 1px, transparent 1px);
    background-size: 60px 60px;
    animation: gridMove 20s linear infinite;
}

@keyframes gridMove {
    0% { background-position: 0 0; }
    100% { background-position: 60px 60px; }
}

/* ── Particle Background ── */
.particles {
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    pointer-events: none;
    z-index: 1;
    overflow: hidden;
}

.particle {
    position: absolute;
    border-radius: 50%;
    animation: float linear infinite;
}

.particle-dot {
    background: rgba(255,255,255,0.12);
}

.particle-glow {
    background: radial-gradient(circle, rgba(99,102,241,0.4) 0%, transparent 70%);
}

.particle-cyan {
    background: radial-gradient(circle, rgba(34,211,238,0.3) 0%, transparent 60%);
}

.particle-purple {
    background: radial-gradient(circle, rgba(168,85,247,0.3) 0%, transparent 60%);
}

.particle-green {
    background: radial-gradient(circle, rgba(52,211,153,0.25) 0%, transparent 60%);
}

.meteor {
    position: absolute;
    width: 2px;
    height: 80px;
    background: linear-gradient(to bottom, rgba(255,255,255,0), rgba(99,102,241,0.5), rgba(255,255,255,0.7));
    border-radius: 2px;
    animation: meteorFall linear infinite;
    opacity: 0;
}

@keyframes float {
    0% { transform: translateY(100vh) translateX(0); opacity: 0; }
    10% { opacity: 1; }
    90% { opacity: 1; }
    100% { transform: translateY(-10vh) translateX(30px); opacity: 0; }
}

@keyframes floatSlow {
    0% { transform: translateY(100vh) translateX(0) scale(1); opacity: 0; }
    15% { opacity: 0.6; }
    85% { opacity: 0.4; }
    100% { transform: translateY(-10vh) translateX(-20px) scale(1.5); opacity: 0; }
}

@keyframes meteorFall {
    0% { transform: translateY(-100px) translateX(0) rotate(-35deg); opacity: 0; }
    5% { opacity: 0.6; }
    15% { opacity: 0; }
    100% { transform: translateY(100vh) translateX(-200px) rotate(-35deg); opacity: 0; }
}

/* ── Hero ── */
.hero-wrap {
    text-align: center;
    padding: 5rem 0 3.5rem;
    position: relative;
    animation: fadeDown 0.9s cubic-bezier(0.16,1,0.3,1) both;
}

@keyframes fadeDown {
    from { opacity: 0; transform: translateY(-24px); }
    to   { opacity: 1; transform: translateY(0); }
}

.hero-eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 0.72rem;
    font-weight: 500;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.4);
    margin-bottom: 1.5rem;
}

.hero-eyebrow::before, .hero-eyebrow::after {
    content: '';
    display: block;
    width: 28px; height: 1px;
    background: rgba(255,255,255,0.2);
}

.hero-title {
    font-size: clamp(2.8rem, 6vw, 4.5rem);
    font-weight: 700;
    letter-spacing: -0.03em;
    line-height: 1.05;
    color: #f5f5f7;
    margin-bottom: 1.25rem;
}

.hero-title span {
    background: linear-gradient(135deg, #ffffff 0%, #a0a0a0 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.hero-sub {
    font-size: 1.05rem;
    font-weight: 400;
    color: rgba(255,255,255,0.45);
    max-width: 420px;
    margin: 0 auto 2.5rem;
    line-height: 1.6;
}

/* ── Pills ── */
.pill-row {
    display: flex;
    justify-content: center;
    gap: 8px;
    flex-wrap: wrap;
    margin-bottom: 0;
    animation: fadeUp 1s 0.3s cubic-bezier(0.16,1,0.3,1) both;
}

@keyframes fadeUp {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}

.pill {
    font-size: 0.72rem;
    font-weight: 500;
    color: rgba(255,255,255,0.5);
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 999px;
    padding: 0.3rem 0.85rem;
    letter-spacing: 0.04em;
    transition: all 0.3s cubic-bezier(0.16,1,0.3,1);
}

.pill:hover {
    background: rgba(255,255,255,0.1);
    border-color: rgba(255,255,255,0.2);
    color: rgba(255,255,255,0.8);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}

/* ── Divider ── */
.rule {
    height: 1px;
    background: rgba(255,255,255,0.08);
    margin: 2.5rem 0;
    animation: scaleX 1s 0.4s cubic-bezier(0.16,1,0.3,1) both;
    transform-origin: left;
}

@keyframes scaleX {
    from { transform: scaleX(0); opacity: 0; }
    to   { transform: scaleX(1); opacity: 1; }
}

/* ── Panel Labels ── */
.panel-label {
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.3);
    margin-bottom: 0.85rem;
    display: flex;
    align-items: center;
    gap: 8px;
    animation: fadeUp 0.8s 0.5s cubic-bezier(0.16,1,0.3,1) both;
}

.panel-dot {
    width: 5px; height: 5px;
    background: rgba(255,255,255,0.25);
    border-radius: 50%;
    animation: breathe 3s ease-in-out infinite;
}

@keyframes breathe {
    0%, 100% { opacity: 0.3; transform: scale(1); }
    50% { opacity: 1; transform: scale(1.3); }
}

.panel-dot.active {
    background: #34d399;
    animation: pulse-green 1.5s ease-in-out infinite;
}

@keyframes pulse-green {
    0%, 100% { opacity: 1; box-shadow: 0 0 0 0 rgba(52,211,153,0.4); }
    50% { opacity: 0.8; box-shadow: 0 0 0 6px rgba(52,211,153,0); }
}

/* ── Text Area ── */
.stTextArea {
    animation: fadeUp 0.8s 0.55s cubic-bezier(0.16,1,0.3,1) both;
}

.stTextArea textarea {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 16px !important;
    color: rgba(255,255,255,0.85) !important;
    font-family: 'SF Mono', 'Fira Code', monospace !important;
    font-size: 0.82rem !important;
    line-height: 1.75 !important;
    padding: 1.25rem !important;
    transition: border-color 0.3s ease, box-shadow 0.3s ease !important;
    resize: none !important;
    caret-color: white !important;
}

.stTextArea textarea:focus {
    border-color: rgba(255,255,255,0.22) !important;
    box-shadow: 0 0 0 4px rgba(255,255,255,0.04), 0 8px 40px rgba(0,0,0,0.4) !important;
    outline: none !important;
}

.stTextArea textarea::placeholder {
    color: rgba(255,255,255,0.18) !important;
}

/* ── Selectbox ── */
.stSelectbox {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 14px;
    padding: 0.3rem 1.2rem 1rem;
    margin-bottom: 1rem;
}

.stSelectbox label {
    font-size: 0.65rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.14em !important;
    text-transform: uppercase !important;
    color: rgba(255,255,255,0.25) !important;
    font-family: 'Inter', sans-serif !important;
    margin-bottom: 0.5rem !important;
    padding: 0 !important;
    height: auto !important;
    min-height: auto !important;
}

.stSelectbox > div > div {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 10px !important;
    color: #ffffff !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.85rem !important;
    transition: border-color 0.2s ease !important;
    min-height: 40px !important;
    cursor: pointer !important;
}

.stSelectbox svg {
    fill: rgba(255,255,255,0.6) !important;
}

ul[data-baseweb="menu"] {
    background: #141414 !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 12px !important;
    padding: 6px !important;
}

ul[data-baseweb="menu"] li {
    color: rgba(255,255,255,0.8) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.85rem !important;
    border-radius: 8px !important;
    padding: 8px 12px !important;
    cursor: pointer !important;
    transition: background 0.15s ease !important;
}

ul[data-baseweb="menu"] li:hover {
    background: rgba(255,255,255,0.1) !important;
}

ul[data-baseweb="menu"] li[aria-selected="true"] {
    background: rgba(255,255,255,0.06) !important;
    color: #ffffff !important;
}

/* ── Stats Bar ── */
.stats {
    display: flex;
    gap: 2rem;
    padding: 1rem 0 0.5rem;
    animation: fadeUp 0.8s 0.6s cubic-bezier(0.16,1,0.3,1) both;
}

.stat { display: flex; flex-direction: column; gap: 3px; }

.stat-label {
    font-size: 0.62rem;
    font-weight: 500;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.25);
}

.stat-value {
    font-family: 'SF Mono', monospace;
    font-size: 0.9rem;
    font-weight: 600;
    color: rgba(255,255,255,0.7);
    transition: color 0.3s ease;
}

/* ── Button ── */
.stButton > button {
    width: 100% !important;
    background: #f5f5f7 !important;
    color: #000000 !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 0.9rem 2rem !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    letter-spacing: -0.01em !important;
    cursor: pointer !important;
    transition: all 0.25s cubic-bezier(0.16,1,0.3,1) !important;
    margin-top: 0.75rem !important;
    animation: fadeUp 0.8s 0.65s cubic-bezier(0.16,1,0.3,1) both !important;
}

.stButton > button:hover {
    background: #ffffff !important;
    transform: scale(1.015) !important;
    box-shadow: 0 12px 40px rgba(255,255,255,0.12) !important;
}

.stButton > button:active {
    transform: scale(0.99) !important;
}

/* ── Result Panel ── */
.result-wrap {
    animation: fadeUp 0.8s 0.6s cubic-bezier(0.16,1,0.3,1) both;
}

.result-box {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px;
    padding: 1.75rem;
    min-height: 430px;
    font-size: 0.875rem;
    line-height: 1.75;
    color: rgba(255,255,255,0.75);
    animation: fadeIn 0.6s cubic-bezier(0.16,1,0.3,1) both;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
}

.result-box h2 {
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.9);
    margin: 1.5rem 0 0.6rem;
    padding-bottom: 0.4rem;
    border-bottom: 1px solid rgba(255,255,255,0.07);
}

.result-box h2:first-child { margin-top: 0; }
.result-box ul { padding-left: 1.2rem; }
.result-box li { margin-bottom: 0.35rem; color: rgba(255,255,255,0.6); }

.result-box code {
    background: rgba(255,255,255,0.07);
    color: rgba(255,255,255,0.85);
    padding: 0.1rem 0.45rem;
    border-radius: 5px;
    font-family: 'SF Mono', monospace;
    font-size: 0.78rem;
}

/* ── Empty State ── */
.empty {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 380px;
    gap: 12px;
    animation: fadeIn 0.5s ease both;
}

.empty-icon {
    font-size: 2rem;
    opacity: 0.12;
    animation: breathe 4s ease-in-out infinite;
}

.empty-text {
    font-size: 0.75rem;
    font-weight: 500;
    letter-spacing: 0.1em;
    color: rgba(255,255,255,0.15);
    text-transform: uppercase;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #0a0a0a !important;
    border-right: 1px solid rgba(255,255,255,0.07) !important;
}

section[data-testid="stSidebar"] .block-container {
    padding: 2.5rem 1.5rem;
}

.sidebar-section {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 1.1rem 1.2rem;
    margin-bottom: 1rem;
}

.sidebar-label {
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.25);
    margin-bottom: 0.85rem;
}

.guide-item {
    display: flex;
    gap: 10px;
    align-items: flex-start;
    margin-bottom: 0.7rem;
}

.guide-num {
    font-family: 'SF Mono', monospace;
    font-size: 0.65rem;
    color: rgba(255,255,255,0.4);
    background: rgba(255,255,255,0.07);
    border-radius: 5px;
    padding: 2px 6px;
    min-width: 22px;
    text-align: center;
    margin-top: 1px;
}

.guide-text {
    font-size: 0.78rem;
    color: rgba(255,255,255,0.4);
    line-height: 1.45;
}

.model-tag {
    font-family: 'SF Mono', monospace;
    font-size: 0.68rem;
    color: rgba(255,255,255,0.35);
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 6px;
    padding: 0.25rem 0.55rem;
    display: inline-block;
    margin-top: 0.4rem;
}

/* ── Spinner ── */
.stSpinner > div {
    border-color: rgba(255,255,255,0.15) !important;
    border-top-color: rgba(255,255,255,0.7) !important;
}

/* ── Alerts ── */
.stWarning, .stError {
    border-radius: 12px !important;
    font-size: 0.85rem !important;
    border: none !important;
}
</style>

<!-- Floating Particles -->
<div class="particles" id="particles"></div>

<script>
(function() {
    const container = document.getElementById('particles');
    if (!container) return;
    while (container.firstChild) {
        container.removeChild(container.firstChild);
    }
    const colors = ['particle-dot', 'particle-glow', 'particle-cyan', 'particle-purple', 'particle-green'];
    for (let i = 0; i < 50; i++) {
        const p = document.createElement('div');
        const cls = colors[Math.floor(Math.random() * colors.length)];
        const isGlow = cls !== 'particle-dot';
        const size = isGlow ? Math.random() * 4 + 3 : Math.random() * 2 + 1;
        const dur = isGlow ? Math.random() * 30 + 20 : Math.random() * 20 + 12;
        const anim = isGlow ? 'floatSlow' : 'float';
        p.className = 'particle ' + cls;
        p.style.cssText = `
            left: ${Math.random() * 100}%;
            width: ${size}px;
            height: ${size}px;
            animation-name: ${anim};
            animation-duration: ${dur}s;
            animation-delay: ${Math.random() * 30}s;
        `;
        container.appendChild(p);
    }
    for (let i = 0; i < 5; i++) {
        const m = document.createElement('div');
        m.className = 'meteor';
        m.style.cssText = `
            left: ${Math.random() * 90 + 5}%;
            top: ${Math.random() * 80}%;
            width: ${Math.random() * 1.5 + 1}px;
            height: ${Math.random() * 80 + 40}px;
            animation-duration: ${Math.random() * 4 + 3}s;
            animation-delay: ${Math.random() * 8 + i * 5}s;
        `;
        container.appendChild(m);
    }
})();
</script>
""", unsafe_allow_html=True)

# ── Hero ──
st.markdown("""
<div class="hero-wrap">
    <div class="hero-eyebrow">AI-Powered Code Analysis</div>
    <div class="hero-title"><span>AI Code Reviewer</span></div>
    <div class="hero-sub">Instant, intelligent feedback on your code — bugs, security, performance, and clarity.</div>
    <div class="pill-row">
        <span class="pill">Bug Detection</span>
        <span class="pill">Security Analysis</span>
        <span class="pill">Performance</span>
        <span class="pill">Readability</span>
        <span class="pill">10 Languages</span>
    </div>
</div>
<div class="rule"></div>
""", unsafe_allow_html=True)

# ── Main Layout ──
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown('<div class="panel-label"><span class="panel-dot"></span>Input Kode</div>', unsafe_allow_html=True)

    language = st.selectbox(
        "Language",
        ["Python", "JavaScript", "TypeScript", "Java", "C++", "PHP", "Go", "Rust", "Kotlin", "Swift"],
        key="language_select"
    )

    code_input = st.text_area(
        label="code",
        height=340,
        placeholder="# Paste kode kamu di sini...\n# Python, JS, TypeScript, Java, C++, dan lainnya",
        label_visibility="collapsed"
    )

    lines = len(code_input.splitlines()) if code_input.strip() else 0
    chars = len(code_input) if code_input.strip() else 0

    st.markdown(f"""
    <div class="stats">
        <div class="stat">
            <span class="stat-label">Lines</span>
            <span class="stat-value">{lines}</span>
        </div>
        <div class="stat">
            <span class="stat-label">Chars</span>
            <span class="stat-value">{chars}</span>
        </div>
        <div class="stat">
            <span class="stat-label">Language</span>
            <span class="stat-value">{language}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    review_button = st.button("Review Code →", type="primary", use_container_width=True)

with col2:
    st.markdown('<div class="panel-label"><span class="panel-dot active"></span>Hasil Review</div>', unsafe_allow_html=True)

    if review_button:
        if not code_input.strip():
            st.warning("Kode tidak boleh kosong.")
        else:
            warnings = detect_language_mismatch(code_input, language)
            if warnings:
                for w in warnings:
                    st.warning(w)
            else:
                with st.spinner("Menganalisis kode..."):
                    try:
                        prompt = get_review_prompt(code_input, language)
                        response = client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=[{"role": "user", "content": prompt}]
                        )
                        result = response.choices[0].message.content
                        st.markdown(f'<div class="result-box">{result}</div>', unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
    else:
        st.markdown("""
        <div class="result-wrap">
            <div class="result-box">
                <div class="empty">
                    <div class="empty-icon">◆</div>
                    <div class="empty-text">awaiting input</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center;padding:2rem 0 0;">
    <span style="font-size:0.65rem;color:rgba(255,255,255,0.2);letter-spacing:0.1em;text-transform:uppercase;">Powered by llama-3.3-70b-versatile via Groq</span>
</div>
""", unsafe_allow_html=True)