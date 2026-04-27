import torch
from torch import nn


class RiskLSTM(nn.Module):
    def __init__(self, input_size: int = 4, hidden_size: int = 32, num_layers: int = 1):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
        )
        self.fc = nn.Linear(hidden_size, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        output, _ = self.lstm(x)
        logits = self.fc(output[:, -1, :])
        return logits.squeeze(-1)
