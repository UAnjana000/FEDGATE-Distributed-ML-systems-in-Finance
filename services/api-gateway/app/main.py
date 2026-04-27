import os
from datetime import datetime

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from services.common.logging import configure_logging
from services.common.schemas import BorrowerIn

configure_logging("api-gateway")
app = FastAPI(title="API Gateway", version="0.1.0")

RISK_ENGINE_URL = os.getenv("RISK_ENGINE_URL", "http://risk-engine:8001")
ALERT_SERVICE_URL = os.getenv("ALERT_SERVICE_URL", "http://alert-service:8003")
FL_ORCHESTRATOR_URL = os.getenv("FL_ORCHESTRATOR_URL", "http://fl-orchestrator:8002")

cors_allow_origins = os.getenv("CORS_ALLOW_ORIGINS", "*")
allow_origins = ["*"] if cors_allow_origins.strip() == "*" else [
    origin.strip() for origin in cors_allow_origins.split(",") if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "api-gateway"}


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "api-gateway",
        "message": "API gateway is running. Visit /docs for interactive API docs.",
    }


@app.post("/borrowers/score")
async def score_borrower(payload: BorrowerIn) -> dict:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(f"{RISK_ENGINE_URL}/risk/score", json=payload.model_dump())
    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()


@app.get("/alerts")
async def get_alerts(limit: int = 50) -> dict:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{ALERT_SERVICE_URL}/alerts", params={"limit": limit})
    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()


@app.get("/borrowers/snapshots")
async def get_snapshots(limit: int = 50) -> dict:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{RISK_ENGINE_URL}/risk/snapshots", params={"limit": limit})
    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()


@app.post("/borrowers/seed")
async def seed_sample_borrowers() -> dict[str, str | int]:
    payloads = [
        BorrowerIn(
            borrower_id=f"seed-{idx}",
            monthly_income=50000 + idx * 10000,
            existing_emi=12000 + idx * 1000,
            requested_loan_emi=6000 + idx * 800,
            debt_outstanding=200000 + idx * 20000,
            account_balance_series=[100000 - i * 1000 - idx * 200 for i in range(12)],
            repayment_delay_series=[0, 0, 1, 0, 2, 1, 0, 1, 2, 3, 2, 1],
        )
        for idx in range(1, 4)
    ]
    async with httpx.AsyncClient(timeout=30.0) as client:
        for payload in payloads:
            await client.post(f"{RISK_ENGINE_URL}/risk/score", json=payload.model_dump())
    return {"status": "seeded", "count": len(payloads), "at": datetime.utcnow().isoformat()}


@app.post("/federated/start")
async def start_federated_rounds(req: dict) -> dict:
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(f"{FL_ORCHESTRATOR_URL}/fl/start", json=req)
    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()
