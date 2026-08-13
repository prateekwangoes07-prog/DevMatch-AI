import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.dependencies.auth import require_admin
from app.schemas.client import ClientCreate, ClientUpdate, ClientResponse
from app.repositories.client_repository import ClientRepository
from app.services.client_service import ClientService

router = APIRouter()

def get_client_service(db: AsyncSession = Depends(get_db)) -> ClientService:
    repo = ClientRepository(db)
    return ClientService(repo)

@router.post("", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(
    schema: ClientCreate,
    service: ClientService = Depends(get_client_service),
    current_user = Depends(require_admin)
):
    return await service.create_client(schema)

@router.get("", response_model=List[ClientResponse])
async def list_clients(
    service: ClientService = Depends(get_client_service),
    current_user = Depends(require_admin)
):
    return await service.list_clients()

@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: str,
    service: ClientService = Depends(get_client_service),
    current_user = Depends(require_admin)
):
    try:
        parsed_id = uuid.UUID(client_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    return await service.get_client(parsed_id)

@router.patch("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: str,
    schema: ClientUpdate,
    service: ClientService = Depends(get_client_service),
    current_user = Depends(require_admin)
):
    try:
        parsed_id = uuid.UUID(client_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    return await service.update_client(parsed_id, schema)

@router.delete("/{client_id}", response_model=ClientResponse)
async def delete_client(
    client_id: str,
    service: ClientService = Depends(get_client_service),
    current_user = Depends(require_admin)
):
    try:
        parsed_id = uuid.UUID(client_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    return await service.deactivate_client(parsed_id)
