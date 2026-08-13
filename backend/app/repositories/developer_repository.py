import uuid
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.developer import Developer

class DeveloperRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, developer_id: uuid.UUID) -> Developer | None:
        result = await self.db.execute(
            select(Developer)
            .filter(Developer.id == developer_id)
            .options(selectinload(Developer.projects))
        )
        return result.scalar_one_or_none()

    async def get_by_id_with_lock(self, developer_id: uuid.UUID) -> Developer | None:
        result = await self.db.execute(
            select(Developer)
            .filter(Developer.id == developer_id)
            .options(selectinload(Developer.projects))
            .with_for_update()
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Developer | None:
        result = await self.db.execute(
            select(Developer).filter(Developer.email == email)
        )
        return result.scalar_one_or_none()

    async def list_all(self) -> Sequence[Developer]:
        result = await self.db.execute(
            select(Developer)
            .options(selectinload(Developer.projects))
            .order_by(Developer.created_at.desc())
        )
        return result.scalars().all()

    async def create(self, developer: Developer) -> Developer:
        self.db.add(developer)
        await self.db.commit()
        await self.db.refresh(developer)
        return developer

    async def update(self, developer: Developer) -> Developer:
        await self.db.commit()
        await self.db.refresh(developer)
        return developer
