import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.db import clear_tasks


@pytest.fixture(autouse=True)
def clear_storage():
    clear_tasks()


@pytest.fixture
def client():
    return TestClient(app)


def test_create_task(client):
    response = client.post(
        "/tasks",
        headers={"X-User-Id": "10"},
        json={
            "title": "Задача 1",
            "description": "Описание 1",
            "status": "todo",
            "priority": 4
        }
    )

    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "title": "Задача 1",
        "description": "Описание 1",
        "status": "todo",
        "priority": 4,
        "owner_id": 10
    }


def test_health(client, monkeypatch):
    monkeypatch.setenv("APP_ENV", "docker")

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "env": "docker"
    }


def test_short_title(client):
    response = client.post(
        "/tasks",
        headers={"X-User-Id": "10"},
        json={
            "title": "AB",
            "description": "Описание 1",
            "status": "todo",
            "priority": 4
        }
    )

    assert response.status_code == 422


def test_no_user_header(client):
    response = client.post(
        "/tasks",
        json={
            "title": "Задача 1",
            "description": "Описание 1",
            "status": "todo",
            "priority": 4
        }
    )

    assert response.status_code == 401


def test_only_own_tasks(client):
    client.post(
        "/tasks",
        headers={"X-User-Id": "10"},
        json={
            "title": "Задача 1",
            "description": "Описание 1",
            "status": "todo",
            "priority": 2
        }
    )

    client.post(
        "/tasks",
        headers={"X-User-Id": "20"},
        json={
            "title": "Задача 2",
            "description": "Описание 2",
            "status": "done",
            "priority": 5
        }
    )

    response = client.get(
        "/tasks",
        headers={"X-User-Id": "10"}
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["owner_id"] == 10
    assert response.json()[0]["title"] == "Задача 1"


def test_filter_tasks(client):
    client.post(
        "/tasks",
        headers={"X-User-Id": "10"},
        json={
            "title": "Задача 1",
            "description": "Описание 1",
            "status": "todo",
            "priority": 2
        }
    )

    client.post(
        "/tasks",
        headers={"X-User-Id": "10"},
        json={
            "title": "Задача 2",
            "description": "Описание 2",
            "status": "todo",
            "priority": 5
        }
    )

    client.post(
        "/tasks",
        headers={"X-User-Id": "10"},
        json={
            "title": "Задача 3",
            "description": "Описание 3",
            "status": "done",
            "priority": 5
        }
    )

    response = client.get(
        "/tasks",
        headers={"X-User-Id": "10"},
        params={
            "status": "todo",
            "min_priority": 4
        }
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Задача 2"
    assert response.json()[0]["status"] == "todo"
    assert response.json()[0]["priority"] == 5


def test_update_status(client):
    create_response = client.post(
        "/tasks",
        headers={"X-User-Id": "10"},
        json={
            "title": "Задача 1",
            "description": "Описание 1",
            "status": "todo",
            "priority": 4
        }
    )

    task_id = create_response.json()["id"]

    response = client.patch(
        f"/tasks/{task_id}/status",
        headers={"X-User-Id": "10"},
        json={
            "status": "done"
        }
    )

    assert response.status_code == 200
    assert response.json()["id"] == task_id
    assert response.json()["status"] == "done"


def test_foreign_task(client):
    create_response = client.post(
        "/tasks",
        headers={"X-User-Id": "10"},
        json={
            "title": "Задача 1",
            "description": "Описание 1",
            "status": "todo",
            "priority": 4
        }
    )

    task_id = create_response.json()["id"]

    response = client.get(
        f"/tasks/{task_id}",
        headers={"X-User-Id": "20"}
    )

    assert response.status_code == 404


def test_missing_task(client):
    response = client.get(
        "/tasks/999",
        headers={"X-User-Id": "10"}
    )

    assert response.status_code == 404


def test_delete_task(client):
    create_response = client.post(
        "/tasks",
        headers={"X-User-Id": "10"},
        json={
            "title": "Задача 1",
            "description": "Описание 1",
            "status": "todo",
            "priority": 4
        }
    )

    task_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/tasks/{task_id}",
        headers={"X-User-Id": "10"}
    )

    get_response = client.get(
        f"/tasks/{task_id}",
        headers={"X-User-Id": "10"}
    )

    assert delete_response.status_code == 204
    assert get_response.status_code == 404
