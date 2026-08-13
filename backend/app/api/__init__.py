from fastapi import APIRouter
from app.api.auth import router as auth_router
from app.api.developer import router as developer_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(developer_router, prefix="/developers", tags=["developers"])

