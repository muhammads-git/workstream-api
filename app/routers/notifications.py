from fastapi import APIRouter, WebSocket,Depends,HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.auth_services import get_current_user
from app.models import User,Organization,Membership,MemberRole,Notification

notification_router = APIRouter()


@notification_router.websocket('/ws/{user_id}')
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    manager = websocket.app.state.manager
    await manager.connect(user_id, websocket)  # ← add this
    try:
        while True:
            await websocket.receive_text()
    except:
        manager.disconnect(user_id)



@notification_router.get('/notifications')
def get_all_notifications(db : Session = Depends(get_db), curr_user = Depends(get_current_user)):
    
    user = db.query(User).filter(User.id == curr_user.get('user_id')).first()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    
    notifications = db.query(Notification).filter(Notification.user_id == user.id,Notification.read == False).all()

    return {
        'Notifications' : [
            {
                'message':n.message,
                'type':n.type
            }
            for n in notifications
        ]
    }