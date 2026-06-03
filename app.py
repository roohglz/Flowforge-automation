import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import streamlit as st
from processors.workflow_engine import get_workflow_stats, get_all_workflows

# Auto setup database if it doesn't exist
if not os.path.exists('database/flowforge.db'):
    from database.models import create_tables
    from database.setup_db import seed_data
    create_tables()
    seed_data()

st.set_page_config(
    page_title="FlowForge Automation Suite",
    page_icon="⚡",
    layout="wide"
)

# ── HEADER ───────────────────────────────────────────────────────
st.markdown("""
    <div style='text-align:center; padding: 2rem 0 1rem 0;'>
        <h1 style='font-size:3rem; color:#6366f1;'>⚡ FlowForge</h1>
        <p style='color:#94a3b8; font-size:1.1rem;'>Cloud-based Workflow Automation Suite</p>
    </div>
""", unsafe_allow_html=True)

st.divider()

# ── KPI CARDS ────────────────────────────────────────────────────
stats = get_workflow_stats()

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("⚡ Total Workflows", stats.get("total_workflows", 0))
col2.metric("✅ Active Workflows", stats.get("active_workflows", 0))
col3.metric("📄 Total Documents", stats.get("total_documents", 0))
col4.metric("✔️ Processed", stats.get("processed_documents", 0))
col5.metric("📊 Processing Rate", f"{stats.get('processing_rate', 0)}%")

st.divider()

# ── WORKFLOWS TABLE ──────────────────────────────────────────────
st.subheader("📋 Your Workflows")

workflows = get_all_workflows()

for w in workflows:
    status_color = "#10b981" if w['status'] == 'active' else "#f59e0b" if w['status'] == 'paused' else "#6b7280"
    completion = w['completion_rate']

    with st.container():
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        with col1:
            st.markdown(f"**{w['name']}**")
            st.caption(w['description'])
        with col2:
            st.markdown(f"<span style='color:{status_color}'>● {w['status'].capitalize()}</span>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"📄 {w['processed_documents']}/{w['total_documents']} docs")
        with col4:
            st.markdown(f"**{completion}%** complete")
        st.progress(completion / 100)
        st.markdown("---")

st.divider()
st.markdown("👈 **Use the sidebar to navigate**")
