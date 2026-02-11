"""
📈 Evaluation Results — Interactive RAG vs Base LLM Comparison Dashboard
"""

import streamlit as st
import json
import os
from pathlib import Path

st.set_page_config(page_title="Evaluation Results", page_icon="📈", layout="wide")

# ── Login gate ────────────────────────────────────────────────────────────────
if "access_token" not in st.session_state or not st.session_state.access_token:
    st.warning("🔒 Please login first to view evaluation results.")
    st.stop()

# ── Custom CSS for premium look ──────────────────────────────────────────────
st.markdown("""
<style>
    /* ── Global ── */
    .main .block-container { padding-top: 1.5rem; }
    
    /* ── Hero header ── */
    .eval-hero {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        border-radius: 16px;
        padding: 2.5rem 2rem;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }
    .eval-hero h1 {
        color: #ffffff;
        font-size: 2.2rem;
        margin: 0 0 0.5rem 0;
        font-weight: 700;
    }
    .eval-hero p {
        color: #b8b8d4;
        font-size: 1.05rem;
        margin: 0;
    }
    
    /* ── Metric cards ── */
    .metric-card {
        background: linear-gradient(145deg, #1a1a2e, #16213e);
        border-radius: 14px;
        padding: 1.4rem 1.2rem;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.06);
        box-shadow: 0 4px 20px rgba(0,0,0,0.25);
        transition: transform 0.2s, box-shadow 0.2s;
        margin-bottom: 0.8rem;
    }
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 30px rgba(100,100,255,0.15);
    }
    .metric-card .label {
        color: #8888aa;
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        font-weight: 600;
        margin-bottom: 0.4rem;
    }
    .metric-card .value {
        font-size: 1.85rem;
        font-weight: 800;
        margin: 0.2rem 0;
    }
    .metric-card .sub {
        font-size: 0.75rem;
        color: #666688;
    }
    .val-green { color: #00e676; }
    .val-blue  { color: #448aff; }
    .val-amber { color: #ffd740; }
    .val-cyan  { color: #18ffff; }
    .val-pink  { color: #ff80ab; }
    
    /* ── Winner badge ── */
    .winner-badge {
        display: inline-block;
        background: linear-gradient(135deg, #00c853, #00e676);
        color: #0a0a0a;
        padding: 0.25rem 0.8rem;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    .winner-badge-base {
        background: linear-gradient(135deg, #ff6d00, #ff9100);
    }
    
    /* ── Comparison bar ── */
    .comp-row {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        margin: 0.6rem 0;
        padding: 0.8rem 1rem;
        background: rgba(255,255,255,0.03);
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.05);
    }
    .comp-label {
        min-width: 180px;
        color: #aaaacc;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .comp-bar-wrap {
        flex: 1;
        display: flex;
        gap: 4px;
        align-items: center;
    }
    .comp-bar {
        height: 28px;
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.72rem;
        font-weight: 700;
        color: #fff;
        min-width: 45px;
        transition: width 0.6s ease;
    }
    .bar-rag  { background: linear-gradient(90deg, #7c4dff, #536dfe); }
    .bar-base { background: linear-gradient(90deg, #ff6d00, #ff9100); }
    
    /* ── Query card ── */
    .query-card {
        background: linear-gradient(145deg, #1a1a2e, #16213e);
        border-radius: 14px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border: 1px solid rgba(255,255,255,0.06);
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    }
    .query-title {
        color: #b388ff;
        font-size: 0.82rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.3rem;
    }
    .query-text {
        color: #e8e8f0;
        font-size: 1.05rem;
        font-weight: 500;
        margin-bottom: 1rem;
        line-height: 1.45;
    }
    
    /* ── Answer box ── */
    .answer-box {
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin-top: 0.6rem;
        font-size: 0.88rem;
        line-height: 1.55;
        color: #d0d0e8;
    }
    .answer-rag {
        background: rgba(124, 77, 255, 0.08);
        border-left: 4px solid #7c4dff;
    }
    .answer-base {
        background: rgba(255, 109, 0, 0.08);
        border-left: 4px solid #ff6d00;
    }
    .answer-label {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.4rem;
    }
    .answer-label-rag  { color: #b388ff; }
    .answer-label-base { color: #ffab40; }
    
    /* ── Section divider ── */
    .section-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
        margin: 2rem 0;
    }
    
    /* ── Info chip ── */
    .info-chip {
        display: inline-block;
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 8px;
        padding: 0.5rem 1rem;
        margin: 0.3rem 0.3rem 0.3rem 0;
        color: #b8b8d4;
        font-size: 0.82rem;
    }
    .info-chip strong { color: #e0e0f0; }
</style>
""", unsafe_allow_html=True)

