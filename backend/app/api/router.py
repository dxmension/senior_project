from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.transcript import router as transcript_router
from app.api.v1.user import router as user_router

api_router = APIRouter(prefix="/v1")


api_router.include_router(auth_router)
api_router.include_router(transcript_router)
api_router.include_router(user_router)
