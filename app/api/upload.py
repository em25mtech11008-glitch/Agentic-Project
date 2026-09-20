import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.auth.middleware import get_current_user

# Import our custom RAG builders
from app.rag.loader import load_pdf
from app.rag.splitter import split_documents
from app.rag.vectorstore import add_documents_to_store

router = APIRouter(prefix="/api/upload", tags=["Upload"])

@router.post("")
async def upload_endpoint(file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    """
    Ingest & Upload PDF for RAG.
    """
    try:
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are supported.")
            
        os.makedirs("data", exist_ok=True)
        file_path = os.path.join("data", file.filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        raw_docs = load_pdf(file_path)
        split_docs = split_documents(raw_docs)
        add_documents_to_store(split_docs)
        
        return {
            "status": "success",
            "filename": file.filename,
            "chunks": len(split_docs)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