# ── Load data ────────────────────────────────────────────────────────────────
RESULTS_PATH = Path(__file__).resolve().parents[2] / "results" / "results.json"
REPORT_PATH  = Path(__file__).resolve().parents[2] / "results" / "evaluation_report.md"

if not RESULTS_PATH.exists():
    st.warning("⚠️ No evaluation results found. Run the evaluation first:")
    st.code("python -m scripts.evaluate_rag_vs_llm", language="bash")
    st.stop()

with open(RESULTS_PATH) as f:
    data = json.load(f)

meta    = data.get("metadata", {})
results = data.get("per_query_results", [])
avg     = data.get("average_metrics", {})

# ── Hero Header ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="eval-hero">
    <h1>📈 RAG vs Base LLM — Evaluation Results</h1>
    <p>Interactive comparison dashboard showing how Retrieval-Augmented Generation outperforms a standalone LLM</p>
</div>
""", unsafe_allow_html=True)

# ── Metadata chips ───────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="info-chip">🤖 <strong>LLM:</strong> {meta.get("llm_provider", "N/A").upper()}</div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="info-chip">🗄️ <strong>Vector DB:</strong> {meta.get("vector_store", "N/A").title()}</div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="info-chip">📝 <strong>Queries:</strong> {meta.get("num_queries", 0)}</div>', unsafe_allow_html=True)
with c4:
    ts = meta.get("timestamp", "")[:19]
    st.markdown(f'<div class="info-chip">🕐 <strong>Run:</strong> {ts}</div>', unsafe_allow_html=True)

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# Section 1: Average Metrics Overview
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("### 🏆 Average Metrics — RAG Wins Across the Board")
st.caption("Each metric averaged over all 5 evaluation queries")

m1, m2, m3, m4, m5 = st.columns(5)

p5 = avg.get("precision_at_5", 0)
if isinstance(p5, dict):
    p5 = p5.get("rag", 0)

def _get_rag_base(key):
    v = avg.get(key, {"rag": 0, "base": 0})
    return v.get("rag", 0), v.get("base", 0)

sim_r, sim_b     = _get_rag_base("sim_with_top_doc")
rouge_r, rouge_b = _get_rag_base("rouge_proxy_f1")
rel_r, rel_b     = _get_rag_base("answer_relevance")
faith_r, faith_b = _get_rag_base("faithfulness")

def _pct_change(a, b):
    if b == 0:
        return "+∞"
    return f"+{((a - b) / b * 100):.0f}%"

with m1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="label">Precision@5</div>
        <div class="value val-green">{p5:.2f}</div>
        <div class="sub">Perfect retrieval</div>
    </div>""", unsafe_allow_html=True)
with m2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="label">Token Similarity</div>
        <div class="value val-blue">{sim_r:.4f}</div>
        <div class="sub">vs Base {sim_b:.4f} <span class="val-green">({_pct_change(sim_r, sim_b)})</span></div>
    </div>""", unsafe_allow_html=True)
with m3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="label">ROUGE-Proxy F1</div>
        <div class="value val-amber">{rouge_r:.4f}</div>
        <div class="sub">vs Base {rouge_b:.4f} <span class="val-green">({_pct_change(rouge_r, rouge_b)})</span></div>
    </div>""", unsafe_allow_html=True)
