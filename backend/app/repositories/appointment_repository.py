import uuid
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.appointment import Appointment

class AppointmentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, appointment_id: uuid.UUID) -> Appointment | None:
        result = await self.db.execute(
            select(Appointment).filter(Appointment.id == appointment_id)
        )
        return result.scalar_one_or_none()

    async def get_by_external_id(self, external_booking_id: str) -> Appointment | None:
        result = await self.db.execute(
            select(Appointment).filter(Appointment.external_booking_id == external_booking_id)
        )
        return result.scalar_one_or_none()

    async def list_all(self) -> Sequence[Appointment]:
        result = await self.db.execute(
            select(Appointment).order_by(Appointment.appointment_time.desc())
        )
        return result.scalars().all()

    async def list_by_client(self, client_id: uuid.UUID) -> Sequence[Appointment]:
        result = await self.db.execute(
            select(Appointment)
            .filter(Appointment.client_id == client_id)
            .order_by(Appointment.appointment_time.desc())
        )
        return result.scalars().all()

    async def create(self, appointment: Appointment) -> Appointment:
        self.db.add(appointment)
        await self.db.commit()
        await self.db.refresh(appointment)
        return appointment

    async def update(self, appointment: Appointment) -> Appointment:
        await self.db.commit()
        await self.db.refresh(appointment)
        return appointment
