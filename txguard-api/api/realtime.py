import json

from redis import Redis

from .config import settings

ALERTS_CHANNEL = "txguard:alerts:live"


def publish_alert_event(event: dict) -> None:
    """Publish a JSON event for WebSocket consumers."""
    client = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    try:
        client.publish(ALERTS_CHANNEL, json.dumps(event))
    finally:
        client.close()
