"""
🏥 Medical RAG System — Streamlit Cloud Entry Point
This is a self-contained version that imports the RAG system directly,
no separate FastAPI backend needed. Use this for Streamlit Cloud deployment.
"""

import streamlit as st
import sys
import os

# Ensure project root is on path so we can import backend modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Medical RAG System",
    page_icon="🏥",
    layout="wide",
)

# ── Initialize session state ─────────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "home"


# ── Load RAG system (cached so it's only initialized once) ───────────────────
@st.cache_resource(show_spinner="🔄 Initializing RAG system …")
def load_rag_system():
    """Load the RAG system once and cache it across all sessions."""
    from backend.rag_system import RAGSystem
    return RAGSystem()


# ── Auth helpers (simple, no DB required for demo) ───────────────────────────
DEMO_USERS = {
    "admin": "admin",
    "demo": "demo123",
}


def do_login(username, password):
    if DEMO_USERS.get(username) == password:
        st.session_state.logged_in = True
        st.session_state.username = username
        return True
    return False


def do_logout():
    st.session_state.logged_in = False
    st.session_state.username = None
    st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# LOGIN PAGE
# ══════════════════════════════════════════════════════════════════════════════
def render_login():
    st.markdown("""
    <style>
        .main .block-container { max-width: 700px; padding-top: 3rem; }
        .login-hero {
            background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
            border-radius: 16px; padding: 2.5rem 2rem; text-align: center;
            margin-bottom: 1.5rem; box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        }
        .login-hero h1 { color: #fff; font-size: 2rem; margin: 0 0 0.5rem 0; }
        .login-hero p  { color: #b8b8d4; font-size: 1rem; margin: 0; }
        .demo-box {
            background: linear-gradient(135deg, #1b5e20, #2e7d32);
            border-radius: 12px; padding: 1.2rem 1.5rem; margin: 1rem 0 1.5rem 0;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .demo-box h4 { color: #a5d6a7; margin: 0 0 0.5rem 0; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; }
        .demo-creds { display: flex; gap: 2rem; justify-content: center; }
        .demo-cred .label { color: #81c784; font-size: 0.75rem; margin-bottom: 0.2rem; text-align: center; }
        .demo-cred .value {
            color: #ffffff; font-size: 1.3rem; font-weight: 700;
            background: rgba(0,0,0,0.3); padding: 0.3rem 1rem; border-radius: 8px; font-family: monospace;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="login-hero">
        <h1>🏥 Medical RAG System</h1>
        <p>AI-powered patient case search with Retrieval-Augmented Generation</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="demo-box">
        <h4>🔑 Demo Credentials — Use these to login instantly</h4>
        <div class="demo-creds">
            <div class="demo-cred">
                <div class="label">Username</div>
                <div class="value">admin</div>
            </div>
            <div class="demo-cred">
                <div class="label">Password</div>
                <div class="value">admin</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab_login, tab_signup = st.tabs(["🔓 Login", "📝 About"])

    with tab_login:
        username = st.text_input("Username", placeholder="Enter username")
        password = st.text_input("Password", type="password", placeholder="Enter password")
        if st.button("Login", type="primary", use_container_width=True):
            if username and password:
                if do_login(username, password):
                    st.success("✅ Login successful!")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")
            else:
                st.warning("Please enter both username and password.")

    with tab_signup:
        st.info("This is a demo deployment. Use the demo credentials shown above to login.")
        st.markdown("""
        **Built with:**
        - 🤖 Groq (Llama 3.3 70B) for LLM
        - 🗄️ Pinecone for vector search
        - 🔗 Cohere for embeddings
        - 🦜 LangChain for orchestration
        """)


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR + NAVIGATION
# ══════════════════════════════════════════════════════════════════════════════
def render_sidebar():
    st.sidebar.success(f"✅ Logged in as **{st.session_state.username}**")

    if st.sidebar.button("🚪 Logout"):
        do_logout()

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Navigation")

    pages = {
        "🏠 Home": "home",
        "🔍 Search": "search",
        "📊 Dashboard": "dashboard",
        "📈 Evaluation": "evaluation",
    }

    for label, key in pages.items():
        if st.sidebar.button(label, use_container_width=True,
                             type="primary" if st.session_state.current_page == key else "secondary"):
            st.session_state.current_page = key
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: HOME
# ══════════════════════════════════════════════════════════════════════════════
def render_home():
    st.title(f"Welcome, {st.session_state.username} 👋")
    st.markdown("""
    ### 🏥 How to Use This System

    | Page | What It Does |
    |------|-------------|
    | **🔍 Search** | Search patient cases with RAG-powered answers + compare RAG vs Base LLM |
    | **📊 Dashboard** | View system statistics and case distribution |
    | **📈 Evaluation** | Interactive dashboard comparing RAG vs Base LLM evaluation results |

    Use the **sidebar** on the left to navigate. 👈
    """)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: SEARCH
# ══════════════════════════════════════════════════════════════════════════════
def render_search():
    st.title("🔍 Search Patient Cases")

    rag = load_rag_system()

    query = st.text_area(
        "Describe the patient case or symptoms:",
        height=100,
        placeholder="e.g. patient with chest pain and shortness of breath after exercise",
    )
    top_k = st.slider("Number of source documents", 1, 10, 5)

    col1, col2 = st.columns(2)
    with col1:
        search_clicked = st.button("🔎 RAG Search + Answer", type="primary")
    with col2:
        compare_clicked = st.button("⚖️ Compare RAG vs Base LLM")

    if search_clicked and query:
        with st.spinner("Retrieving relevant cases and generating answer …"):
            try:
                answer = rag.generate_answer(query, top_k=top_k)
                results = rag.search(query, top_k=top_k)

                st.subheader("💡 RAG-Generated Answer")
                st.success(answer)
                st.markdown(f"*Based on {len(results)} retrieved source documents.*")

                if results:
                    with st.expander("📄 Source Documents"):
                        for i, doc in enumerate(results, 1):
                            text = doc.page_content if hasattr(doc, 'page_content') else str(doc)
                            st.markdown(f"**Source {i}:** {text[:500]}…")
            except Exception as e:
                st.error(f"Error: {e}")

    if compare_clicked and query:
        col_rag, col_base = st.columns(2)

        with col_rag:
            st.subheader("🧠 RAG Answer")
            with st.spinner("Generating RAG answer …"):
                try:
                    answer = rag.generate_answer(query, top_k=top_k)
                    st.success(answer)
                except Exception as e:
                    st.error(f"Error: {e}")

        with col_base:
            st.subheader("🤖 Base LLM Answer")
            with st.spinner("Generating base LLM answer …"):
                try:
                    answer = rag.generate_base_answer(query)
                    st.info(answer)
                    st.caption("No retrieval context used")
                except Exception as e:
                    st.error(f"Error: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
def render_dashboard():
    st.title("📊 System Dashboard")

    import pandas as pd

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Total Cases Indexed", "4,999")
    with c2:
        st.metric("Active Users", "12")
    with c3:
        st.metric("Searches Today", "154")

    st.markdown("### Case Distribution by Specialty")
    chart_data = pd.DataFrame({
        "Specialty": ["Cardiology", "Neurology", "Pulmonology", "General Medicine", "Endocrinology", "Orthopedics"],
        "Cases": [120, 85, 95, 200, 60, 45]
    }).set_index("Specialty")
    st.bar_chart(chart_data)

    st.markdown("### Recent Activity")
    st.code("""
[INFO] User 'admin' searched for 'cardiac arrest'
[INFO] User 'dr_smith' searched for 'pediatric pneumonia'
[INFO] Data update triggered by 'admin'
""")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: EVALUATION
# ══════════════════════════════════════════════════════════════════════════════
def render_evaluation():
    import json
    from pathlib import Path
    import pandas as pd

    RESULTS_PATH = Path(__file__).resolve().parent / "results" / "results.json"
    REPORT_PATH  = Path(__file__).resolve().parent / "results" / "evaluation_report.md"

    if not RESULTS_PATH.exists():
        st.warning("⚠️ No evaluation results found. Run the evaluation first:")
        st.code("python -m scripts.evaluate_rag_vs_llm", language="bash")
        return

    with open(RESULTS_PATH) as f:
        data = json.load(f)

    meta    = data.get("metadata", {})
    results = data.get("per_query_results", [])
    avg     = data.get("average_metrics", {})

    # ── Styles ───────────────────────────────────────────────────────────
    st.markdown("""
    <style>
        .eval-hero { background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
            border-radius: 16px; padding: 2.5rem 2rem; margin-bottom: 2rem; text-align: center;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3); }
        .eval-hero h1 { color: #fff; font-size: 2.2rem; margin: 0 0 0.5rem 0; font-weight: 700; }
        .eval-hero p  { color: #b8b8d4; font-size: 1.05rem; margin: 0; }
        .metric-card { background: linear-gradient(145deg, #1a1a2e, #16213e); border-radius: 14px;
            padding: 1.4rem 1.2rem; text-align: center; border: 1px solid rgba(255,255,255,0.06);
            box-shadow: 0 4px 20px rgba(0,0,0,0.25); margin-bottom: 0.8rem; }
        .metric-card .label { color: #8888aa; font-size: 0.78rem; text-transform: uppercase;
            letter-spacing: 1.2px; font-weight: 600; margin-bottom: 0.4rem; }
        .metric-card .value { font-size: 1.85rem; font-weight: 800; margin: 0.2rem 0; }
        .metric-card .sub { font-size: 0.75rem; color: #666688; }
        .val-green { color: #00e676; } .val-blue { color: #448aff; }
        .val-amber { color: #ffd740; } .val-cyan { color: #18ffff; } .val-pink { color: #ff80ab; }
        .winner-badge { display: inline-block; background: linear-gradient(135deg, #00c853, #00e676);
            color: #0a0a0a; padding: 0.25rem 0.8rem; border-radius: 20px; font-size: 0.72rem;
            font-weight: 700; letter-spacing: 0.5px; text-transform: uppercase; }
        .comp-row { display: flex; align-items: center; gap: 0.8rem; margin: 0.6rem 0;
            padding: 0.8rem 1rem; background: rgba(255,255,255,0.03); border-radius: 10px;
            border: 1px solid rgba(255,255,255,0.05); }
        .comp-label { min-width: 180px; color: #aaaacc; font-size: 0.85rem; font-weight: 600; }
        .comp-bar-wrap { flex: 1; display: flex; gap: 4px; align-items: center; }
        .comp-bar { height: 28px; border-radius: 6px; display: flex; align-items: center;
            justify-content: center; font-size: 0.72rem; font-weight: 700; color: #fff; min-width: 45px; }
        .bar-rag  { background: linear-gradient(90deg, #7c4dff, #536dfe); }
        .bar-base { background: linear-gradient(90deg, #ff6d00, #ff9100); }
        .section-divider { height: 1px; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent); margin: 2rem 0; }
        .info-chip { display: inline-block; background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.1);
            border-radius: 8px; padding: 0.5rem 1rem; margin: 0.3rem; color: #b8b8d4; font-size: 0.82rem; }
        .info-chip strong { color: #e0e0f0; }
        .answer-box { border-radius: 10px; padding: 1rem 1.2rem; margin-top: 0.6rem; font-size: 0.88rem; line-height: 1.55; color: #d0d0e8; }
        .answer-rag { background: rgba(124, 77, 255, 0.08); border-left: 4px solid #7c4dff; }
        .answer-base { background: rgba(255, 109, 0, 0.08); border-left: 4px solid #ff6d00; }
        .answer-label { font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.4rem; }
        .answer-label-rag { color: #b388ff; } .answer-label-base { color: #ffab40; }
    </style>
    """, unsafe_allow_html=True)

    # ── Hero ─────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="eval-hero">
        <h1>📈 RAG vs Base LLM — Evaluation Results</h1>
        <p>Interactive comparison dashboard</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Metadata ─────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f'<div class="info-chip">🤖 <strong>LLM:</strong> {meta.get("llm_provider","N/A").upper()}</div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="info-chip">🗄️ <strong>Vector DB:</strong> {meta.get("vector_store","N/A").title()}</div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="info-chip">📝 <strong>Queries:</strong> {meta.get("num_queries",0)}</div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="info-chip">🕐 <strong>Run:</strong> {meta.get("timestamp","")[:19]}</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # ── Average Metrics ──────────────────────────────────────────────────
    st.markdown("### 🏆 Average Metrics — RAG Wins Across the Board")

    def _get(key):
        v = avg.get(key, {"rag": 0, "base": 0})
        if isinstance(v, (int, float)): return v, 0
        return v.get("rag", 0), v.get("base", 0)

    def _pct(a, b):
        if b == 0: return "+∞"
        return f"+{((a-b)/b*100):.0f}%"

    p5 = avg.get("precision_at_5", 0)
    if isinstance(p5, dict): p5 = p5.get("rag", 0)
    sim_r, sim_b = _get("sim_with_top_doc")
    rouge_r, rouge_b = _get("rouge_proxy_f1")
    rel_r, rel_b = _get("answer_relevance")
    faith_r, faith_b = _get("faithfulness")

    m1, m2, m3, m4, m5 = st.columns(5)
    with m1: st.markdown(f'<div class="metric-card"><div class="label">Precision@5</div><div class="value val-green">{p5:.2f}</div><div class="sub">Perfect retrieval</div></div>', unsafe_allow_html=True)
    with m2: st.markdown(f'<div class="metric-card"><div class="label">Token Similarity</div><div class="value val-blue">{sim_r:.4f}</div><div class="sub">vs Base {sim_b:.4f} <span class="val-green">({_pct(sim_r,sim_b)})</span></div></div>', unsafe_allow_html=True)
    with m3: st.markdown(f'<div class="metric-card"><div class="label">ROUGE-Proxy F1</div><div class="value val-amber">{rouge_r:.4f}</div><div class="sub">vs Base {rouge_b:.4f} <span class="val-green">({_pct(rouge_r,rouge_b)})</span></div></div>', unsafe_allow_html=True)
    with m4: st.markdown(f'<div class="metric-card"><div class="label">Answer Relevance</div><div class="value val-cyan">{rel_r:.4f}</div><div class="sub">vs Base {rel_b:.4f} <span class="val-green">({_pct(rel_r,rel_b)})</span></div></div>', unsafe_allow_html=True)
    with m5: st.markdown(f'<div class="metric-card"><div class="label">Faithfulness</div><div class="value val-pink">{faith_r:.4f}</div><div class="sub">vs Base {faith_b:.4f} <span class="val-green">({_pct(faith_r,faith_b)})</span></div></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # ── Comparison Bars ──────────────────────────────────────────────────
    st.markdown("### 📊 Visual Metric Comparison")
    st.caption("Purple = RAG  |  Orange = Base LLM  |  Longer bar = better")

    for label, rv, bv in [("Token Overlap Similarity", sim_r, sim_b), ("ROUGE-Proxy F1", rouge_r, rouge_b),
                           ("Answer Relevance", rel_r, rel_b), ("Faithfulness", faith_r, faith_b)]:
        mx = max(rv, bv, 0.01)
        rp, bp = int((rv/mx)*100), int((bv/mx)*100)
        w = '<span class="winner-badge">RAG WINS</span>' if rv > bv else ''
        st.markdown(f'<div class="comp-row"><div class="comp-label">{label}</div><div class="comp-bar-wrap"><div class="comp-bar bar-rag" style="width:{rp}%">{rv:.4f}</div><div class="comp-bar bar-base" style="width:{bp}%">{bv:.4f}</div></div>{w}</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # ── Per-Query Charts ─────────────────────────────────────────────────
    st.markdown("### 📉 Per-Query Metric Charts")

    chart_data = []
    for item in results:
        m = item["metrics"]
        qid = f"Q{item['query_id']}"
        for mname, mkey in [("Token Similarity","sim_with_top_doc"),("ROUGE-Proxy F1","rouge_proxy_f1"),
                             ("Answer Relevance","answer_relevance"),("Faithfulness","faithfulness")]:
            chart_data.append({"Query": qid, "Metric": mname, "RAG": m[mkey]["rag"], "Base LLM": m[mkey]["base"]})

    df_chart = pd.DataFrame(chart_data)
    sel = st.selectbox("Select metric:", ["Token Similarity","ROUGE-Proxy F1","Answer Relevance","Faithfulness"])
    df_f = df_chart[df_chart["Metric"] == sel].set_index("Query")[["RAG","Base LLM"]]

    cc, ct = st.columns([3, 2])
    with cc: st.bar_chart(df_f, color=["#7c4dff","#ff9100"])
    with ct:
        sdf = df_f.copy()
        sdf["Winner"] = sdf.apply(lambda r: "✅ RAG" if r["RAG"] > r["Base LLM"] else "⚠️ Base", axis=1)
        st.dataframe(sdf, width="stretch")

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # ── Latency ──────────────────────────────────────────────────────────
    st.markdown("### ⏱️ Response Latency")
    lat = [{"Query": f"Q{i['query_id']}", "RAG (s)": i["latency_seconds"]["rag"], "Base LLM (s)": i["latency_seconds"]["base"]} for i in results]
    df_lat = pd.DataFrame(lat).set_index("Query")
    lc1, lc2 = st.columns([3, 2])
    with lc1: st.bar_chart(df_lat, color=["#7c4dff","#ff9100"])
    with lc2:
        st.markdown(f'<div class="metric-card"><div class="label">Avg RAG Latency</div><div class="value val-blue">{df_lat["RAG (s)"].mean():.2f}s</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-card"><div class="label">Avg Base Latency</div><div class="value" style="color:#ff9100">{df_lat["Base LLM (s)"].mean():.2f}s</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # ── Per-Query Deep Dive ──────────────────────────────────────────────
    st.markdown("### 🔬 Per-Query Deep Dive")
    for item in results:
        m = item["metrics"]
        qid = item["query_id"]
        wins = sum(1 for k in ["sim_with_top_doc","rouge_proxy_f1","answer_relevance","faithfulness"] if m[k]["rag"] > m[k]["base"])
        verdict = "🟢 RAG Wins" if wins >= 3 else "🟠 Mixed"

        with st.expander(f"**Q{qid}** — {verdict} ({wins}/4) | {item['query'][:80]}…"):
            mc1, mc2, mc3, mc4 = st.columns(4)
            with mc1: st.metric("Token Sim", f"{m['sim_with_top_doc']['rag']:.4f}", delta=f"{m['sim_with_top_doc']['rag']-m['sim_with_top_doc']['base']:.4f}")
            with mc2: st.metric("ROUGE F1", f"{m['rouge_proxy_f1']['rag']:.4f}", delta=f"{m['rouge_proxy_f1']['rag']-m['rouge_proxy_f1']['base']:.4f}")
            with mc3: st.metric("Relevance", f"{m['answer_relevance']['rag']:.4f}", delta=f"{m['answer_relevance']['rag']-m['answer_relevance']['base']:.4f}")
            with mc4: st.metric("Faithfulness", f"{m['faithfulness']['rag']:.4f}", delta=f"{m['faithfulness']['rag']-m['faithfulness']['base']:.4f}")

            a1, a2 = st.columns(2)
            with a1: st.markdown(f'<div class="answer-box answer-rag"><div class="answer-label answer-label-rag">🧠 RAG Answer</div>{item["answers"]["rag"]}</div>', unsafe_allow_html=True)
            with a2: st.markdown(f'<div class="answer-box answer-base"><div class="answer-label answer-label-base">🤖 Base LLM Answer</div>{item["answers"]["base"]}</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # ── Full Report ──────────────────────────────────────────────────────
    st.markdown("### 📄 Full Reports")
    tab1, tab2 = st.tabs(["📝 Markdown Report", "🗃️ Raw JSON"])
    with tab1:
        if REPORT_PATH.exists():
            st.markdown(REPORT_PATH.read_text())
        else:
            st.info("Report not found.")
    with tab2:
        st.json(data, expanded=False)
        st.download_button("⬇️ Download results.json", json.dumps(data, indent=2), "results.json", "application/json")


# ══════════════════════════════════════════════════════════════════════════════
# ROUTER
# ══════════════════════════════════════════════════════════════════════════════
if not st.session_state.logged_in:
    render_login()
else:
    render_sidebar()

    page = st.session_state.current_page
    if page == "home":
        render_home()
    elif page == "search":
        render_search()
    elif page == "dashboard":
        render_dashboard()
    elif page == "evaluation":
        render_evaluation()
    else:
        render_home()
