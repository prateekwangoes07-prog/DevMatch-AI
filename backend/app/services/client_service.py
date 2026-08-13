import uuid
from typing import List, Dict, Any
from fastapi import HTTPException, status
from app.repositories.client_repository import ClientRepository
from app.models.client import Client
from app.schemas.client import ClientCreate, ClientUpdate

class ClientService:
    def __init__(self, repository: ClientRepository):
        self.repository = repository

    def _to_response_dict(self, client: Client) -> Dict[str, Any]:
        return {
            "id": client.id,
            "name": client.name,
            "company": client.company,
            "email": client.email,
            "phone": client.phone,
            "requirement": client.requirement,
            "required_role": client.required_role,
            "status": client.status,
            "created_at": client.created_at,
            "updated_at": client.updated_at
        }

    async def create_client(self, schema: ClientCreate) -> Dict[str, Any]:
        existing = await self.repository.get_by_email(schema.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Client with this email already registered"
            )
        
        client = Client(
            name=schema.name,
            company=schema.company,
            email=schema.email,
            phone=schema.phone,
            requirement=schema.requirement,
            required_role=schema.required_role,
            status="active"
        )
        created_client = await self.repository.create(client)
        return self._to_response_dict(created_client)

    async def list_clients(self) -> List[Dict[str, Any]]:
        clients = await self.repository.list_all()
        return [self._to_response_dict(c) for c in clients]

    async def get_client(self, client_id: uuid.UUID) -> Dict[str, Any]:
        client = await self.repository.get_by_id(client_id)
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found"
            )
        return self._to_response_dict(client)

    async def update_client(self, client_id: uuid.UUID, schema: ClientUpdate) -> Dict[str, Any]:
        client = await self.repository.get_by_id(client_id)
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found"
            )

        if schema.email is not None and schema.email != client.email:
            existing = await self.repository.get_by_email(schema.email)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered to another client"
                )
            client.email = schema.email

        if schema.name is not None:
            client.name = schema.name
        if schema.company is not None:
            client.company = schema.company
        if schema.phone is not None:
            client.phone = schema.phone
        if schema.requirement is not None:
            client.requirement = schema.requirement
        if schema.required_role is not None:
            client.required_role = schema.required_role
        if schema.status is not None:
            client.status = schema.status

        updated_client = await self.repository.update(client)
        return self._to_response_dict(updated_client)

    async def deactivate_client(self, client_id: uuid.UUID) -> Dict[str, Any]:
        client = await self.repository.get_by_id(client_id)
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found"
            )
        
        client.status = "inactive"
        updated_client = await self.repository.update(client)
        return self._to_response_dict(updated_client)
