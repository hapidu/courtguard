"""
Video deepfake detection.

Approach: pull a handful of evenly-spaced frames out of the video, run each
one through the SAME pretrained image model used in image.py, then average
the "fake" probability across frames. This is a standard, defensible
approach for an FYP-scale video deepfake detector.
"""
import tempfile
from fastapi import APIRouter, UploadFile, File

from app.routers.image import get_pipe, extract_frames

router = APIRouter()


@router.post("")
async def analyze_video(file: UploadFile = File(...)):
    contents = await file.read()

    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=True) as tmp:
        tmp.write(contents)
        tmp.flush()

        frames = extract_frames(tmp.name, num_frames=8)
        if not frames:
            return {"verdict": "error", "confidence_score": 0, "details": {"error": "Could not read any frames from video"}}

        pipe = get_pipe()
        fake_scores = []
        real_scores = []
        per_frame_results = []

        for frame in frames:
            results = pipe(frame)
            per_frame_results.append(results)
            for r in results:
                if "fake" in r["label"].lower() or "deepfake" in r["label"].lower():
                    fake_scores.append(r["score"])
                elif "real" in r["label"].lower():
                    real_scores.append(r["score"])

        avg_fake = sum(fake_scores) / len(fake_scores) if fake_scores else 0
        avg_real = sum(real_scores) / len(real_scores) if real_scores else 0

        is_fake = avg_fake > avg_real
        confidence = avg_fake if is_fake else avg_real

    return {
        "verdict": "fake" if is_fake else "real",
        "confidence_score": round(confidence * 100, 2),
        "details": {
            "frames_analyzed": len(frames),
            "average_fake_score": round(avg_fake * 100, 2),
            "average_real_score": round(avg_real * 100, 2),
            "per_frame_results": per_frame_results,
        },
    }