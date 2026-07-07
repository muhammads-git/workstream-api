from fastapi import APIRouter, WebSocket

notification_router = APIRouter()

@notification_router.websocket('/ws/{user_id}')
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f'Message received: {data}')








