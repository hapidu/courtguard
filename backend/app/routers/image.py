"""
Image/video deepfake detection.

We use a PRETRAINED model from Hugging Face instead of training our own,
because deepfake-detection CNNs need huge labelled datasets (e.g. FaceForensics++,
referenced in your literature review) and days of GPU training — not realistic
for a laptop FYP. Using a pretrained model and building the surrounding
verification system (scoring, reporting, multi-modal pipeline) around it is a
legitimate and common approach for this kind of project — just be explicit
about this in your dissertation methodology chapter.

HOW TO PICK A MODEL:
1. Go to https://huggingface.co/models?pipeline_tag=image-classification&search=deepfake
2. Pick a model card (read it - check it's for face/deepfake classification)
3. Copy its model ID (looks like "username/model-name")
4. Paste it into MODEL_NAME below

The first time you run this, transformers will download the model weights
automatically (needs internet, only happens once, then it's cached).

For VIDEO: for now, this endpoint accepts an image. To handle video, the
simplest approach (good enough for an FYP) is to extract a handful of frames
from the video with OpenCV and run each frame through this same model, then
average the fake-probability across frames. See extract_frames() below.
"""
import io
from fastapi import APIRouter, UploadFile, File
from PIL import Image
from app.database import save_analysis

router = APIRouter()

MODEL_NAME = "Wvolf/ViT_Deepfake_Detection"

_pipe = None


def get_pipe():
    global _pipe
    if _pipe is None:
        from transformers import pipeline
        _pipe = pipeline("image-classification", model=MODEL_NAME)
    return _pipe


@router.post("")
async def analyze_image(file: UploadFile = File(...)):
    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGB")

    pipe = get_pipe()
    results = pipe(image)  # e.g. [{"label": "fake", "score": 0.87}, {"label": "real", "score": 0.13}]

    top = max(results, key=lambda r: r["score"])
    is_fake = "fake" in top["label"].lower() or "deepfake" in top["label"].lower()

    result = {
        "verdict": "fake" if is_fake else "real",
        "confidence_score": round(top["score"] * 100, 2),
        "details": {"raw_model_output": results},
    }
    save_analysis(
        evidence_name=file.filename,
        evidence_type="image",
        verdict=result["verdict"],
        confidence_score=result["confidence_score"],
        details=str(result["details"]),
    )
    return result

def extract_frames(video_path: str, num_frames: int = 8):
    """
    Pulls evenly-spaced frames out of a video for analysis.
    Requires: pip install opencv-python
    Call this from a /analyze/video endpoint you add later, then run each
    returned PIL image through get_pipe() and average the fake scores.
    """
    import cv2

    cap = cv2.VideoCapture(video_path)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    step = max(total // num_frames, 1)

    frames = []
    for i in range(0, total, step):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ok, frame = cap.read()
        if ok:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append(Image.fromarray(rgb))
        if len(frames) >= num_frames:
            break

    cap.release()
    return frames
