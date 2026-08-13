import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.dependencies.auth import require_admin
from app.schemas.customer_request import (
    CustomerRequestCreate,
    CustomerRequestApproval,
    CustomerRequestResponse
)
from app.repositories.customer_request_repository import CustomerRequestRepository
from app.repositories.client_repository import ClientRepository
from app.repositories.developer_repository import DeveloperRepository
from app.services.customer_request_service import CustomerRequestService

router = APIRouter()

def get_customer_request_service(db: AsyncSession = Depends(get_db)) -> CustomerRequestService:
    repo = CustomerRequestRepository(db)
    client_repo = ClientRepository(db)
    dev_repo = DeveloperRepository(db)
    return CustomerRequestService(repo, client_repo, dev_repo)

@router.post("", response_model=CustomerRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_request(
    schema: CustomerRequestCreate,
    service: CustomerRequestService = Depends(get_customer_request_service),
    current_user = Depends(require_admin)
):
    return await service.create_request(schema)

@router.get("", response_model=List[CustomerRequestResponse])
async def list_requests(
    service: CustomerRequestService = Depends(get_customer_request_service),
    current_user = Depends(require_admin)
):
    return await service.list_requests()

@router.get("/{request_id}", response_model=CustomerRequestResponse)
async def get_request(
    request_id: str,
    service: CustomerRequestService = Depends(get_customer_request_service),
    current_user = Depends(require_admin)
):
    try:
        parsed_id = uuid.UUID(request_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer request not found"
        )
    return await service.get_request(parsed_id)

@router.patch("/{request_id}/approval", response_model=CustomerRequestResponse)
async def update_approval(
    request_id: str,
    schema: CustomerRequestApproval,
    service: CustomerRequestService = Depends(get_customer_request_service),
    current_user = Depends(require_admin)
):
    try:
        parsed_id = uuid.UUID(request_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer request not found"
        )
    return await service.update_approval(parsed_id, schema)
