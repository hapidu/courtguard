"""
CourtGuard backend entry point.

Run locally with:
    uvicorn app.main:app --reload --port 8000
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import text, image, audio, report

app = FastAPI(
    title="CourtGuard API",
    description="AI-based digital evidence verification system",
    version="0.1.0",
)

# Allow the frontend (running on a different port/file) to call this API.
# For your dissertation, you can tighten this later to your real frontend domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(text.router, prefix="/analyze/text", tags=["Text Analysis"])
app.include_router(image.router, prefix="/analyze/image", tags=["Image/Video Analysis"])
app.include_router(audio.router, prefix="/analyze/audio", tags=["Audio Analysis"])
app.include_router(report.router, prefix="/report", tags=["PDF Report"])


@app.get("/")
def health_check():
    return {"status": "ok", "message": "CourtGuard API is running"}
