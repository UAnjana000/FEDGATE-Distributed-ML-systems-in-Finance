from ml.features.engineering import compute_debt_burden, compute_foir


def test_foir_computation() -> None:
    assert round(compute_foir(50000, 20000), 2) == 0.4


def test_debt_burden_computation() -> None:
    assert round(compute_debt_burden(50000, 300000), 2) == 0.5
