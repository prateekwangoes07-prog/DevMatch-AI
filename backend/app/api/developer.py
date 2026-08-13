import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.dependencies.auth import require_admin
from app.schemas.developer import DeveloperCreate, DeveloperUpdate, DeveloperResponse
from app.repositories.developer_repository import DeveloperRepository
from app.services.developer_service import DeveloperService

router = APIRouter()

def get_developer_service(db: AsyncSession = Depends(get_db)) -> DeveloperService:
    repo = DeveloperRepository(db)
    return DeveloperService(repo)

@router.post("", response_model=DeveloperResponse, status_code=status.HTTP_201_CREATED)
async def create_developer(
    schema: DeveloperCreate,
    service: DeveloperService = Depends(get_developer_service),
    current_user = Depends(require_admin)
):
    return await service.create_developer(schema)

@router.get("", response_model=List[DeveloperResponse])
async def list_developers(
    service: DeveloperService = Depends(get_developer_service),
    current_user = Depends(require_admin)
):
    return await service.list_developers()

@router.get("/{developer_id}", response_model=DeveloperResponse)
async def get_developer(
    developer_id: str,
    service: DeveloperService = Depends(get_developer_service),
    current_user = Depends(require_admin)
):
    try:
        parsed_id = uuid.UUID(developer_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Developer not found"
        )
    return await service.get_developer(parsed_id)

@router.patch("/{developer_id}", response_model=DeveloperResponse)
async def update_developer(
    developer_id: str,
    schema: DeveloperUpdate,
    service: DeveloperService = Depends(get_developer_service),
    current_user = Depends(require_admin)
):
    try:
        parsed_id = uuid.UUID(developer_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Developer not found"
        )
    return await service.update_developer(parsed_id, schema)

@router.delete("/{developer_id}", response_model=DeveloperResponse)
async def delete_developer(
    developer_id: str,
    service: DeveloperService = Depends(get_developer_service),
    current_user = Depends(require_admin)
):
    try:
        parsed_id = uuid.UUID(developer_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Developer not found"
        )
    return await service.deactivate_developer(parsed_id)
