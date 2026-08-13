import uuid
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.customer_request import CustomerRequest

class CustomerRequestRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, request_id: uuid.UUID) -> CustomerRequest | None:
        result = await self.db.execute(
            select(CustomerRequest).filter(CustomerRequest.id == request_id)
        )
        return result.scalar_one_or_none()

    async def list_all(self) -> Sequence[CustomerRequest]:
        result = await self.db.execute(
            select(CustomerRequest).order_by(CustomerRequest.created_at.desc())
        )
        return result.scalars().all()

    async def create(self, request: CustomerRequest) -> CustomerRequest:
        self.db.add(request)
        await self.db.commit()
        await self.db.refresh(request)
        return request

    async def update(self, request: CustomerRequest) -> CustomerRequest:
        await self.db.commit()
        await self.db.refresh(request)
        return request
