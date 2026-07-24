"""
Audio deepfake / synthetic voice detection.

Same idea as image.py: use a pretrained model rather than training your own
voice-cloning detector from scratch. Search:
https://huggingface.co/models?pipeline_tag=audio-classification&search=deepfake

Paste the model ID into MODEL_NAME below.
"""
import io
import tempfile
from fastapi import APIRouter, UploadFile, File
from app.database import save_analysis

router = APIRouter()

MODEL_NAME = "Gustking/wav2vec2-large-xlsr-deepfake-audio-classification"

_pipe = None


def get_pipe():
    global _pipe
    if _pipe is None:
        from transformers import pipeline
        _pipe = pipeline("audio-classification", model=MODEL_NAME)
    return _pipe


@router.post("")
async def analyze_audio(file: UploadFile = File(...)):
    contents = await file.read()

    # transformers' audio pipeline wants a file path or array, so we write
    # the upload to a temp file first.
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as tmp:
        tmp.write(contents)
        tmp.flush()

        pipe = get_pipe()
        results = pipe(tmp.name)

    top = max(results, key=lambda r: r["score"])
    is_fake = "fake" in top["label"].lower() or "spoof" in top["label"].lower()

    result = {
        "verdict": "fake" if is_fake else "real",
        "confidence_score": round(top["score"] * 100, 2),
        "details": {"raw_model_output": results},
    }
    save_analysis(
        evidence_name=file.filename,
        evidence_type="audio",
        verdict=result["verdict"],
        confidence_score=result["confidence_score"],
        details=str(result["details"]),
    )
    return result
