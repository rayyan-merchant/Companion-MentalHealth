from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import logging
import traceback

# KRR Imports
try:
    from reasoning.orchestrator import run_krr_pipeline
except ImportError:
    print("WARNING: KRR modules not found. Ensure PYTHONPATH is set correctly.")
    run_krr_pipeline = None

# Logging Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Mental Health KRR System", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Models (Strict Contract) ---

class KrrRequest(BaseModel):
    session_id: str
    student_id: str
    text: str

class KrrResponse(BaseModel):
    session_id: str
    summary: str
    explanations: List[str]
    ranked_concerns: List[str]
    escalation_guidance: str
    disclaimer: str
    audit_ref: str

class ErrorResponse(BaseModel):
    error: str

# --- Endpoints ---

@app.post("/api/krr/run", response_model=KrrResponse, responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def run_reasoning_pipeline(request: KrrRequest):
    """
    Execute the symbolic Knowledge-Rich Reasoning pipeline.
    Strictly symbolic. No ML. No numerics.
    """
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text input cannot be empty.")
    
    if run_krr_pipeline is None:
         raise HTTPException(status_code=500, detail="KRR backend modules not initialized.")

    try:
        logger.info(f"Starting KRR pipeline for session {request.session_id}")
        
        # Execute Pipeline (Synchronous function wrapped in async handler)
        result = run_krr_pipeline(
            session_id=request.session_id,
            student_uri_str=request.student_id,
            raw_text=request.text
        )
        
        # Validate Response Structure matches Contract
        response_data = KrrResponse(
            session_id=result["session_id"],
            summary=result["summary"],
            explanations=result["explanations"],
            ranked_concerns=result["ranked_concerns"],
            escalation_guidance=result["escalation_guidance"],
            disclaimer=result["disclaimer"],
            audit_ref=result["audit_ref"]
        )
        
        return response_data

    except Exception as e:
        logger.error(f"KRR Pipeline Error: {str(e)}")
        traceback.print_exc()
        # Security: Never expose stack trace to frontend
        raise HTTPException(status_code=500, detail="Unable to process request at this time")

@app.get("/")
async def root():
    return {"message": "Mental Health KRR Symbolic Reasoning Engine", "status": "active"}
