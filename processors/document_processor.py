import os
import time
import re
from datetime import datetime
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import SessionLocal, Document

# ── TEXT EXTRACTION ──────────────────────────────────────────────
def extract_from_txt(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()

def extract_from_csv(filepath):
    import pandas as pd
    df = pd.read_csv(filepath)
    summary_text = f"CSV File with {len(df)} rows and {len(df.columns)} columns.\n"
    summary_text += f"Columns: {', '.join(df.columns.tolist())}\n\n"
    summary_text += f"First 5 rows:\n{df.head().to_string()}"
    return summary_text

def extract_from_pdf(filepath):
    try:
        import PyPDF2
        text = ""
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""
        return text if text.strip() else "Could not extract text from PDF."
    except Exception as e:
        return f"PDF extraction error: {str(e)}"

def extract_text(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    if ext == '.txt':
        return extract_from_txt(filepath)
    elif ext == '.csv':
        return extract_from_csv(filepath)
    elif ext == '.pdf':
        return extract_from_pdf(filepath)
    else:
        return "Unsupported file type."

# ── SUMMARIZER ───────────────────────────────────────────────────
def summarize_text(text, max_sentences=5):
    if not text or len(text.strip()) < 50:
        return "Text too short to summarize."

    # Clean text
    text = re.sub(r'\s+', ' ', text).strip()

    # Split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

    if not sentences:
        return text[:300] + "..."

    # Score sentences by word frequency
    words = re.findall(r'\w+', text.lower())
    word_freq = {}
    for word in words:
        if len(word) > 3:
            word_freq[word] = word_freq.get(word, 0) + 1

    # Score each sentence
    sentence_scores = []
    for sentence in sentences:
        score = sum(word_freq.get(w.lower(), 0) for w in re.findall(r'\w+', sentence))
        sentence_scores.append((score, sentence))

    # Pick top sentences
    top = sorted(sentence_scores, reverse=True)[:max_sentences]
    top_sentences = [s for _, s in top]

    return ' '.join(top_sentences)

# ── CLASSIFIER ───────────────────────────────────────────────────
def classify_document(text, filename):
    text_lower = text.lower()
    filename_lower = filename.lower()

    if any(k in text_lower or k in filename_lower for k in ['invoice', 'payment', 'bill', 'amount due']):
        return 'Invoice'
    elif any(k in text_lower or k in filename_lower for k in ['contract', 'agreement', 'terms', 'clause']):
        return 'Contract'
    elif any(k in text_lower or k in filename_lower for k in ['report', 'analysis', 'summary', 'quarterly']):
        return 'Report'
    elif any(k in text_lower or k in filename_lower for k in ['hr', 'employee', 'onboarding', 'resume', 'cv']):
        return 'HR Document'
    elif any(k in text_lower or k in filename_lower for k in ['financial', 'revenue', 'profit', 'loss', 'balance']):
        return 'Financial Document'
    else:
        return 'General Document'

# ── MAIN PROCESSOR ───────────────────────────────────────────────
def process_document(document_id, filepath):
    db = SessionLocal()
    doc = db.query(Document).filter(Document.id == document_id).first()

    if not doc:
        db.close()
        return {"error": "Document not found"}

    start_time = time.time()

    try:
        # Update status to processing
        doc.status = 'processing'
        db.commit()

        # Extract text
        extracted_text = extract_text(filepath)

        # Summarize
        summary = summarize_text(extracted_text)

        # Classify
        doc_type = classify_document(extracted_text, doc.filename)

        # Word count
        word_count = len(extracted_text.split())

        # Processing time
        processing_time = round(time.time() - start_time, 2)

        # Update document
        doc.extracted_text = extracted_text[:5000]  # store first 5000 chars
        doc.summary = summary
        doc.status = 'completed'
        doc.processed_at = datetime.utcnow()
        doc.word_count = word_count
        doc.processing_time = processing_time
        db.commit()

        print(f"✅ Processed: {doc.filename} | Type: {doc_type} | Words: {word_count} | Time: {processing_time}s")

        return {
            "status": "completed",
            "filename": doc.filename,
            "doc_type": doc_type,
            "word_count": word_count,
            "summary": summary,
            "processing_time": processing_time
        }

    except Exception as e:
        doc.status = 'failed'
        db.commit()
        print(f"❌ Failed: {doc.filename} | Error: {str(e)}")
        return {"status": "failed", "error": str(e)}

    finally:
        db.close()
