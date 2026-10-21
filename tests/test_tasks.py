import os
import pytest
from datetime import date, timedelta


@pytest.mark.asyncio
async def test_create_task_returns_created_task(client):
    payload = {
        "name": "Write tests",
        "description": "Add API route tests",
        "due_date": (date.today() + timedelta(days=1)).isoformat(),
        "completed": False,
    }

    response = await client.post("/v1/tasks", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Write tests"
    assert data["description"] == "Add API route tests"
    assert data["completed"] is False
    assert data["due_date"] == (date.today() + timedelta(days=1)).isoformat()
    assert data["id"] == 1
    assert "created_at" in data

@pytest.mark.asyncio
async def test_create_task_rejects_past_due_date(client):
    payload = {
        "name": "Past task",
        "description": "This due date is in the past",
        "due_date": (date.today() - timedelta(days=1)).isoformat(),
        "completed": False,
    }

    response = await client.post("/v1/tasks", json=payload)

    assert response.status_code == 422
    assert response.json()["detail"]["message"] == "Due date cannot be in the past"


@pytest.mark.asyncio
async def test_create_task_rejects_duplicate_name_and_due_date(client):
    payload = {
        "name": "Duplicate task",
        "description": "This should not be allowed twice",
        "due_date": (date.today() + timedelta(days=1)).isoformat(),
        "completed": False,
    }

    first_response = await client.post("/v1/tasks", json=payload)
    second_response = await client.post("/v1/tasks", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 422
    assert second_response.json()["detail"]["message"] == "Task with the same name and due date already exists"


@pytest.mark.asyncio
async def test_create_task_rejects_empty_name(client):
    payload = {
        "name": "",
        "description": "Empty names are invalid",
        "due_date": (date.today() + timedelta(days=3)).isoformat(),
        "completed": False,
    }

    response = await client.post("/v1/tasks", json=payload)

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "name"]
