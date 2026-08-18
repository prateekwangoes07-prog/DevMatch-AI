import uuid
from datetime import datetime
from typing import Sequence
from fastapi import HTTPException, status
from app.repositories.appointment_repository import AppointmentRepository
from app.repositories.client_repository import ClientRepository
from app.services.calcom_service import CalcomService
from app.models.appointment import Appointment
from app.schemas.appointment import AppointmentCreate

class AppointmentService:
    def __init__(
        self,
        appointment_repo: AppointmentRepository,
        client_repo: ClientRepository,
        calcom_service: CalcomService
    ):
        self.appointment_repo = appointment_repo
        self.client_repo = client_repo
        self.calcom_service = calcom_service

    async def get_availability(self, start_date: datetime, end_date: datetime) -> Sequence[str]:
        """
        Get slot availability from Cal.com
        """
        return await self.calcom_service.get_availability(start_date, end_date)

    async def list_appointments(self) -> Sequence[Appointment]:
        """
        List all appointments
        """
        return await self.appointment_repo.list_all()

    async def get_appointment(self, appointment_id: uuid.UUID) -> Appointment:
        """
        Get details of an appointment
        """
        appointment = await self.appointment_repo.get_by_id(appointment_id)
        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appointment not found"
            )
        return appointment

    async def create_appointment(self, schema: AppointmentCreate) -> Appointment:
        """
        Create a new appointment:
        1. Validate client exists and is active.
        2. Prevent duplicate bookings using external_booking_id if provided.
        3. Call Cal.com API to create the booking.
        4. Save the appointment to the database.
        """
        # Validate client
        client = await self.client_repo.get_by_id(schema.client_id)
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found"
            )

        if client.status != "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive clients cannot book new appointments"
            )

        # Check if external_booking_id was provided and already exists
        if schema.external_booking_id:
            existing = await self.appointment_repo.get_by_external_id(schema.external_booking_id)
            if existing:
                return existing

        # Create booking on Cal.com
        try:
            booking = await self.calcom_service.create_booking(
                client_name=client.name,
                client_email=client.email,
                appointment_time=schema.appointment_time
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to create booking on Cal.com: {str(e)}"
            )

        external_id = str(booking.get("id"))

        # Idempotence check with the newly created external booking ID
        existing = await self.appointment_repo.get_by_external_id(external_id)
        if existing:
            return existing

        # Create local appointment
        appointment = Appointment(
            client_id=client.id,
            appointment_time=schema.appointment_time,
            status="scheduled",
            external_booking_id=external_id
        )

        return await self.appointment_repo.create(appointment)

    async def cancel_appointment(self, appointment_id: uuid.UUID) -> Appointment:
        """
        Cancel an appointment locally.
        """
        appointment = await self.appointment_repo.get_by_id(appointment_id)
        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appointment not found"
            )
        
        appointment.status = "cancelled"
        return await self.appointment_repo.update(appointment)
