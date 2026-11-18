"""FastAPI app: the backend of Voice to Report.

Run it from the backend folder:
    uvicorn app.main:app --reload
"""

import os
from datetime import date

from fastapi import Depends, FastAPI, HTTPException

from app.llm import LLMError, LLMProvider, get_provider
from app.models import GenerateRequest, Report
from app.report_service import ReportError, generate_report

# In development the React app (Vite) forwards /api/... calls here, so no CORS setup is needed.
app = FastAPI(title="Voice to Report")


@app.get("/api/health")
def health() -> dict:
    """Is the backend running, and which LLM provider is active?"""
    return {"status": "ok", "llm_provider": os.getenv("LLM_PROVIDER", "claude")}


@app.post("/api/reports/generate")
def generate(request: GenerateRequest, provider: LLMProvider = Depends(get_provider)) -> Report:
    """Turn a transcript into a structured report (not saved yet)."""
    try:
        return generate_report(request.transcript, request.language, provider, date.today())
    except (LLMError, ReportError) as error:
        raise HTTPException(status_code=502, detail=str(error)) from error
