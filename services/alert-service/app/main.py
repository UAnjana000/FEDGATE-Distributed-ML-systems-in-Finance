import json

from fastapi import FastAPI

from services.common.logging import configure_logging
from services.common.storage import redis_client

configure_logging("alert-service")
app = FastAPI(title="Alert Service", version="0.1.0")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "alert-service"}


@app.get("/alerts")
async def get_alerts(limit: int = 50) -> dict[str, list[dict]]:
    raw_items = redis_client.lrange("alerts:list", 0, max(0, limit - 1))
    parsed = [json.loads(item) for item in raw_items]
    return {"items": parsed}
