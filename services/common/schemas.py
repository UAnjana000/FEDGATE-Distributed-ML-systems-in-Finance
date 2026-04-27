from datetime import datetime

from pydantic import BaseModel, Field


class BorrowerIn(BaseModel):
    borrower_id: str
    monthly_income: float = Field(gt=0)
    existing_emi: float = Field(ge=0)
    requested_loan_emi: float = Field(ge=0)
    debt_outstanding: float = Field(ge=0)
    account_balance_series: list[float] = Field(default_factory=list)
    repayment_delay_series: list[float] = Field(default_factory=list)


class RiskScore(BaseModel):
    borrower_id: str
    risk_probability: float
    foir: float
    debt_burden: float
    distress_flag: bool
    severity: str
    generated_at: datetime


class FederatedRunRequest(BaseModel):
    num_clients: int = Field(default=3, ge=2, le=20)
    num_rounds: int = Field(default=2, ge=1, le=20)
    local_epochs: int = Field(default=1, ge=1, le=10)


class FederatedRunResponse(BaseModel):
    run_id: str
    num_clients: int
    num_rounds: int
    accuracy: float | None = None
    loss: float | None = None


class AlertEvent(BaseModel):
    borrower_id: str
    severity: str
    message: str
    created_at: datetime
