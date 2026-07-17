"""
Generates a downloadable PDF verification report — this is fully your own
code (nothing pretrained here), so it's a good part of your dissertation to
describe in detail.
"""
import io
from datetime import datetime
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

router = APIRouter()


class ReportRequest(BaseModel):
    evidence_name: str
    evidence_type: str  # "video" | "audio" | "text" | "image"
    verdict: str
    confidence_score: float
    analyst_name: str = "CourtGuard Automated System"
    notes: str = ""


@router.post("")
def generate_report(request: ReportRequest):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    y = height - 2 * cm
    c.setFont("Helvetica-Bold", 18)
    c.drawString(2 * cm, y, "CourtGuard Digital Evidence Verification Report")

    y -= 1.2 * cm
    c.setFont("Helvetica", 10)
    c.drawString(2 * cm, y, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    y -= 1 * cm
    c.line(2 * cm, y, width - 2 * cm, y)

    fields = [
        ("Evidence file", request.evidence_name),
        ("Evidence type", request.evidence_type),
        ("Verdict", request.verdict.upper()),
        ("Confidence score", f"{request.confidence_score}%"),
        ("Analyst / System", request.analyst_name),
    ]

    y -= 1 * cm
    c.setFont("Helvetica-Bold", 12)
    for label, value in fields:
        c.drawString(2 * cm, y, f"{label}:")
        c.setFont("Helvetica", 12)
        c.drawString(6 * cm, y, str(value))
        c.setFont("Helvetica-Bold", 12)
        y -= 0.8 * cm

    if request.notes:
        y -= 0.5 * cm
        c.setFont("Helvetica-Bold", 12)
        c.drawString(2 * cm, y, "Notes:")
        y -= 0.7 * cm
        c.setFont("Helvetica", 10)
        c.drawString(2 * cm, y, request.notes[:100])

    y -= 2 * cm
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(
        2 * cm, y,
        "This report was generated automatically by CourtGuard and should be "
        "reviewed by a qualified forensic analyst before use as legal evidence."
    )

    c.showPage()
    c.save()
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=courtguard_report_{request.evidence_name}.pdf"},
    )
