from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import logging
import traceback
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from agents.pipeline import process_message
except ImportError:
    print("WARNING: Hybrid pipeline modules not found. Ensure PYTHONPATH is set correctly.")
    process_message = None

# Import routers - try relative imports first, fall back to absolute
try:
    from .auth_routes import router as auth_router
    from .session_routes import router as session_router
except ImportError:
    from backend.auth_routes import router as auth_router
    from backend.session_routes import router as session_router

# Logging Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Mental Health KRR System", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Broaden for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with /api prefix
app.include_router(auth_router, prefix="/api")
app.include_router(session_router, prefix="/api")


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


@app.post("/api/krr/run", response_model=KrrResponse, responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def run_reasoning_pipeline(request: KrrRequest):

    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text input cannot be empty.")
    
    if process_message is None:
         raise HTTPException(status_code=500, detail="Hybrid pipeline modules not initialized.")

    try:
        logger.info(f"Starting Hybrid Pipeline for session {request.session_id}")
        
        # This now uses the full agentic pipeline
        result = process_message(
            session_id=request.session_id,
            message=request.text
        )
        
        return result

    except Exception as e:
        logger.error(f"Pipeline Error: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Unable to process request at this time")

@app.get("/api/health")
async def health_check():
    return {"status": "active", "service": "Mental Health KRR System"}

# Serve Frontend Static Files
# Ensure the 'dist' folder exists (it is created by the build process)
static_path = Path(__file__).parent.parent / "frontend" / "dist"
if static_path.exists():
    app.mount("/assets", StaticFiles(directory=str(static_path / "assets")), name="assets")
    
    # Catch-all route for SPA (React Router)
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # API requests are already handled by routers above (prefix /api)
        # If it's a file request that exists, StaticFiles would handle it if we mounted root purely,
        # but for SPA we want everything else to go to index.html unless it's an API call.
        
        # Check if it matches a static file explicitly (like favicon, manifest)
        file_path = static_path / full_path
        if file_path.exists() and file_path.is_file():
             return FileResponse(file_path)
             
        # Otherwise serve index.html
        return FileResponse(static_path / "index.html")
else:
    print(f"WARNING: Frontend static files not found at {static_path}. Run 'npm run build' in frontend/.")
    
    @app.get("/")
    async def root():
        return {"message": "Backend Active. Frontend not built.", "status": "active"}
