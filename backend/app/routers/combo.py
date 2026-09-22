from fastapi import APIRouter
from app.schemas.combo import ComboScheduleRequest
from app.services.mortgage_service import MortgageService
router = APIRouter()
@router.post("/combo/schedule")
def post_combo_schedule(body: ComboScheduleRequest):
    with MortgageService() as s:
        return s.combo_schedule(body.legs(), body.loan_id, body.persist, body.preview_rows)
