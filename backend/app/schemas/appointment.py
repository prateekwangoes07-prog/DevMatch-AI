import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class AppointmentBase(BaseModel):
    client_id: uuid.UUID
    appointment_time: datetime

class AppointmentCreate(AppointmentBase):
    external_booking_id: str | None = None

class AppointmentResponse(AppointmentBase):
    id: uuid.UUID
    status: str
    external_booking_id: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CalcomSlot(BaseModel):
    time: str  # ISO string or formatted datetime representation from Cal.com

class CalcomAvailabilityResponse(BaseModel):
    slots: list[CalcomSlot] = []

class CalcomBookingCreate(BaseModel):
    client_id: uuid.UUID
    appointment_time: datetime
