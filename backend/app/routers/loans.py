from fastapi import APIRouter, HTTPException
from app.schemas.combo import LegsPayload
from app.services.mortgage_service import MortgageService
router = APIRouter()
@router.get("/loans")
def list_loans():
    with MortgageService() as s: return {"items": s.list_loans()}
@router.get("/loans/{loan_id}")
def get_loan(loan_id: int):
    with MortgageService() as s:
        row = s.loan(loan_id)
        if not row: raise HTTPException(404)
        return row
@router.put("/loans/{loan_id}/legs")
def put_loan_legs(loan_id: int, body: LegsPayload):
    with MortgageService() as s:
        try:
            row = s.save_legs(loan_id, body.legs())
        except ValueError as e:
            raise HTTPException(422, str(e))
        if not row: raise HTTPException(404)
        return row
