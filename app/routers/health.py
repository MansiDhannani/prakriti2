import os
from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/health")
def health():
    return {
        "status":  "healthy",
        "time":    datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "groq_ai_enabled": bool(os.getenv("GROQ_API_KEY")),
    }
