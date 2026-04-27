import torch

from ml.models.lstm import RiskLSTM


def test_lstm_output_shape() -> None:
    model = RiskLSTM(input_size=4, hidden_size=8)
    x = torch.randn(5, 12, 4)
    out = model(x)
    assert out.shape == (5,)
