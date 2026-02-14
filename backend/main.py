from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import logging
import traceback
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# ==========================================
# Environment Setup
# ==========================================

load_dotenv()

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from agents.pipeline import process_message
except ImportError:
    print("WARNING: Hybrid pipeline modules not found.")
    process_message = None

# Import routers
try:
    from .auth_routes import router as auth_router
    from .session_routes import router as session_router
except ImportError:
    from backend.auth_routes import router as auth_router
    from backend.session_routes import router as session_router

# ==========================================
# Logging
# ==========================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==========================================
# FastAPI App
# ==========================================

app = FastAPI(title="Mental Health KRR System", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# Include API Routers
# ==========================================

app.include_router(auth_router, prefix="/api")
app.include_router(session_router, prefix="/api")

# ==========================================
# Models
# ==========================================

class KrrRequest(BaseModel):
    session_id: str
    student_id: str
    text: str


class EvidenceSummary(BaseModel):
    emotions: List[str]
    symptoms: List[str]
    triggers: List[str]
    intensity: str
    temporal: Optional[str] = None


class KrrResponse(BaseModel):
    session_id: str
    response: str
    state: Optional[str]
    confidence: str
    action: str
    evidence: EvidenceSummary
    follow_up_questions: List[str] = []
    disclaimer: str


class ErrorResponse(BaseModel):
    error: str

# ==========================================
# API Endpoints
# ==========================================

@app.post(
    "/api/krr/run",
    response_model=KrrResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def run_reasoning_pipeline(request: KrrRequest):

    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text input cannot be empty.")

    if process_message is None:
        raise HTTPException(status_code=500, detail="Pipeline not initialized.")

    try:
        logger.info(f"Running pipeline for session {request.session_id}")

        result = process_message(
            session_id=request.session_id,
            message=request.text
        )

        return result

    except Exception as e:
        logger.error(str(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Processing failed")


@app.get("/api/health")
async def health_check():
    return {"status": "active"}

# ==========================================
# Frontend (React) Production Serving
# ==========================================

# Path inside Docker: /app/frontend/dist
FRONTEND_DIR = os.path.join(os.getcwd(), "frontend", "dist")

# Serve static assets (JS, CSS, images)
app.mount(
    "/assets",
    StaticFiles(directory=os.path.join(FRONTEND_DIR, "assets")),
    name="assets",
)

# Catch-all route for React (must be LAST)
@app.get("/{full_path:path}")
async def serve_react(full_path: str):
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    return FileResponse(index_path)
