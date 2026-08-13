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
