import asyncio
import os
from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

os.environ["DB_USER"] = "test_user"
os.environ["DB_PASSWORD"] = "test_password"
os.environ["DB_HOST"] = "localhost"
os.environ["DB_PORT"] = "5432"
os.environ["DB_DRIVER"] = "sqlite+aiosqlite"

from src.task_mgmt_api.database import Base, init_db
from src.task_mgmt_api.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("DB_NAME", str(tmp_path / "task_mgmt_test.db"))
    init_db()

    async def setup_db():
        from src.task_mgmt_api.database import engine

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(setup_db())

    with TestClient(app) as test_client:
        yield test_client


def test_create_task_returns_created_task(client):
    payload = {
        "name": "Write tests",
        "description": "Add API route tests",
        "due_date": "2026-09-22",
        "completed": False,
    }

    response = client.post("/v1/tasks", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Write tests"
    assert data["description"] == "Add API route tests"
    assert data["completed"] is False
    assert data["due_date"] == "2026-09-22"
    assert data["id"] == 1
    assert "created_at" in data


def test_create_task_rejects_past_due_date(client):
    payload = {
        "name": "Past task",
        "description": "This due date is in the past",
        "due_date": (date.today() - timedelta(days=1)).isoformat(),
        "completed": False,
    }

    response = client.post("/v1/tasks", json=payload)

    assert response.status_code == 422
    assert response.json()["detail"]["message"] == "Due date cannot be in the past"


def test_create_task_rejects_duplicate_name_and_due_date(client):
    payload = {
        "name": "Duplicate task",
        "description": "This should not be allowed twice",
        "due_date": "2026-09-25",
        "completed": False,
    }

    first_response = client.post("/v1/tasks", json=payload)
    second_response = client.post("/v1/tasks", json=payload)

    assert first_response.status_code == 200
    assert second_response.status_code == 422
    assert second_response.json()["detail"]["message"] == "Task with the same name and due date already exists"


def test_create_task_rejects_empty_name(client):
    payload = {
        "name": "",
        "description": "Empty names are invalid",
        "due_date": "2026-09-30",
        "completed": False,
    }

    response = client.post("/v1/tasks", json=payload)

    assert response.status_code == 422
