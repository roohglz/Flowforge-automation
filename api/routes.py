import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import shutil

from processors.workflow_engine import (
    get_workflow_stats,
    get_all_workflows,
    create_workflow,
    upload_and_process,
    get_documents_by_workflow
)
from database.models import SessionLocal, Workflow, Document

app = FastAPI(
    title="FlowForge Automation Suite",
    description="Cloud-based workflow automation platform for document-intensive operations",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ── MODELS ───────────────────────────────────────────────────────
class WorkflowCreate(BaseModel):
    name: str
    description: Optional[str] = ""

class WorkflowUpdate(BaseModel):
    status: str

# ── HEALTH CHECK ─────────────────────────────────────────────────
@app.get("/")
def root():
    return {"message": "FlowForge API is running", "version": "1.0.0"}

@app.get("/health")
def health():
    return {"status": "healthy"}

# ── DASHBOARD STATS ──────────────────────────────────────────────
@app.get("/api/stats")
def get_stats():
    return get_workflow_stats()

# ── WORKFLOWS ────────────────────────────────────────────────────
@app.get("/api/workflows")
def list_workflows():
    return get_all_workflows()

@app.post("/api/workflows")
def create_new_workflow(workflow: WorkflowCreate):
    workflow_id = create_workflow(workflow.name, workflow.description)
    return {"message": "Workflow created", "workflow_id": workflow_id}

@app.get("/api/workflows/{workflow_id}")
def get_workflow(workflow_id: int):
    db = SessionLocal()
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    db.close()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return {
        "id": workflow.id,
        "name": workflow.name,
        "description": workflow.description,
        "status": workflow.status,
        "total_documents": workflow.total_documents,
        "processed_documents": workflow.processed_documents,
        "created_at": str(workflow.created_at)
    }

@app.patch("/api/workflows/{workflow_id}")
def update_workflow_status(workflow_id: int, update: WorkflowUpdate):
    db = SessionLocal()
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        db.close()
        raise HTTPException(status_code=404, detail="Workflow not found")
    workflow.status = update.status
    db.commit()
    db.close()
    return {"message": f"Workflow status updated to {update.status}"}

@app.delete("/api/workflows/{workflow_id}")
def delete_workflow(workflow_id: int):
    db = SessionLocal()
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        db.close()
        raise HTTPException(status_code=404, detail="Workflow not found")
    db.delete(workflow)
    db.commit()
    db.close()
    return {"message": "Workflow deleted"}

# ── DOCUMENTS ────────────────────────────────────────────────────
@app.get("/api/workflows/{workflow_id}/documents")
def list_documents(workflow_id: int):
    return get_documents_by_workflow(workflow_id)

@app.post("/api/workflows/{workflow_id}/upload")
async def upload_document(
    workflow_id: int,
    file: UploadFile = File(...)
):
    allowed_types = ['.txt', '.csv', '.pdf']
    ext = os.path.splitext(file.filename)[1].lower()

    if ext not in allowed_types:
        raise HTTPException(status_code=400, detail=f"File type {ext} not supported. Use: {allowed_types}")

    # Save file
    filepath = os.path.join(UPLOAD_DIR, file.filename)
    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)

    file_size = round(os.path.getsize(filepath) / 1024, 2)  # KB

    # Process
    result = upload_and_process(workflow_id, filepath, file.filename, file_size)
    return result

@app.get("/api/documents/{document_id}")
def get_document(document_id: int):
    db = SessionLocal()
    doc = db.query(Document).filter(Document.id == document_id).first()
    db.close()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return {
        "id": doc.id,
        "filename": doc.filename,
        "file_type": doc.file_type,
        "status": doc.status,
        "summary": doc.summary,
        "extracted_text": doc.extracted_text,
        "word_count": doc.word_count,
        "processing_time": doc.processing_time,
        "uploaded_at": str(doc.uploaded_at),
        "processed_at": str(doc.processed_at)
    }

@app.delete("/api/documents/{document_id}")
def delete_document(document_id: int):
    db = SessionLocal()
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        db.close()
        raise HTTPException(status_code=404, detail="Document not found")
    db.delete(doc)
    db.commit()
    db.close()
    return {"message": "Document deleted"}
