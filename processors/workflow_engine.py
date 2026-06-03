import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import SessionLocal, Workflow, Document, WorkflowStep
from processors.document_processor import process_document
from datetime import datetime

def get_workflow_stats():
    db = SessionLocal()
    workflows = db.query(Workflow).all()

    stats = {
        "total_workflows": len(workflows),
        "active_workflows": len([w for w in workflows if w.status == 'active']),
        "total_documents": sum(w.total_documents for w in workflows),
        "processed_documents": sum(w.processed_documents for w in workflows),
    }
    stats["processing_rate"] = round(
        stats["processed_documents"] / stats["total_documents"] * 100, 1
    ) if stats["total_documents"] > 0 else 0

    db.close()
    return stats

def get_all_workflows():
    db = SessionLocal()
    workflows = db.query(Workflow).all()
    result = []
    for w in workflows:
        result.append({
            "id": w.id,
            "name": w.name,
            "description": w.description,
            "status": w.status,
            "total_documents": w.total_documents,
            "processed_documents": w.processed_documents,
            "created_at": str(w.created_at),
            "completion_rate": round(w.processed_documents / w.total_documents * 100, 1) if w.total_documents > 0 else 0
        })
    db.close()
    return result

def create_workflow(name, description):
    db = SessionLocal()
    workflow = Workflow(name=name, description=description, status='active')
    db.add(workflow)
    db.commit()
    db.refresh(workflow)

    # Auto create default steps
    steps = [
        WorkflowStep(workflow_id=workflow.id, step_name="Upload", step_type="upload", order=1, status="completed"),
        WorkflowStep(workflow_id=workflow.id, step_name="Extract Text", step_type="extract", order=2, status="pending"),
        WorkflowStep(workflow_id=workflow.id, step_name="Summarize", step_type="summarize", order=3, status="pending"),
        WorkflowStep(workflow_id=workflow.id, step_name="Export", step_type="export", order=4, status="pending"),
    ]
    for s in steps:
        db.add(s)
    db.commit()
    db.close()

    print(f"✅ Workflow created: {name}")
    return workflow.id

def upload_and_process(workflow_id, filepath, filename, file_size):
    db = SessionLocal()

    # Save document record
    doc = Document(
        workflow_id=workflow_id,
        filename=filename,
        file_type=os.path.splitext(filename)[1].lower(),
        file_size=file_size,
        status='pending'
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # Update workflow count
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if workflow:
        workflow.total_documents += 1
        db.commit()

    doc_id = doc.id
    db.close()

    # Process it
    result = process_document(doc_id, filepath)

    # Update workflow processed count
    if result.get("status") == "completed":
        db = SessionLocal()
        workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
        if workflow:
            workflow.processed_documents += 1
            db.commit()
        db.close()

    return result

def get_documents_by_workflow(workflow_id):
    db = SessionLocal()
    docs = db.query(Document).filter(Document.workflow_id == workflow_id).all()
    result = []
    for d in docs:
        result.append({
            "id": d.id,
            "filename": d.filename,
            "file_type": d.file_type,
            "file_size": d.file_size,
            "status": d.status,
            "uploaded_at": str(d.uploaded_at),
            "word_count": d.word_count,
            "processing_time": d.processing_time,
            "summary": d.summary
        })
    db.close()
    return result
