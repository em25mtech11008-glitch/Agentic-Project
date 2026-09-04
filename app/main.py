import os
import shutil
import uuid
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv

# LangChain message modules
from langchain_core.messages import HumanMessage

# LangGraph Memory Saver checkpointing
from langgraph.checkpoint.memory import MemorySaver

# Import our custom RAG and Graph Workflow builders
from app.graph.workflow import create_workflow
from app.rag.loader import load_pdf
from app.rag.splitter import split_documents
from app.rag.vectorstore import add_documents_to_store

# 1. Initialize environment variables
load_dotenv()

# 2. Compile our LangGraph state machine with MemorySaver
# MemorySaver stores conversation threads in RAM, giving us automatic checkpointer state history.
memory_saver = MemorySaver()
graph_app = create_workflow(checkpointer=memory_saver)

# 3. Initialize FastAPI
app = FastAPI(title="🏢 AI Operations Command Center")

# 3b. CORS Middleware — allows the React frontend (port 5173) to call the FastAPI backend (port 8000)
# Educational Comment:
# Without CORS, the browser blocks requests from localhost:5173 to localhost:8000
# because they are different "origins". This middleware explicitly allows it.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3c. Register Auth Routes
from app.auth.routes import router as auth_router
app.include_router(auth_router)

# 3d. Register Business APIs
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

# 4. Session Manager
# We maintain a dynamic thread ID that we can reset to "clear" history.
class SessionManager:
    def __init__(self):
        self.thread_id = str(uuid.uuid4())
    
    def reset(self):
        self.thread_id = str(uuid.uuid4())

session = SessionManager()

# 5. Serve Static UI Assets
# Mount the static directory so the page can fetch style.css and index.html
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# 6. Serving HTML Front-end UI at the root "/"
@app.get("/", response_class=HTMLResponse)
async def get_index():
    index_path = os.path.join("app", "static", "index.html")
    if not os.path.exists(index_path):
        raise HTTPException(status_code=404, detail="Index HTML not found.")
    with open(index_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

# 7. Request schema for chat
class ChatRequest(BaseModel):
    query: str
    thread_id: str = None

# 8. API Endpoint: Send Chat Message
@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    try:
        query_text = req.query.strip()
        if not query_text:
            raise HTTPException(status_code=400, detail="Query cannot be empty.")

        # Configuration dictionary containing the current session's thread ID
        # Default to a generic session if not provided by the client
        current_thread_id = req.thread_id if req.thread_id else session.thread_id
        config = {"configurable": {"thread_id": current_thread_id}}
        
        # Accumulate execution trace steps for UI dashboard feedback
        steps = []
        
        # Run the workflow asynchronously and stream updates at node transitions
        # input_state adds the new user message to the thread history
        input_state = {"messages": [HumanMessage(content=query_text)]}
        
        async for event in graph_app.astream(input_state, config=config, stream_mode="updates"):
            for node_name, node_update in event.items():
                if node_name == "retrieve":
                    # The RAG retriever node was executed
                    doc_count = len(node_update.get("context", []))
                    steps.append(f"RAG: Retrieved {doc_count} document chunks from Chroma DB.")
                elif node_name == "tools":
                    # The tools executor node was executed
                    steps.append("Tools: Executed calculations or weather checks.")
                elif node_name == "agent":
                    # The LLM model was invoked
                    steps.append("LLM: Agent generated response reasoning step.")

        # Retrieve the final consolidated state from the checkpointer
        final_state = graph_app.get_state(config)
        final_messages = final_state.values.get("messages", [])
        
        if not final_messages:
            raise HTTPException(status_code=500, detail="No response generated by the agent.")
            
        # The last message in the state represents the final AIMessage output
        raw_content = final_messages[-1].content
        if isinstance(raw_content, list):
            # Extract text from the list of message parts (common with Google GenAI models)
            final_response = "".join([part.get("text", "") for part in raw_content if isinstance(part, dict) and "text" in part])
        else:
            final_response = str(raw_content)
        
        return {
            "status": "success",
            "response": final_response,
            "steps": steps
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

# 9. API Endpoint: Ingest & Upload PDF for RAG
@app.post("/api/upload")
async def upload_endpoint(file: UploadFile = File(...)):
    try:
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are supported.")
            
        os.makedirs("data", exist_ok=True)
        file_path = os.path.join("data", file.filename)
        
        # Save the uploaded file locally
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # 1. Parse and extract text from the PDF using PyPDFLoader
        raw_docs = load_pdf(file_path)
        
        # 2. Chunk text using RecursiveCharacterTextSplitter
        split_docs = split_documents(raw_docs)
        
        # 3. Embed text chunks and save to Chroma Vector DB
        add_documents_to_store(split_docs)
        
        return {
            "status": "success",
            "filename": file.filename,
            "chunks": len(split_docs)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

class ClearRequest(BaseModel):
    thread_id: str = None

# 10. API Endpoint: Reset Chat Thread (Clear History)
@app.post("/api/clear")
async def clear_endpoint(req: ClearRequest = None):
    # If using global session, we would reset it here
    # However, since we're using client-side thread IDs now, history is effectively cleared 
    # simply by the client generating a new one next time they refresh. 
    # For now, we can still reset the global session as a fallback.
    session.reset()
    return {"status": "success", "message": "Conversation history cleared."}
