from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Borrower(Base):
    __tablename__ = "borrowers"
    borrower_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    monthly_income: Mapped[float] = mapped_column(Float, nullable=False)
    existing_emi: Mapped[float] = mapped_column(Float, nullable=False)
    requested_loan_emi: Mapped[float] = mapped_column(Float, nullable=False)
    debt_outstanding: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class RiskSnapshot(Base):
    __tablename__ = "risk_snapshots"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    borrower_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    risk_probability: Mapped[float] = mapped_column(Float, nullable=False)
    foir: Mapped[float] = mapped_column(Float, nullable=False)
    debt_burden: Mapped[float] = mapped_column(Float, nullable=False)
    distress_flag: Mapped[bool] = mapped_column(Boolean, nullable=False)
    severity: Mapped[str] = mapped_column(String(16), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class Alert(Base):
    __tablename__ = "alerts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    borrower_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(16), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class FederatedRound(Base):
    __tablename__ = "federated_rounds"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    round_count: Mapped[int] = mapped_column(Integer, nullable=False)
    num_clients: Mapped[int] = mapped_column(Integer, nullable=False)
    accuracy: Mapped[float] = mapped_column(Float, nullable=True)
    loss: Mapped[float] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
