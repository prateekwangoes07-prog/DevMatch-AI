from fastapi import APIRouter
from app.api.auth import router as auth_router
from app.api.developer import router as developer_router
from app.api.client import router as client_router
from app.api.customer_request import router as customer_request_router
from app.api.appointment import router as appointment_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(developer_router, prefix="/developers", tags=["developers"])
api_router.include_router(client_router, prefix="/clients", tags=["clients"])
api_router.include_router(customer_request_router, prefix="/customer-requests", tags=["customer-requests"])
api_router.include_router(appointment_router, prefix="/appointments", tags=["appointments"])


