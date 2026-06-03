from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'database', 'flowforge.db')
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Workflow(Base):
    __tablename__ = 'workflows'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    status = Column(String, default='active')
    created_at = Column(DateTime, default=datetime.utcnow)
    total_documents = Column(Integer, default=0)
    processed_documents = Column(Integer, default=0)

class Document(Base):
    __tablename__ = 'documents'
    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, nullable=False)
    filename = Column(String, nullable=False)
    file_type = Column(String)
    file_size = Column(Float)
    status = Column(String, default='pending')
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    extracted_text = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    word_count = Column(Integer, default=0)
    processing_time = Column(Float, default=0.0)

class WorkflowStep(Base):
    __tablename__ = 'workflow_steps'
    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, nullable=False)
    step_name = Column(String, nullable=False)
    step_type = Column(String)
    order = Column(Integer)
    status = Column(String, default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)

def create_tables():
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
