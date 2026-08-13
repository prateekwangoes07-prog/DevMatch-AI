import uuid
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.client import Client

class ClientRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, client_id: uuid.UUID) -> Client | None:
        result = await self.db.execute(
            select(Client).filter(Client.id == client_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Client | None:
        result = await self.db.execute(
            select(Client).filter(Client.email == email)
        )
        return result.scalar_one_or_none()

    async def list_all(self) -> Sequence[Client]:
        result = await self.db.execute(
            select(Client).order_by(Client.created_at.desc())
        )
        return result.scalars().all()

    async def create(self, client: Client) -> Client:
        self.db.add(client)
        await self.db.commit()
        await self.db.refresh(client)
        return client

    async def update(self, client: Client) -> Client:
        await self.db.commit()
        await self.db.refresh(client)
        return client
