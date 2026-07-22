"""
CourtGuard backend entry point.

Run locally with:
    uvicorn app.main:app --reload --port 8000
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db

from app.routers import image, audio, video, report, combined, history
from app.security import verify_api_key


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

@app.on_event("startup")
def startup_event():
    init_db()

app.include_router(image.router, prefix="/analyze/image", tags=["Image/Video Analysis"], dependencies=[Depends(verify_api_key)])
app.include_router(video.router, prefix="/analyze/video", tags=["Video Analysis"], dependencies=[Depends(verify_api_key)])
app.include_router(audio.router, prefix="/analyze/audio", tags=["Audio Analysis"], dependencies=[Depends(verify_api_key)])
app.include_router(combined.router, prefix="/analyze/combined", tags=["Combined Risk Score"], dependencies=[Depends(verify_api_key)])
app.include_router(history.router, prefix="/history", tags=["History / Audit Trail"], dependencies=[Depends(verify_api_key)])
app.include_router(report.router, prefix="/report", tags=["PDF Report"])


@app.get("/")
def health_check():
    return {"status": "ok", "message": "CourtGuard API is running"}

