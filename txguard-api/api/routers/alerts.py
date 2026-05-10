from typing import List, Optional
from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from redis.asyncio import Redis
from ..database import get_db
from ..models.alert import Alert
from ..schemas.alert import Alert as AlertSchema
from ..config import settings
from ..realtime import ALERTS_CHANNEL

router = APIRouter(prefix="/alerts", tags=["alerts"])

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@router.get("/", response_model=List[AlertSchema])
async def get_alerts(
    tier: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Alert)
    if tier:
        query = query.filter(Alert.risk_tier == tier)
    if status:
        query = query.filter(Alert.investigation_status == status)
    return query.order_by(Alert.created_at.desc()).all()

@router.websocket("/live")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(ALERTS_CHANNEL)
    try:
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message and message.get("data"):
                await websocket.send_text(message["data"])
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    finally:
        await pubsub.unsubscribe(ALERTS_CHANNEL)
        await pubsub.close()
        await redis_client.close()
