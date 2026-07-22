"""
Combined / overall risk scoring across all evidence modules.

This directly implements your objective: "To generate confidence-based
results for evidence verification" at a system level, not just per-module.

Weighting rationale (cite this in your methodology chapter): your own
survey found video was rated the highest-risk evidence type (46.3%),
followed by images (29.3%), text (14.6%), then audio (9.8%). We use that
to weight the combined score, adjusted so weights sum to 1.0.
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class ModuleScore(BaseModel):
    verdict: str  # "real"/"fake" or "legitimate"/"suspicious"
    confidence_score: float  # 0-100


class CombinedRequest(BaseModel):
    video: Optional[ModuleScore] = None
    image: Optional[ModuleScore] = None
    audio: Optional[ModuleScore] = None
    


# Weights derived from your survey's "most vulnerable evidence type" results
WEIGHTS = {
    "video": 0.54,
    "image": 0.34,
    "audio": 0.12,
}


def _risk_contribution(module: Optional[ModuleScore], weight: float) -> float:
    """
    Converts a module's verdict+confidence into a 0-100 'risk' contribution.
    A 'fake'/'suspicious' verdict contributes its confidence directly as risk.
    A 'real'/'legitimate' verdict contributes (100 - confidence) as risk,
    i.e. low confidence in "real" still counts as some risk.
    """
    if module is None:
        return 0.0

    flagged = module.verdict.lower() in ("fake", "suspicious")
    risk = module.confidence_score if flagged else (100 - module.confidence_score)
    return risk * weight


@router.post("")
def combined_risk(request: CombinedRequest):
    present_weights = {
        name: w for name, w in WEIGHTS.items()
        if getattr(request, name) is not None
    }
    total_weight = sum(present_weights.values())
    if total_weight == 0:
        return {"overall_risk_score": 0, "risk_level": "unknown", "details": "No module results provided"}

    # Renormalize weights so they sum to 1 even if some modules are missing
    contributions = {}
    weighted_sum = 0.0
    for name, weight in present_weights.items():
        normalized_weight = weight / total_weight
        contribution = _risk_contribution(getattr(request, name), normalized_weight)
        contributions[name] = round(contribution, 2)
        weighted_sum += contribution

    if weighted_sum >= 70:
        level = "high risk"
    elif weighted_sum >= 40:
        level = "moderate risk"
    else:
        level = "low risk"

    return {
        "overall_risk_score": round(weighted_sum, 2),
        "risk_level": level,
        "details": {
            "module_contributions": contributions,
            "weights_used": {k: round(v / total_weight, 2) for k, v in present_weights.items()},
        },
    }