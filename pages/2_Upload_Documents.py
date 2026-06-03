import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from processors.workflow_engine import get_all_workflows, upload_and_process
import tempfile

st.set_page_config(page_title="Upload Documents", page_icon="📤", layout="wide")

st.title("📤 Upload & Process Documents")
st.caption("Upload PDF, CSV, or TXT files — FlowForge will extract, summarize and classify them automatically")

st.divider()

# ── SELECT WORKFLOW ──────────────────────────────────────────────
workflows = get_all_workflows()
active_workflows = [w for w in workflows if w['status'] == 'active']

if not active_workflows:
    st.warning("No active workflows found. Please create one first!")
    st.stop()

workflow_names = {w['name']: w['id'] for w in active_workflows}
selected_name = st.selectbox("📋 Select Workflow", list(workflow_names.keys()))
selected_id = workflow_names[selected_name]

st.divider()

# ── FILE UPLOAD ──────────────────────────────────────────────────
st.subheader("📁 Upload Document")
st.caption("Supported formats: PDF, CSV, TXT")

uploaded_file = st.file_uploader("Choose a file", type=['pdf', 'csv', 'txt'])

if uploaded_file:
    st.info(f"📄 File: **{uploaded_file.name}** | Size: **{round(uploaded_file.size/1024, 2)} KB**")

    if st.button("⚡ Process Document", use_container_width=True):
        with st.spinner("Processing document..."):
            # Save to temp file
            suffix = os.path.splitext(uploaded_file.name)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name

            file_size = round(uploaded_file.size / 1024, 2)
            result = upload_and_process(selected_id, tmp_path, uploaded_file.name, file_size)
            os.unlink(tmp_path)

            if result.get("status") == "completed":
                st.success("✅ Document processed successfully!")
                st.divider()

                col1, col2, col3 = st.columns(3)
                col1.metric("📝 Word Count", result.get("word_count", 0))
                col2.metric("⏱️ Processing Time", f"{result.get('processing_time', 0)}s")
                col3.metric("🏷️ Document Type", result.get("doc_type", "Unknown"))

                st.divider()
                st.subheader("📋 Summary")
                st.write(result.get("summary", "No summary available"))
            else:
                st.error(f"❌ Processing failed: {result.get('error', 'Unknown error')}")

st.divider()

# ── DOCUMENTS IN THIS WORKFLOW ───────────────────────────────────
st.subheader(f"📂 Documents in '{selected_name}'")

from processors.workflow_engine import get_documents_by_workflow
docs = get_documents_by_workflow(selected_id)

if not docs:
    st.info("No documents uploaded yet. Upload your first document above!")
else:
    for doc in docs:
        status_icon = "✅" if doc['status'] == 'completed' else "⏳" if doc['status'] == 'processing' else "❌"
        with st.expander(f"{status_icon} {doc['filename']} — {doc['word_count']} words"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Type:** {doc['file_type']}")
                st.write(f"**Size:** {doc['file_size']} KB")
                st.write(f"**Status:** {doc['status']}")
                st.write(f"**Processing Time:** {doc['processing_time']}s")
            with col2:
                st.write("**Summary:**")
                st.write(doc['summary'] or "Not yet processed")
