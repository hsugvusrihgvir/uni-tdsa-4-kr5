import pytest
from fastapi.testclient import TestClient

from Task3.app.main import app, manager


@pytest.fixture(autouse=True)
def clear_rooms():
    manager.rooms.clear()


@pytest.fixture
def client():
    return TestClient(app)


def test_connect_to_room(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as websocket:
        data = websocket.receive_json()

        assert data == {
            "type": "join",
            "room_id": "python",
            "username": "alice"
        }

        response = client.get("/rooms/python/users")

        assert response.status_code == 200
        assert response.json() == {
            "room_id": "python",
            "users": ["alice"]
        }


def test_send_message(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as websocket:
        websocket.receive_json()

        websocket.send_json({
            "type": "message",
            "text": "Hello"
        })

        assert websocket.receive_json() == {
            "type": "message",
            "room_id": "python",
            "username": "alice",
            "text": "Hello"
        }


def test_two_clients_get_same_message(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as alice:
        alice.receive_json()

        with client.websocket_connect("/ws/rooms/python?username=bob") as bob:
            alice.receive_json()
            bob.receive_json()

            alice.send_json({
                "type": "message",
                "text": "Hello"
            })

            message_for_alice = alice.receive_json()
            message_for_bob = bob.receive_json()

            assert message_for_alice == {
                "type": "message",
                "room_id": "python",
                "username": "alice",
                "text": "Hello"
            }
            assert message_for_bob == message_for_alice


def test_users_from_other_rooms_dont_get_message(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as alice:
        alice.receive_json()

        with client.websocket_connect("/ws/rooms/js?username=bob") as bob:
            bob.receive_json()

            alice.send_json({
                "type": "message",
                "text": "Hello"
            })

            assert alice.receive_json() == {
                "type": "message",
                "room_id": "python",
                "username": "alice",
                "text": "Hello"
            }
            assert client.get("/rooms/js/users").json() == {
                "room_id": "js",
                "users": ["bob"]
            }


def test_long_message(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as websocket:
        websocket.receive_json()

        websocket.send_json({
            "type": "message",
            "text": "a" * 301
        })

        assert websocket.receive_json() == {
            "type": "error",
            "detail": "Message is too long"
        }


def test_user_removed_after_disconnect(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as websocket:
        websocket.receive_json()

    assert client.get("/rooms/python/users").json() == {
        "room_id": "python",
        "users": []
    }
