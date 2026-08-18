import uuid
from datetime import datetime, timedelta, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies.auth import require_admin
from app.schemas.appointment import AppointmentCreate, AppointmentResponse
from app.repositories.appointment_repository import AppointmentRepository
from app.repositories.client_repository import ClientRepository
from app.services.calcom_service import CalcomService
from app.services.appointment_service import AppointmentService

router = APIRouter()

def get_appointment_service(db: AsyncSession = Depends(get_db)) -> AppointmentService:
    appointment_repo = AppointmentRepository(db)
    client_repo = ClientRepository(db)
    calcom_service = CalcomService()
    return AppointmentService(appointment_repo, client_repo, calcom_service)

@router.get("", response_model=List[AppointmentResponse])
async def list_appointments(
    service: AppointmentService = Depends(get_appointment_service),
    current_user = Depends(require_admin)
):
    """
    List all appointments (Admin only)
    """
    return await service.list_appointments()

@router.get("/availability", response_model=List[str])
async def get_availability(
    start_date: datetime | None = Query(None),
    end_date: datetime | None = Query(None),
    service: AppointmentService = Depends(get_appointment_service),
    current_user = Depends(require_admin)
):
    """
    Get available slots from Cal.com (Admin only)
    """
    if not start_date:
        start_date = datetime.now(timezone.utc)
    if not end_date:
        end_date = start_date + timedelta(days=7)
    
    return await service.get_availability(start_date, end_date)

@router.post("/book", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def book_appointment(
    schema: AppointmentCreate,
    service: AppointmentService = Depends(get_appointment_service),
    current_user = Depends(require_admin)
):
    """
    Book a new appointment (Admin only)
    """
    return await service.create_appointment(schema)

@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: str,
    service: AppointmentService = Depends(get_appointment_service),
    current_user = Depends(require_admin)
):
    """
    Get details of a specific appointment (Admin only)
    """
    try:
        parsed_id = uuid.UUID(appointment_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    return await service.get_appointment(parsed_id)

@router.post("/{appointment_id}/cancel", response_model=AppointmentResponse)
async def cancel_appointment(
    appointment_id: str,
    service: AppointmentService = Depends(get_appointment_service),
    current_user = Depends(require_admin)
):
    """
    Cancel an appointment (Admin only)
    """
    try:
        parsed_id = uuid.UUID(appointment_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    return await service.cancel_appointment(parsed_id)
