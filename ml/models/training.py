import numpy as np
import torch
from torch import nn, optim


def train_epoch(
    model: torch.nn.Module,
    x_train: np.ndarray,
    y_train: np.ndarray,
    lr: float = 1e-3,
) -> float:
    model.train()
    criterion = nn.BCEWithLogitsLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)
    x = torch.tensor(x_train, dtype=torch.float32)
    y = torch.tensor(y_train, dtype=torch.float32)
    optimizer.zero_grad()
    logits = model(x)
    loss = criterion(logits, y)
    loss.backward()
    optimizer.step()
    return float(loss.item())


def evaluate(model: torch.nn.Module, x_eval: np.ndarray, y_eval: np.ndarray) -> tuple[float, float]:
    model.eval()
    criterion = nn.BCEWithLogitsLoss()
    with torch.no_grad():
        x = torch.tensor(x_eval, dtype=torch.float32)
        y = torch.tensor(y_eval, dtype=torch.float32)
        logits = model(x)
        loss = float(criterion(logits, y).item())
        probs = torch.sigmoid(logits)
        preds = (probs >= 0.5).float()
        acc = float((preds == y).float().mean().item())
    return loss, acc
