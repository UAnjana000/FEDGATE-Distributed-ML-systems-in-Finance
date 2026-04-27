import json
from datetime import datetime

import numpy as np
import torch
from fastapi import Depends, FastAPI
from sqlalchemy import select
from sqlalchemy.orm import Session

from ml.features.engineering import build_sequence_features, compute_debt_burden, compute_foir
from ml.models.lstm import RiskLSTM
from services.common.logging import configure_logging
from services.common.models import Alert, Base, Borrower, RiskSnapshot
from services.common.schemas import BorrowerIn, RiskScore
from services.common.storage import engine, get_db, redis_client

configure_logging("risk-engine")
app = FastAPI(title="Risk Engine", version="0.1.0")
model = RiskLSTM()


def _severity(prob: float, foir: float, debt_burden: float) -> tuple[str, bool]:
    distress = prob >= 0.6 or foir >= 0.5 or debt_burden >= 0.45
    if prob >= 0.75 or foir >= 0.65:
        return "critical", True
    if distress:
        return "high", True
    if prob >= 0.45:
        return "medium", False
    return "low", False


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "risk-engine"}


@app.post("/risk/score", response_model=RiskScore)
async def score(payload: BorrowerIn, db: Session = Depends(get_db)) -> RiskScore:
    sequence = build_sequence_features(payload)
    x = torch.tensor(np.expand_dims(sequence, axis=0), dtype=torch.float32)
    with torch.no_grad():
        prob = float(torch.sigmoid(model(x)).item())
    total_emi = payload.existing_emi + payload.requested_loan_emi
    foir = compute_foir(payload.monthly_income, total_emi)
    debt_burden = compute_debt_burden(payload.monthly_income, payload.debt_outstanding)
    severity, distress_flag = _severity(prob, foir, debt_burden)
    now = datetime.utcnow()

    borrower = db.get(Borrower, payload.borrower_id)
    if borrower is None:
        borrower = Borrower(
            borrower_id=payload.borrower_id,
            monthly_income=payload.monthly_income,
            existing_emi=payload.existing_emi,
            requested_loan_emi=payload.requested_loan_emi,
            debt_outstanding=payload.debt_outstanding,
        )
        db.add(borrower)
    else:
        borrower.monthly_income = payload.monthly_income
        borrower.existing_emi = payload.existing_emi
        borrower.requested_loan_emi = payload.requested_loan_emi
        borrower.debt_outstanding = payload.debt_outstanding

    snapshot = RiskSnapshot(
        borrower_id=payload.borrower_id,
        risk_probability=prob,
        foir=foir,
        debt_burden=debt_burden,
        distress_flag=distress_flag,
        severity=severity,
        created_at=now,
    )
    db.add(snapshot)

    if distress_flag:
        message = (
            f"Early distress signal for {payload.borrower_id}: "
            f"risk={prob:.2f}, foir={foir:.2f}, debt_burden={debt_burden:.2f}"
        )
        alert = Alert(
            borrower_id=payload.borrower_id,
            severity=severity,
            message=message,
            created_at=now,
        )
        db.add(alert)
        event = {
            "borrower_id": payload.borrower_id,
            "severity": severity,
            "message": message,
            "created_at": now.isoformat(),
        }
        redis_client.publish("risk_alerts", json.dumps(event))
        redis_client.lpush("alerts:list", json.dumps(event))
        redis_client.ltrim("alerts:list", 0, 199)

    db.commit()
    return RiskScore(
        borrower_id=payload.borrower_id,
        risk_probability=prob,
        foir=foir,
        debt_burden=debt_burden,
        distress_flag=distress_flag,
        severity=severity,
        generated_at=now,
    )


@app.get("/risk/snapshots")
async def snapshots(limit: int = 50, db: Session = Depends(get_db)) -> dict:
    rows = db.scalars(select(RiskSnapshot).order_by(RiskSnapshot.created_at.desc()).limit(limit)).all()
    return {
        "items": [
            {
                "borrower_id": row.borrower_id,
                "risk_probability": row.risk_probability,
                "foir": row.foir,
                "debt_burden": row.debt_burden,
                "severity": row.severity,
                "created_at": row.created_at.isoformat(),
            }
            for row in rows
        ]
    }