with m4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="label">Answer Relevance</div>
        <div class="value val-cyan">{rel_r:.4f}</div>
        <div class="sub">vs Base {rel_b:.4f} <span class="val-green">({_pct_change(rel_r, rel_b)})</span></div>
    </div>""", unsafe_allow_html=True)
with m5:
    st.markdown(f"""
    <div class="metric-card">
        <div class="label">Faithfulness</div>
        <div class="value val-pink">{faith_r:.4f}</div>
        <div class="sub">vs Base {faith_b:.4f} <span class="val-green">({_pct_change(faith_r, faith_b)})</span></div>
    </div>""", unsafe_allow_html=True)

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# Section 2: Visual Comparison Bars
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("### 📊 Visual Metric Comparison")
st.caption("Purple = RAG  |  Orange = Base LLM  |  Longer bar = better")

metrics_for_bars = [
    ("Token Overlap Similarity", sim_r, sim_b),
    ("ROUGE-Proxy F1",           rouge_r, rouge_b),
    ("Answer Relevance",         rel_r, rel_b),
    ("Faithfulness",             faith_r, faith_b),
]

for label, rag_val, base_val in metrics_for_bars:
    max_val = max(rag_val, base_val, 0.01)
    rag_pct  = int((rag_val / max_val) * 100)
    base_pct = int((base_val / max_val) * 100)
    
    winner_html = '<span class="winner-badge">RAG WINS</span>' if rag_val > base_val else '<span class="winner-badge winner-badge-base">BASE WINS</span>' if base_val > rag_val else ''

    st.markdown(f"""
    <div class="comp-row">
        <div class="comp-label">{label}</div>
        <div class="comp-bar-wrap">
            <div class="comp-bar bar-rag" style="width:{rag_pct}%">{rag_val:.4f}</div>
            <div class="comp-bar bar-base" style="width:{base_pct}%">{base_val:.4f}</div>
        </div>
        {winner_html}
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# Section 3: Interactive Charts (using Streamlit native)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("### 📉 Per-Query Metric Charts")

import pandas as pd

# Build comparison dataframe
chart_data = []
for item in results:
    m = item["metrics"]
    qid = f"Q{item['query_id']}"
    chart_data.append({
        "Query": qid,
        "Metric": "Token Similarity",
        "RAG": m["sim_with_top_doc"]["rag"],
        "Base LLM": m["sim_with_top_doc"]["base"],
    })
    chart_data.append({
        "Query": qid,
        "Metric": "ROUGE-Proxy F1",
        "RAG": m["rouge_proxy_f1"]["rag"],
        "Base LLM": m["rouge_proxy_f1"]["base"],
    })
    chart_data.append({
        "Query": qid,
        "Metric": "Answer Relevance",
        "RAG": m["answer_relevance"]["rag"],
        "Base LLM": m["answer_relevance"]["base"],
    })
    chart_data.append({
        "Query": qid,
        "Metric": "Faithfulness",
        "RAG": m["faithfulness"]["rag"],
        "Base LLM": m["faithfulness"]["base"],
    })

df_chart = pd.DataFrame(chart_data)

# Filter by metric
selected_metric = st.selectbox(
    "Select metric to visualize across queries:",
    ["Token Similarity", "ROUGE-Proxy F1", "Answer Relevance", "Faithfulness"],
    index=0,
)

df_filtered = df_chart[df_chart["Metric"] == selected_metric].set_index("Query")[["RAG", "Base LLM"]]

col_chart, col_table = st.columns([3, 2])
with col_chart:
    st.bar_chart(df_filtered, color=["#7c4dff", "#ff9100"])
with col_table:
    st.markdown(f"**{selected_metric} — Per Query**")
    styled_df = df_filtered.copy()
    styled_df["Winner"] = styled_df.apply(
        lambda row: "✅ RAG" if row["RAG"] > row["Base LLM"] else "⚠️ Base" if row["Base LLM"] > row["RAG"] else "Tie",
        axis=1,
    )
    styled_df["Δ (RAG − Base)"] = (styled_df["RAG"] - styled_df["Base LLM"]).round(4)
    st.dataframe(styled_df, width="stretch")

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# Section 4: Latency Comparison
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("### ⏱️ Response Latency Comparison")

latency_data = []
for item in results:
    latency_data.append({
        "Query": f"Q{item['query_id']}",
        "RAG (s)": item["latency_seconds"]["rag"],
        "Base LLM (s)": item["latency_seconds"]["base"],
    })
df_latency = pd.DataFrame(latency_data).set_index("Query")

lc1, lc2 = st.columns([3, 2])
with lc1:
    st.bar_chart(df_latency, color=["#7c4dff", "#ff9100"])
