from datetime import datetime

from fastapi.testclient import TestClient

from src.task_mgmt_api.main import app

client = TestClient(app)


def test_create_task_returns_created_task():
    payload = {
        "name": "Write tests",
        "description": "Add API route tests",
        "due_date": "2026-09-22T15:00:00",
        "completed": False,
    }

    response = client.post("/tasks", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Write tests"
    assert data["description"] == "Add API route tests"
    assert data["completed"] is False
    assert data["id"] == 1
    assert "created_at" in data
