import pytest
import uuid
from datetime import datetime, timezone, timedelta
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select, delete
from app.models.user import User
from app.models.client import Client
from app.models.appointment import Appointment
from app.models.enums import UserRole
from app.dependencies.auth import require_admin
from app.main import app

@pytest.mark.anyio
async def test_appointment_auth_enforcement(db_session):
    from app.db.session import get_db
    
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async def override_require_admin_unauthorized():
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Not authenticated")

    async def override_require_admin_forbidden():
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Not enough permissions")

    transport = ASGITransport(app=app)
    
    # Test 1: Unauthenticated user is rejected
    app.dependency_overrides[require_admin] = override_require_admin_unauthorized
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/appointments")
        assert res.status_code == 401
        
        res_post = await ac.post("/appointments/book", json={
            "client_id": str(uuid.uuid4()),
            "appointment_time": datetime.now(timezone.utc).isoformat()
        })
        assert res_post.status_code == 401

    # Test 2: Non-admin is rejected
    app.dependency_overrides[require_admin] = override_require_admin_forbidden
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/appointments")
        assert res.status_code == 403

        res_post = await ac.post("/appointments/book", json={
            "client_id": str(uuid.uuid4()),
            "appointment_time": datetime.now(timezone.utc).isoformat()
        })
        assert res_post.status_code == 403

    app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_appointment_booking_flow(db_session):
    from app.db.session import get_db
    
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    # Clean up first
    await db_session.execute(delete(User).filter(User.email == "admin_appts@example.com"))
    # Delete appointments referencing these clients first to satisfy RESTRICT FK constraint
    await db_session.execute(
        delete(Appointment).where(
            Appointment.client_id.in_(
                select(Client.id).filter(Client.email.in_(["active_c@example.com", "inactive_c@example.com"]))
            )
        )
    )
    await db_session.execute(delete(Client).filter(Client.email.in_(["active_c@example.com", "inactive_c@example.com"])))
    await db_session.commit()

    # Create admin
    admin_user = User(
        name="Admin Appointment Manager",
        email="admin_appts@example.com",
        password_hash="some_hashed_pass",
        role=UserRole.ADMIN,
        is_active=True
    )
    db_session.add(admin_user)

    # Create active client
    active_client = Client(
        name="Active Client",
        company="Active Co",
        email="active_c@example.com",
        required_role="AI_ML",
        status="active"
    )
    db_session.add(active_client)

    # Create inactive client
    inactive_client = Client(
        name="Inactive Client",
        company="Inactive Co",
        email="inactive_c@example.com",
        required_role="AI_ML",
        status="inactive"
    )
    db_session.add(inactive_client)

    await db_session.commit()
    await db_session.refresh(admin_user)
    await db_session.refresh(active_client)
    await db_session.refresh(inactive_client)

    async def override_require_admin():
        return admin_user

    app.dependency_overrides[require_admin] = override_require_admin

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Test 1: Fetch availability
        res_avail = await ac.get("/appointments/availability")
        assert res_avail.status_code == 200
        slots = res_avail.json()
        assert len(slots) > 0

        # Test 2: Invalid/non-existent client is rejected (404)
        bad_uuid = uuid.uuid4()
        res_bad_client = await ac.post("/appointments/book", json={
            "client_id": str(bad_uuid),
            "appointment_time": datetime.now(timezone.utc).isoformat()
        })
        assert res_bad_client.status_code == 404

        # Test 3: Inactive client is rejected (400)
        res_inactive_client = await ac.post("/appointments/book", json={
            "client_id": str(inactive_client.id),
            "appointment_time": datetime.now(timezone.utc).isoformat()
        })
        assert res_inactive_client.status_code == 400
        assert "Inactive clients cannot book new appointments" in res_inactive_client.json()["detail"]

        # Test 4: Active client can successfully book appointment
        appt_time = datetime.now(timezone.utc) + timedelta(days=1)
        res_book = await ac.post("/appointments/book", json={
            "client_id": str(active_client.id),
            "appointment_time": appt_time.isoformat()
        })
        assert res_book.status_code == 201
        booking_res = res_book.json()
        assert booking_res["client_id"] == str(active_client.id)
        assert booking_res["status"] == "scheduled"
        assert booking_res["external_booking_id"] is not None
        assert booking_res["external_booking_id"].startswith("mock_cal_")
        
        external_id = booking_res["external_booking_id"]
        appt_id = booking_res["id"]

        # Test 5: Re-submitting the same booking with the same external_booking_id returns existing record without duplication
        res_dup = await ac.post("/appointments/book", json={
            "client_id": str(active_client.id),
            "appointment_time": appt_time.isoformat(),
            "external_booking_id": external_id
        })
        assert res_dup.status_code == 201
        assert res_dup.json()["id"] == appt_id

        # Test 6: Verify appointments can be listed and the new record is present
        res_list = await ac.get("/appointments")
        assert res_list.status_code == 200
        items = res_list.json()
        assert len(items) > 0
        assert any(item["id"] == appt_id for item in items)

        # Test 7: Get appointment details
        res_details = await ac.get(f"/appointments/{appt_id}")
        assert res_details.status_code == 200
        assert res_details.json()["id"] == appt_id

        # Test 8: Get details with invalid UUID handles safely
        res_bad_id = await ac.get("/appointments/not-a-uuid-string")
        assert res_bad_id.status_code == 404

        # Test 9: Cancel appointment
        res_cancel = await ac.post(f"/appointments/{appt_id}/cancel")
        assert res_cancel.status_code == 200
        assert res_cancel.json()["status"] == "cancelled"

        # Verify historical record remains in the database (not deleted)
        result_db = await db_session.execute(select(Appointment).filter(Appointment.id == uuid.UUID(appt_id)))
        db_appt = result_db.scalar_one_or_none()
        assert db_appt is not None
        assert db_appt.status == "cancelled"

    app.dependency_overrides.clear()
