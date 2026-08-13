import uuid
from typing import List, Dict, Any
from fastapi import HTTPException, status
from app.repositories.developer_repository import DeveloperRepository
from app.models.developer import Developer
from app.schemas.developer import DeveloperCreate, DeveloperUpdate

class DeveloperService:
    def __init__(self, repository: DeveloperRepository):
        self.repository = repository

    def _get_active_project_count(self, developer: Developer) -> int:
        if not developer.projects:
            return 0
        return sum(1 for p in developer.projects if p.status.lower() == "active")

    def _to_response_dict(self, developer: Developer) -> Dict[str, Any]:
        return {
            "id": developer.id,
            "name": developer.name,
            "email": developer.email,
            "phone": developer.phone,
            "role": developer.role,
            "is_active": developer.is_active,
            "active_project_count": self._get_active_project_count(developer),
            "created_at": developer.created_at,
            "updated_at": developer.updated_at
        }

    async def create_developer(self, schema: DeveloperCreate) -> Dict[str, Any]:
        existing = await self.repository.get_by_email(schema.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Developer with this email already registered"
            )
        
        dev = Developer(
            name=schema.name,
            email=schema.email,
            phone=schema.phone,
            role=schema.role,
            is_active=True
        )
        created_dev = await self.repository.create(dev)
        reloaded = await self.repository.get_by_id(created_dev.id)
        return self._to_response_dict(reloaded or created_dev)

    async def list_developers(self) -> List[Dict[str, Any]]:
        devs = await self.repository.list_all()
        return [self._to_response_dict(d) for d in devs]

    async def get_developer(self, developer_id: uuid.UUID) -> Dict[str, Any]:
        dev = await self.repository.get_by_id(developer_id)
        if not dev:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Developer not found"
            )
        return self._to_response_dict(dev)

    async def update_developer(self, developer_id: uuid.UUID, schema: DeveloperUpdate) -> Dict[str, Any]:
        dev = await self.repository.get_by_id(developer_id)
        if not dev:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Developer not found"
            )

        if schema.email is not None and schema.email != dev.email:
            existing = await self.repository.get_by_email(schema.email)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered to another developer"
                )
            dev.email = schema.email

        if schema.name is not None:
            dev.name = schema.name
        if schema.phone is not None:
            dev.phone = schema.phone
        if schema.role is not None:
            dev.role = schema.role

        updated_dev = await self.repository.update(dev)
        return self._to_response_dict(updated_dev)

    async def deactivate_developer(self, developer_id: uuid.UUID) -> Dict[str, Any]:
        dev = await self.repository.get_by_id(developer_id)
        if not dev:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Developer not found"
            )
        
        dev.is_active = False
        updated_dev = await self.repository.update(dev)
        return self._to_response_dict(updated_dev)
