from datetime import date, timedelta

import pytest


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
    assert (
        second_response.json()["detail"]["message"]
        == "Task with the same name and due date already exists"
    )


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


@pytest.mark.asyncio
async def test_get_tasks_returns_empty_list_when_no_tasks(client):
    response = await client.get("/v1/tasks")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_tasks_returns_all_tasks(client):
    # Create two tasks first
    payload1 = {
        "name": "Task 1",
        "description": "First task",
        "due_date": (date.today() + timedelta(days=1)).isoformat(),
        "completed": False,
    }
    payload2 = {
        "name": "Task 2",
        "description": "Second task",
        "due_date": (date.today() + timedelta(days=2)).isoformat(),
        "completed": False,
    }

    await client.post("/v1/tasks", json=payload1)
    await client.post("/v1/tasks", json=payload2)

    response = await client.get("/v1/tasks")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Task 1"
    assert data[1]["name"] == "Task 2"


@pytest.mark.asyncio
async def test_get_task_by_id_returns_task(client):
    payload = {
        "name": "Task by ID",
        "description": "Fetch this task by its ID",
        "due_date": (date.today() + timedelta(days=1)).isoformat(),
        "completed": False,
    }

    create_response = await client.post("/v1/tasks", json=payload)
    task_id = create_response.json()["id"]

    get_response = await client.get(f"/v1/tasks/{task_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == task_id
    assert data["name"] == "Task by ID"


@pytest.mark.asyncio
async def test_get_task_by_id_returns_404_for_nonexistent_task(client):
    response = await client.get("/v1/tasks/9999")  # Assuming this ID doesn't exist
    assert response.status_code == 404
    assert response.json()["detail"]["message"] == "Task not found"
