from fastapi import APIRouter
from app.database import get_all_analyses

router = APIRouter()


@router.get("")
def list_history(limit: int = 100):
    return {"analyses": get_all_analyses(limit=limit)}