from fastapi import APIRouter, WebSocket

notification_router = APIRouter()


@notification_router.websocket('/ws/{user_id}')
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    manager = websocket.app.state.manager
    print(f'Notification manager {id(manager)}')
    await manager.connect(user_id, websocket)  # ← add this
    try:
        while True:
            await websocket.receive_text()
    except:
        manager.disconnect(user_id)

