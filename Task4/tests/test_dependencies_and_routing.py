import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.storage import clear_tasks


@pytest.fixture(autouse=True)
def clear_storage():
    clear_tasks()


@pytest.fixture
def client():
    return TestClient(app)


def create_task(client, user_id: int, status: str = "todo", priority: int = 4):
    return client.post(
        "/tasks",
        headers={"X-User-Id": str(user_id)},
        json={
            "title": "Task test",
            "description": "Description test",
            "status": status,
            "priority": priority
        }
    )


def test_users_me(client):
    response = client.get(
        "/users/me",
        headers={
            "X-User-Id": "10",
            "X-User-Role": "user"
        }
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": 10,
        "role": "user"
    }


def test_no_user_header(client):
    response = client.get("/users/me")

    assert response.status_code == 401


def test_user_cant_get_admin_stats(client):
    response = client.get(
        "/admin/stats",
        headers={
            "X-User-Id": "10",
            "X-User-Role": "user"
        }
    )

    assert response.status_code == 403


def test_admin_get_stats(client):
    create_task(client, 10, "todo")
    create_task(client, 10, "todo")
    create_task(client, 20, "in_progress")
    create_task(client, 20, "done")
    create_task(client, 30, "done")

    response = client.get(
        "/admin/stats",
        headers={
            "X-User-Id": "1",
            "X-User-Role": "admin"
        }
    )

    assert response.status_code == 200
    assert response.json() == {
        "total_tasks": 5,
        "by_status": {
            "todo": 2,
            "in_progress": 1,
            "done": 2
        }
    }


def test_user_cant_delete_foreign_task(client):
    create_response = create_task(client, 10)
    task_id = create_response.json()["id"]

    response = client.delete(
        f"/tasks/{task_id}",
        headers={"X-User-Id": "20"}
    )

    assert response.status_code == 404


def test_admin_can_delete_foreign_task(client):
    create_response = create_task(client, 10)
    task_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/admin/tasks/{task_id}",
        headers={
            "X-User-Id": "1",
            "X-User-Role": "admin"
        }
    )
    get_response = client.get(
        f"/tasks/{task_id}",
        headers={"X-User-Id": "10"}
    )

    assert delete_response.status_code == 204
    assert get_response.status_code == 404


def test_swagger_tags(client):
    response = client.get("/openapi.json")
    paths = response.json()["paths"]

    assert paths["/tasks"]["post"]["tags"] == ["tasks"]
    assert paths["/users/me"]["get"]["tags"] == ["users"]
    assert paths["/admin/stats"]["get"]["tags"] == ["admin"]
