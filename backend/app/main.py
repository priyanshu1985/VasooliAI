import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.api.routes import router as api_router

load_dotenv()

app = FastAPI(
    title="AI Revenue Recovery Agent API",
    description="Automated multi-stage revenue recovery pipeline with ML diagnosis, smart retry sequencing, and promise tracking.",
    version="1.0.0"
)

# CORS configuration
origins_str = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173")
origins = [origin.strip() for origin in origins_str.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes matching docs/design.md data contract
app.include_router(api_router)


@app.get("/health", tags=["system"])
def health_check():
    """Health check endpoint to verify the backend server status."""
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
