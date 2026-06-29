from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, PlainTextResponse

from backend.app.modules.ai_runtime.router import router as ai_runtime_router
from backend.app.modules.projects.router import router as projects_router
from backend.app.modules.prompt_skill.router import router as prompt_skill_router


app = FastAPI(title="Chtest API")
app.include_router(projects_router, prefix="/api")
app.include_router(ai_runtime_router, prefix="/api")
app.include_router(prompt_skill_router, prefix="/api")


@app.get("/health", response_class=PlainTextResponse)
@app.get("/api/health", response_class=PlainTextResponse)
def health() -> str:
    return "ok"


@app.exception_handler(HTTPException)
async def http_exception_handler(_request: Request, exc: HTTPException) -> JSONResponse:
    if isinstance(exc.detail, dict) and "error_code" in exc.detail:
        content: dict[str, Any] = exc.detail
    else:
        content = {
            "error_code": "HTTP_ERROR",
            "message": str(exc.detail),
            "details": {},
        }
    return JSONResponse(status_code=exc.status_code, content=content)


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(
    _request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "error_code": "VALIDATION_ERROR",
            "message": "Request validation failed.",
            "details": {"errors": exc.errors()},
        },
    )
