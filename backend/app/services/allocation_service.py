import uuid
from typing import List, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.developer import Developer
from app.models.client import Client
from app.models.project import Project
from app.models.enums import DeveloperRole
from app.repositories.developer_repository import DeveloperRepository

class AllocationService:
    @staticmethod
    def _get_active_project_count(developer: Developer) -> int:
        if not developer.projects:
            return 0
        return sum(1 for p in developer.projects if p.status.lower() == "active")

    @classmethod
    async def find_available_developers(
        cls, db: AsyncSession, required_role: DeveloperRole
    ) -> List[Dict[str, Any]]:
        result = await db.execute(
            select(Developer)
            .filter(Developer.is_active == True, Developer.role == required_role)
            .options(selectinload(Developer.projects))
        )
        devs = result.scalars().all()

        available_devs = []
        for dev in devs:
            count = cls._get_active_project_count(dev)
            if count < 2:
                available_devs.append({
                    "id": dev.id,
                    "name": dev.name,
                    "email": dev.email,
                    "role": dev.role,
                    "is_active": dev.is_active,
                    "active_project_count": count,
                    "available": True
                })
        return available_devs

    @classmethod
    async def allocate_developer(
        cls,
        db: AsyncSession,
        developer_id: uuid.UUID,
        client_id: uuid.UUID,
        project_name: str
    ) -> Dict[str, Any]:
        repo = DeveloperRepository(db)
        
        # Lock developer row during query
        dev = await repo.get_by_id_with_lock(developer_id)
        if not dev:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Developer not found"
            )

        if not dev.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Developer is inactive"
            )

        # Verify client exists
        client_result = await db.execute(select(Client).filter(Client.id == client_id))
        client = client_result.scalar_one_or_none()
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found"
            )

        if client.status != "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Client is inactive"
            )

        # Verify role matching
        if dev.role != client.required_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Developer role does not match client's required role"
            )

        # Enforce max-2 active projects limit
        active_count = cls._get_active_project_count(dev)
        if active_count >= 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Developer already has maximum active projects"
            )

        # Verify client does not already have an active project
        proj_result = await db.execute(
            select(Project).filter(Project.client_id == client_id, Project.status == "active")
        )
        existing_active = proj_result.scalar_one_or_none()
        if existing_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Client already has an active project assignment"
            )

        # Create project assignment
        new_project = Project(
            client_id=client_id,
            developer_id=developer_id,
            name=project_name,
            status="active"
        )
        db.add(new_project)
        from sqlalchemy.exc import IntegrityError
        try:
            await db.commit()
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Client already has an active project assignment"
            )
        await db.refresh(new_project)

        return {
            "project_id": new_project.id,
            "project_name": new_project.name,
            "status": new_project.status,
            "developer_id": new_project.developer_id,
            "client_id": new_project.client_id,
            "created_at": new_project.created_at
        }
