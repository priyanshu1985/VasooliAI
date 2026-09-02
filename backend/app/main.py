import os
import logging
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# Load backend environment variables
env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=env_path)

from app.api.routes import router as api_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("recovery_ai.api")

app = FastAPI(
    title="AI Revenue Recovery Agent API",
    description="Automated 3-stage revenue recovery pipeline: Stage 1 ML Diagnosis, Stage 2 Smart Retry Sequencer with RBI e-mandate compliance, Stage 3 Gemini LLM Promise Tracker with Yale-study escalation.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Global CORS configuration
origins_str = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173")
origins = [origin.strip() for origin in origins_str.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Graceful global exception handler preventing unhandled 500 stack trace leakage."""
    logger.error(f"Unhandled error processing {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred processing the request. Please check server logs.",
            "path": request.url.path
        }
    )


# Register API routes
app.include_router(api_router)

from app.api.stage4_voice import router as stage4_router
app.include_router(stage4_router)


@app.get("/health", tags=["system"])
def health_check():
    """Health check endpoint to verify backend server status and connectivity."""
    return {
        "status": "healthy",
        "service": "AI Revenue Recovery API",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run("app.main:app", host=host, port=port, reload=True)