with lc2:
    avg_rag_lat = df_latency["RAG (s)"].mean()
    avg_base_lat = df_latency["Base LLM (s)"].mean()
    st.markdown(f"""
    <div class="metric-card">
        <div class="label">Avg RAG Latency</div>
        <div class="value val-blue">{avg_rag_lat:.2f}s</div>
        <div class="sub">includes retrieval + generation</div>
    </div>
    <div class="metric-card">
        <div class="label">Avg Base LLM Latency</div>
        <div class="value" style="color:#ff9100">{avg_base_lat:.2f}s</div>
        <div class="sub">generation only</div>
    </div>
    <div class="metric-card">
        <div class="label">RAG Overhead</div>
        <div class="value val-amber">{avg_rag_lat - avg_base_lat:.2f}s</div>
        <div class="sub">small price for much better accuracy</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# Section 5: Per-Query Deep Dive
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("### 🔬 Per-Query Deep Dive")
st.caption("Expand each query to see the full answers from both RAG and Base LLM")

for item in results:
    m = item["metrics"]
    qid = item["query_id"]
    query = item["query"]
    
    # Count wins for this query
    wins_rag = 0
    wins_base = 0
    for mk in ["sim_with_top_doc", "rouge_proxy_f1", "answer_relevance", "faithfulness"]:
        if m[mk]["rag"] > m[mk]["base"]:
            wins_rag += 1
        elif m[mk]["base"] > m[mk]["rag"]:
            wins_base += 1
    
    verdict = "🟢 RAG Wins" if wins_rag > wins_base else "🟠 Base Wins" if wins_base > wins_rag else "🟡 Tie"
    
    with st.expander(f"**Query {qid}** — {verdict} ({wins_rag}/4 metrics) | {query[:80]}…"):
        st.markdown(f"""
        <div class="query-card">
            <div class="query-title">Query {qid}</div>
            <div class="query-text">{query}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Mini metrics row
        mc1, mc2, mc3, mc4, mc5 = st.columns(5)
        with mc1:
            st.metric("Precision@5", f"{m['precision_at_5']:.2f}")
        with mc2:
            st.metric("Token Sim", f"{m['sim_with_top_doc']['rag']:.4f}",
                      delta=f"{m['sim_with_top_doc']['rag'] - m['sim_with_top_doc']['base']:.4f}")
        with mc3:
            st.metric("ROUGE F1", f"{m['rouge_proxy_f1']['rag']:.4f}",
                      delta=f"{m['rouge_proxy_f1']['rag'] - m['rouge_proxy_f1']['base']:.4f}")
        with mc4:
            st.metric("Relevance", f"{m['answer_relevance']['rag']:.4f}",
                      delta=f"{m['answer_relevance']['rag'] - m['answer_relevance']['base']:.4f}")
        with mc5:
            st.metric("Faithfulness", f"{m['faithfulness']['rag']:.4f}",
                      delta=f"{m['faithfulness']['rag'] - m['faithfulness']['base']:.4f}")
        
        # Answers side by side
        ans_col1, ans_col2 = st.columns(2)
        with ans_col1:
            st.markdown(f"""
            <div class="answer-box answer-rag">
                <div class="answer-label answer-label-rag">🧠 RAG Answer</div>
                {item['answers']['rag']}
            </div>
            """, unsafe_allow_html=True)
        with ans_col2:
            st.markdown(f"""
            <div class="answer-box answer-base">
                <div class="answer-label answer-label-base">🤖 Base LLM Answer</div>
                {item['answers']['base']}
            </div>
            """, unsafe_allow_html=True)

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# Section 6: Full Report & Raw JSON
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("### 📄 Full Reports")

tab_report, tab_json = st.tabs(["📝 Evaluation Report (Markdown)", "🗃️ Raw JSON Data"])

with tab_report:
    if REPORT_PATH.exists():
        with open(REPORT_PATH) as f:
            report_md = f.read()
        st.markdown(report_md)
    else:
        st.info("Markdown report not found. Run the evaluation script to generate it.")

with tab_json:
    st.json(data, expanded=False)
    st.download_button(
        label="⬇️ Download results.json",
        data=json.dumps(data, indent=2),
        file_name="rag_vs_llm_results.json",
        mime="application/json",
    )

# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center; color:#666688; font-size:0.8rem; padding:1rem 0;">
    Medical RAG System v2.0 — Evaluation Dashboard<br/>
    Built with Streamlit • Groq (Llama 3.3 70B) • Pinecone • Cohere
</div>
""", unsafe_allow_html=True)
