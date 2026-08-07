import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from routers.ai_modules import router as ai_router

app = FastAPI(
    title="EDUMITHRA AI Engine",
    description="Backend API powering educational services via Groq Llama 3.3",
    version="1.0.0"
)

# Allow all origins for local Swagger UI testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ai_router)

@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "service": "EDUMITHRA Backend Engine",
        "groq_configured": bool(os.getenv("GROQ_API_KEY"))
    }