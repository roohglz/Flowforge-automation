import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import create_tables, SessionLocal, Workflow, WorkflowStep
from datetime import datetime

def seed_data():
    db = SessionLocal()

    # Create sample workflows
    workflows = [
        Workflow(
            name="Invoice Processing",
            description="Automates extraction and validation of invoice documents",
            status="active",
            total_documents=150,
            processed_documents=142
        ),
        Workflow(
            name="HR Document Handler",
            description="Processes employee onboarding and HR documents",
            status="active",
            total_documents=89,
            processed_documents=89
        ),
        Workflow(
            name="Contract Review",
            description="Extracts key clauses and flags important sections in contracts",
            status="paused",
            total_documents=45,
            processed_documents=38
        ),
        Workflow(
            name="Financial Reports",
            description="Processes and summarizes monthly financial reports",
            status="active",
            total_documents=200,
            processed_documents=198
        ),
    ]

    for w in workflows:
        db.add(w)
    db.commit()

    # Add steps for first workflow
    steps = [
        WorkflowStep(workflow_id=1, step_name="Upload", step_type="upload", order=1, status="completed"),
        WorkflowStep(workflow_id=1, step_name="Extract Text", step_type="extract", order=2, status="completed"),
        WorkflowStep(workflow_id=1, step_name="Summarize", step_type="summarize", order=3, status="completed"),
        WorkflowStep(workflow_id=1, step_name="Export", step_type="export", order=4, status="pending"),
    ]

    for s in steps:
        db.add(s)
    db.commit()
    db.close()

    print("✅ Sample data seeded!")

if __name__ == '__main__':
    create_tables()
    seed_data()
