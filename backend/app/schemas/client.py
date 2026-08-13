import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from app.models.enums import DeveloperRole

class ClientBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    company: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    phone: str | None = Field(None, max_length=50)
    requirement: str | None = None
    required_role: DeveloperRole

class ClientCreate(ClientBase):
    pass

class ClientUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    company: str | None = Field(None, min_length=1, max_length=255)
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=50)
    requirement: str | None = None
    required_role: DeveloperRole | None = None
    status: str | None = Field(None, max_length=50)

class ClientResponse(ClientBase):
    id: uuid.UUID
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
