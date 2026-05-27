from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()


class RoomManager:
    def __init__(self):
        self.rooms = {}

    async def connect(self, room_id: str, username: str, websocket: WebSocket) -> None:
        await websocket.accept()

        if room_id not in self.rooms:
            self.rooms[room_id] = []

        self.rooms[room_id].append({
            "username": username,
            "websocket": websocket
        })

        await self.broadcast(room_id, {
            "type": "join",
            "room_id": room_id,
            "username": username
        })

    def disconnect(self, room_id: str, username: str, websocket: WebSocket) -> None:
        if room_id not in self.rooms:
            return

        self.rooms[room_id] = [
            client for client in self.rooms[room_id]
            if client["websocket"] != websocket
        ]

        if not self.rooms[room_id]:
            del self.rooms[room_id]

    async def broadcast(self, room_id: str, payload: dict) -> None:
        for client in self.rooms.get(room_id, []):
            await client["websocket"].send_json(payload)

    def get_users(self, room_id: str) -> list[str]:
        return [
            client["username"]
            for client in self.rooms.get(room_id, [])
        ]


manager = RoomManager()


@app.get("/rooms/{room_id}/users")
async def get_room_users(room_id: str) -> dict:
    return {
        "room_id": room_id,
        "users": manager.get_users(room_id)
    }


@app.websocket("/ws/rooms/{room_id}")
async def websocket_room(websocket: WebSocket, room_id: str, username: str | None = None):
    if username is None or username.strip() == "":
        await websocket.close(code=1008)
        return

    username = username.strip()
    await manager.connect(room_id, username, websocket)

    try:
        while True:
            data = await websocket.receive_json()

            if data.get("type") == "message":
                text = data.get("text", "")

                if len(text) > 300:
                    await websocket.send_json({
                        "type": "error",
                        "detail": "Message is too long"
                    })
                    continue

                await manager.broadcast(room_id, {
                    "type": "message",
                    "room_id": room_id,
                    "username": username,
                    "text": text
                })
    except WebSocketDisconnect:
        manager.disconnect(room_id, username, websocket)
