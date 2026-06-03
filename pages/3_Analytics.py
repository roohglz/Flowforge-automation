import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import plotly.express as px
import pandas as pd
from processors.workflow_engine import get_all_workflows

st.set_page_config(page_title="Analytics", page_icon="📊", layout="wide")

st.title("📊 Analytics")
st.caption("Workflow performance and document processing insights")

st.divider()

workflows = get_all_workflows()
df = pd.DataFrame(workflows)

if df.empty:
    st.info("No workflow data yet.")
    st.stop()

col1, col2 = st.columns(2)

with col1:
    fig = px.bar(
        df, x='name', y='completion_rate',
        title='Completion Rate by Workflow',
        color='completion_rate',
        color_continuous_scale='Viridis',
        labels={'completion_rate': 'Completion %', 'name': 'Workflow'}
    )
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.pie(
        df, names='name', values='total_documents',
        title='Document Distribution by Workflow',
        hole=0.4,
        color_discrete_sequence=['#6366f1','#8b5cf6','#ec4899','#f59e0b']
    )
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

st.divider()

status_counts = df['status'].value_counts().reset_index()
status_counts.columns = ['status', 'count']

fig = px.bar(
    status_counts, x='status', y='count',
    title='Workflows by Status',
    color='status',
    color_discrete_map={'active': '#10b981', 'paused': '#f59e0b', 'archived': '#6b7280'}
)
fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
st.plotly_chart(fig, use_container_width=True)

st.divider()
st.subheader("📋 Workflow Details")
st.dataframe(df[['name', 'status', 'total_documents', 'processed_documents', 'completion_rate']], use_container_width=True)
