import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from processors.workflow_engine import get_all_workflows, create_workflow
from database.models import SessionLocal, Workflow

st.set_page_config(page_title="Manage Workflows", page_icon="📋", layout="wide")

st.title("📋 Manage Workflows")
st.caption("Create, monitor and manage your automation workflows")

st.divider()

# ── CREATE WORKFLOW ──────────────────────────────────────────────
st.subheader("➕ Create New Workflow")

with st.form("create_workflow"):
    name = st.text_input("Workflow Name", placeholder="e.g. Invoice Processing")
    description = st.text_area("Description", placeholder="What does this workflow do?")
    submitted = st.form_submit_button("Create Workflow ⚡")

    if submitted:
        if not name:
            st.error("Please enter a workflow name")
        else:
            create_workflow(name, description)
            st.success(f"✅ Workflow '{name}' created successfully!")
            st.rerun()

st.divider()

# ── LIST WORKFLOWS ───────────────────────────────────────────────
st.subheader("📋 All Workflows")

workflows = get_all_workflows()

for w in workflows:
    with st.expander(f"{'🟢' if w['status'] == 'active' else '🟡'} {w['name']} — {w['completion_rate']}% complete"):
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Description:** {w['description']}")
            st.write(f"**Status:** {w['status'].capitalize()}")
            st.write(f"**Documents:** {w['processed_documents']}/{w['total_documents']}")
            st.progress(w['completion_rate'] / 100)
        with col2:
            new_status = st.selectbox(
                "Change Status",
                ["active", "paused", "archived"],
                index=["active", "paused", "archived"].index(w['status']),
                key=f"status_{w['id']}"
            )
            if st.button("Update Status", key=f"update_{w['id']}"):
                db = SessionLocal()
                workflow = db.query(Workflow).filter(Workflow.id == w['id']).first()
                workflow.status = new_status
                db.commit()
                db.close()
                st.success("✅ Updated!")
                st.rerun()

            if st.button("🗑️ Delete", key=f"delete_{w['id']}"):
                db = SessionLocal()
                workflow = db.query(Workflow).filter(Workflow.id == w['id']).first()
                db.delete(workflow)
                db.commit()
                db.close()
                st.success("✅ Deleted!")
                st.rerun()
