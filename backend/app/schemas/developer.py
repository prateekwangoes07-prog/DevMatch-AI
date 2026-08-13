import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from app.models.enums import DeveloperRole

class DeveloperBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    phone: str | None = Field(None, max_length=50)
    role: DeveloperRole

class DeveloperCreate(DeveloperBase):
    pass

class DeveloperUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=50)
    role: DeveloperRole | None = None

class DeveloperResponse(DeveloperBase):
    id: uuid.UUID
    is_active: bool
    active_project_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DeveloperAllocate(BaseModel):
    client_id: uuid.UUID
    project_name: str = Field(..., min_length=1, max_length=255)

class DeveloperAvailableResponse(DeveloperBase):
    id: uuid.UUID
    is_active: bool
    active_project_count: int
    available: bool = True

    class Config:
        from_attributes = True

