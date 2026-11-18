"""FastAPI app: the backend of Voice to Report.

Run it from the backend folder:
    uvicorn app.main:app --reload
"""

import os

from fastapi import FastAPI

# In development the React app (Vite) forwards /api/... calls here, so no CORS setup is needed.
app = FastAPI(title="Voice to Report")


@app.get("/api/health")
def health() -> dict:
    """Is the backend running, and which LLM provider is active?"""
    return {"status": "ok", "llm_provider": os.getenv("LLM_PROVIDER", "claude")}
