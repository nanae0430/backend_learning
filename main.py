from fastapi import FastAPI, HTTPException, Response, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import get_db
from models import Document
from schemas import (
    DocumentResponse,
    AskResponse,
    AskRequest,
    DocumentCreate,
    DocumentUpdate,
)
from redis_demo import r, cached_search
import asyncio, time, json

app = FastAPI()

documents = {
    123: {"title": "Transformer"},
    456: {"title": "RAG"},
}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/search")
def search(query: str, top_k: int = 5):
    return cached_search(query, top_k)


@app.get("/documents/{doc_id}", response_model=DocumentResponse)
def get_document(doc_id: int, db: Session = Depends(get_db)):
    document = db.get(Document, doc_id)

    if document is not None:
        return document
    else:
        raise HTTPException(404, detail="Document not found")


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    return {
        "question": request.question,
        "top_k": request.top_k,
        "rerank": request.rerank,
        "answer": "This is a test answer.",
    }


@app.delete("/documents/{doc_id}", status_code=204, response_class=Response)
def delete_document(doc_id: int, db: Session = Depends(get_db)):

    document = db.get(Document, doc_id)

    if document is None:
        raise HTTPException(404, detail="Document not found")

    db.delete(document)
    db.commit()

    return Response(status_code=204)


@app.post("/documents", response_model=DocumentResponse, status_code=201)
def add_document(request: DocumentCreate, db: Session = Depends(get_db)):

    document = Document(**request.model_dump())
    db.add(document)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Database constraint violation")
    db.refresh(document)
    return document


@app.patch("/documents/{doc_id}", response_model=DocumentResponse)
def update_document(
    doc_id: int, request: DocumentUpdate, db: Session = Depends(get_db)
):
    document = db.get(Document, doc_id)

    if document is None:
        raise HTTPException(404, detail="Document not found")

    document.title = request.title
    db.commit()
    db.refresh(document)
    return document


@app.get("/delay")
async def delay():
    await asyncio.sleep(2)
    return {"message": "done"}


def process_document(doc_id: int):

    r.set(f"task:{doc_id}:status", "RUNNING", ex=3600)
    print(f"doc[{doc_id}] starts processing")
    time.sleep(3)
    print(f"doc[{doc_id}] ends processing")
    r.set(f"task:{doc_id}:status", "SUCCESS", ex=3600)


task_status = {}


@app.post("/documents/process", status_code=202)
def start_processing(doc_id: int, background_tasks: BackgroundTasks):

    background_tasks.add_task(process_document, doc_id)
    r.set(f"task:{doc_id}:status", "PENDING", ex=3600)
    return {"message": "Task accepted", "doc_id": doc_id}


@app.get("/tasks/{doc_id}")
def get_task_status(doc_id: int):
    status = r.get(f"task:{doc_id}:status")
    if status:
        raise HTTPException(404, detail="Document not found")
    return {"doc_id": doc_id, "status": status}
