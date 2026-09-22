from fastapi import APIRouter
from app.routers import combo, dashboard, history, loans, schedule, settings
api = APIRouter(prefix="/api")
for r in (combo, dashboard, loans, schedule, history, settings): api.include_router(r.router)
