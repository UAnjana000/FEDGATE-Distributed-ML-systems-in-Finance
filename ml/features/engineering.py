import numpy as np

from services.common.schemas import BorrowerIn


def compute_foir(monthly_income: float, total_emi: float) -> float:
    if monthly_income <= 0:
        return 1.0
    return float(total_emi / monthly_income)


def compute_debt_burden(monthly_income: float, debt_outstanding: float) -> float:
    if monthly_income <= 0:
        return 1.0
    return float(debt_outstanding / (monthly_income * 12.0))


def build_sequence_features(payload: BorrowerIn, seq_len: int = 12) -> np.ndarray:
    balances = payload.account_balance_series[-seq_len:]
    delays = payload.repayment_delay_series[-seq_len:]
    while len(balances) < seq_len:
        balances.insert(0, balances[0] if balances else 0.0)
    while len(delays) < seq_len:
        delays.insert(0, delays[0] if delays else 0.0)
    total_emi = payload.existing_emi + payload.requested_loan_emi
    foir = compute_foir(payload.monthly_income, total_emi)
    burden = compute_debt_burden(payload.monthly_income, payload.debt_outstanding)
    features = np.column_stack(
        [
            np.array(balances, dtype=np.float32),
            np.array(delays, dtype=np.float32),
            np.full(seq_len, foir, dtype=np.float32),
            np.full(seq_len, burden, dtype=np.float32),
        ]
    )
    return features
