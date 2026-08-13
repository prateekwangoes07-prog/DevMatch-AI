import pytest
from sqlalchemy import select
from app.models.developer import Developer
from app.models.client import Client
from app.models.project import Project
from app.models.enums import DeveloperRole

@pytest.mark.anyio
async def test_db_connection(db_session):
    # Verify we can connect and run a simple query
    result = await db_session.execute(select(1))
    assert result.scalar() == 1

@pytest.mark.anyio
async def test_create_and_retrieve_models(db_session):
    # 1. Create a developer
    dev = Developer(
        name="Alice Smith",
        email="alice@example.com",
        phone="1234567890",
        role=DeveloperRole.AI_ML
    )
    db_session.add(dev)

    # 2. Create a client
    client = Client(
        name="John Doe",
        company="Acme Corp",
        email="john@example.com",
        phone="0987654321",
        requirement="Need an AI chatbot",
        required_role=DeveloperRole.AI_ML,
        status="active"
    )
    db_session.add(client)
    
    await db_session.commit()

    # 3. Create a project linking them
    project = Project(
        client_id=client.id,
        developer_id=dev.id,
        name="Acme AI Chatbot",
        status="active"
    )
    db_session.add(project)
    await db_session.commit()

    # Refresh and load relationships
    result_dev = await db_session.execute(
        select(Developer).filter(Developer.id == dev.id)
    )
    db_dev = result_dev.scalar_one()
    
    result_client = await db_session.execute(
        select(Client).filter(Client.id == client.id)
    )
    db_client = result_client.scalar_one()

    result_proj = await db_session.execute(
        select(Project).filter(Project.id == project.id)
    )
    db_proj = result_proj.scalar_one()

    # Verify relationship references
    assert db_proj.client_id == db_client.id
    assert db_proj.developer_id == db_dev.id

    # Cleanup
    await db_session.delete(db_proj)
    await db_session.delete(db_client)
    await db_session.delete(db_dev)
    await db_session.commit()


@pytest.mark.anyio
async def test_client_delete_restrictions(db_session):
    from app.models.appointment import Appointment
    from app.models.call import Call
    from sqlalchemy.exc import IntegrityError
    from datetime import datetime, timezone
    
    # Clean up leftover test data first
    from sqlalchemy import delete
    client_res = await db_session.execute(select(Client).filter(Client.email == "restrict@example.com"))
    stale_client = client_res.scalar_one_or_none()
    if stale_client:
        await db_session.execute(delete(Appointment).filter(Appointment.client_id == stale_client.id))
        await db_session.execute(delete(Call).filter(Call.client_id == stale_client.id))
        await db_session.execute(delete(Client).filter(Client.id == stale_client.id))
        await db_session.commit()

    # 1. Create client
    client = Client(
        name="Restriction Client",
        company="Restricted Corp",
        email="restrict@example.com",
        required_role=DeveloperRole.AI_ML,
        status="active"
    )
    db_session.add(client)
    await db_session.commit()
    await db_session.refresh(client)

    client_id = client.id

    # 2. Add an appointment to the client
    apt = Appointment(
        client_id=client_id,
        appointment_time=datetime.now(timezone.utc),
        status="scheduled"
    )
    db_session.add(apt)
    await db_session.commit()
    await db_session.refresh(apt)
    apt_id = apt.id

    # Verify that trying to delete client raises IntegrityError because of the RESTRICT constraint
    await db_session.delete(client)
    with pytest.raises(IntegrityError):
        await db_session.commit()
    await db_session.rollback()

    # Re-fetch client to refresh session state after rollback
    client_result = await db_session.execute(select(Client).filter(Client.id == client_id))
    client = client_result.scalar_one()

    # Clean up the appointment first, which succeeds
    apt_result = await db_session.execute(select(Appointment).filter(Appointment.id == apt_id))
    apt = apt_result.scalar_one()
    await db_session.delete(apt)
    await db_session.commit()

    # 3. Add a call to the client
    call = Call(
        client_id=client_id,
        call_time=datetime.now(timezone.utc),
        call_outcome="Connected",
        call_summary="First meeting success"
    )
    db_session.add(call)
    await db_session.commit()
    await db_session.refresh(call)
    call_id = call.id

    # Verify that trying to delete client raises IntegrityError because of the RESTRICT constraint
    await db_session.delete(client)
    with pytest.raises(IntegrityError):
        await db_session.commit()
    await db_session.rollback()

    # Re-fetch client and call to refresh session state after rollback
    client_result = await db_session.execute(select(Client).filter(Client.id == client_id))
    client = client_result.scalar_one()
    call_result = await db_session.execute(select(Call).filter(Call.id == call_id))
    call = call_result.scalar_one()

    # Clean up call first, then delete client
    await db_session.delete(call)
    await db_session.commit()
    await db_session.delete(client)
    await db_session.commit()
