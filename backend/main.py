from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import logging
import traceback

try:
    from agents.pipeline import process_message
except ImportError:
    print("WARNING: Hybrid pipeline modules not found. Ensure PYTHONPATH is set correctly.")
    process_message = None

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

@app.get("/")
async def root():
    return {"message": "Mental Health KRR Symbolic Reasoning Engine", "status": "active"}
