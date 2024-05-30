from fastapi import APIRouter
from UL_Windcube.routes import router as ul

api_router = APIRouter()
api_router.include_router(ul, tags=["Windcube"], prefix="/graphs")

