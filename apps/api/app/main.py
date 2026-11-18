"""Voice to Report API.

Run locally:
    uvicorn app.main:app --reload
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.errors import LLMError, RateLimitExceeded, ReportGenerationError


def create_app() -> FastAPI:
    app = FastAPI(title="Voice to Report API", version="1.0.0")
    app.include_router(api_router)

    @app.exception_handler(LLMError)
    @app.exception_handler(ReportGenerationError)
    async def upstream_error(_: Request, error: Exception) -> JSONResponse:
        return JSONResponse(status_code=status.HTTP_502_BAD_GATEWAY, content={"detail": str(error)})

    @app.exception_handler(RateLimitExceeded)
    async def rate_limited(_: Request, error: RateLimitExceeded) -> JSONResponse:
        return JSONResponse(status_code=status.HTTP_429_TOO_MANY_REQUESTS, content={"detail": str(error)})

    return app


app = create_app()
