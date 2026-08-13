import uuid
from typing import List, Dict, Any
from fastapi import HTTPException, status
from app.models.customer_request import CustomerRequest
from app.models.enums import ApprovalStatus
from app.repositories.customer_request_repository import CustomerRequestRepository
from app.repositories.client_repository import ClientRepository
from app.repositories.developer_repository import DeveloperRepository
from app.services.allocation_service import AllocationService
from app.schemas.customer_request import CustomerRequestCreate, CustomerRequestApproval

class CustomerRequestService:
    def __init__(
        self,
        repository: CustomerRequestRepository,
        client_repo: ClientRepository,
        dev_repo: DeveloperRepository
    ):
        self.repository = repository
        self.client_repo = client_repo
        self.dev_repo = dev_repo

    def _to_response_dict(self, req: CustomerRequest) -> Dict[str, Any]:
        return {
            "id": req.id,
            "client_id": req.client_id,
            "required_role": req.required_role,
            "recommended_developer_id": req.recommended_developer_id,
            "appointment_id": req.appointment_id,
            "approval_status": req.approval_status,
            "created_at": req.created_at,
            "updated_at": req.updated_at
        }

    async def create_request(self, schema: CustomerRequestCreate) -> Dict[str, Any]:
        # 1. Verify client exists
        client = await self.client_repo.get_by_id(schema.client_id)
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

        # 2. Validate recommended developer if provided
        if schema.recommended_developer_id is not None:
            dev = await self.dev_repo.get_by_id(schema.recommended_developer_id)
            if not dev:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Recommended developer not found"
                )
            if not dev.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Recommended developer is inactive"
                )
            if dev.role != schema.required_role:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Developer role does not match the required role"
                )
            # Check availability limits (< 2 active projects)
            active_count = AllocationService._get_active_project_count(dev)
            if active_count >= 2:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Recommended developer already has maximum active projects"
                )

        req = CustomerRequest(
            client_id=schema.client_id,
            required_role=schema.required_role,
            recommended_developer_id=schema.recommended_developer_id,
            approval_status=ApprovalStatus.PENDING
        )
        created_req = await self.repository.create(req)
        return self._to_response_dict(created_req)

    async def list_requests(self) -> List[Dict[str, Any]]:
        requests = await self.repository.list_all()
        return [self._to_response_dict(r) for r in requests]

    async def get_request(self, request_id: uuid.UUID) -> Dict[str, Any]:
        req = await self.repository.get_by_id(request_id)
        if not req:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer request not found"
            )
        return self._to_response_dict(req)

    async def update_approval(
        self, request_id: uuid.UUID, schema: CustomerRequestApproval
    ) -> Dict[str, Any]:
        req = await self.repository.get_by_id(request_id)
        if not req:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer request not found"
            )

        if schema.approval_status == ApprovalStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot change status back to PENDING"
            )

        if req.approval_status != ApprovalStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot change status once request is approved or rejected"
            )

        req.approval_status = schema.approval_status
        updated_req = await self.repository.update(req)
        return self._to_response_dict(updated_req)
