import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

# Import our custom RAG builders
from app.rag.loader import load_pdf
from app.rag.splitter import split_documents
from app.rag.vectorstore import add_documents_to_store

# Auth dependencies
from app.auth.middleware import get_current_user

# Custom MongoDB checkpointer
from app.graph.checkpointer import AsyncMongoDBSaver
from motor.motor_asyncio import AsyncIOMotorClient
from app.graph.workflow import create_workflow

# 1. Initialize environment variables
load_dotenv()

# 2. Compile our LangGraph state machine with MongoDBSaver
mongo_client = AsyncIOMotorClient(os.getenv("MONGODB_URI"))
mongodb_saver = AsyncMongoDBSaver(mongo_client)
# IMPORTANT: This compiles the global graph that all routes should import and use
graph_app = create_workflow(checkpointer=mongodb_saver)

# 3. Initialize FastAPI
app = FastAPI(title="🏢 AI Operations Command Center")

# 4. CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5. Register All Routers
from app.auth.routes import router as auth_router
from app.api.dashboard import router as dashboard_router
from app.api.customers import router as customers_router
from app.api.finance import router as finance_router
from app.api.sales import router as sales_router
from app.api.support import router as support_router
from app.api.operations import router as ops_router
from app.api.hr import router as hr_router
from app.api.ai_command import router as ai_router
from app.api.chats import router as chats_router
from app.api.approvals import router as approvals_router

app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(customers_router)
app.include_router(finance_router)
app.include_router(sales_router)
app.include_router(support_router)
app.include_router(ops_router)
app.include_router(hr_router)
app.include_router(ai_router)
app.include_router(chats_router)
app.include_router(approvals_router)

# 6. Serve Static UI Assets
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# 7. Serving HTML Front-end UI at the root "/"
@app.get("/", response_class=HTMLResponse)
async def get_index():
    index_path = os.path.join("app", "static", "index.html")
    if not os.path.exists(index_path):
        raise HTTPException(status_code=404, detail="Index HTML not found.")
    with open(index_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

# 8. API Endpoint: Ingest & Upload PDF for RAG
@app.post("/api/upload")
async def upload_endpoint(file: UploadFile = File(...), user: dict = Depends(get_current_user)):
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
