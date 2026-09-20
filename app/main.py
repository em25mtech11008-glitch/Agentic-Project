import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

# 1. Initialize environment variables
load_dotenv()

# 2. Register Routers
from app.auth.routes import router as auth_router
from app.api.dashboard import router as dashboard_router
from app.api.customers import router as customers_router
from app.api.finance import router as finance_router
from app.api.sales import router as sales_router
from app.api.support import router as support_router
from app.api.operations import router as ops_router
from app.api.hr import router as hr_router
from app.api.chats import router as chats_router
from app.api.approvals import router as approvals_router
from app.api.upload import router as upload_router

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

# 5. Include all API routers
app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(customers_router)
app.include_router(finance_router)
app.include_router(sales_router)
app.include_router(support_router)
app.include_router(ops_router)
app.include_router(hr_router)
app.include_router(chats_router)
app.include_router(approvals_router)
app.include_router(upload_router)

# 6. Serve Static UI Assets
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# 7. Serve HTML Front-end UI at the root "/"
@app.get("/", response_class=HTMLResponse)
async def get_index():
    index_path = os.path.join("app", "static", "index.html")
    if not os.path.exists(index_path):
        raise HTTPException(status_code=404, detail="Index HTML not found.")
    with open(index_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())
