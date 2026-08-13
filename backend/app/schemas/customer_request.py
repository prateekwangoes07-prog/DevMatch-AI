import uuid
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.enums import DeveloperRole, ApprovalStatus

class CustomerRequestBase(BaseModel):
    client_id: uuid.UUID
    required_role: DeveloperRole
    recommended_developer_id: uuid.UUID | None = None

class CustomerRequestCreate(CustomerRequestBase):
    pass

class CustomerRequestUpdate(BaseModel):
    client_id: uuid.UUID | None = None
    required_role: DeveloperRole | None = None
    recommended_developer_id: uuid.UUID | None = None

class CustomerRequestApproval(BaseModel):
    approval_status: ApprovalStatus

class CustomerRequestResponse(BaseModel):
    id: uuid.UUID
    client_id: uuid.UUID
    required_role: DeveloperRole
    recommended_developer_id: uuid.UUID | None
    appointment_id: uuid.UUID | None
    approval_status: ApprovalStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
