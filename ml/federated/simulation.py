import uuid
from pathlib import Path

import flwr as fl
import numpy as np
import torch

from ml.models.lstm import RiskLSTM
from ml.models.training import evaluate, train_epoch


def _get_model_parameters(model: RiskLSTM) -> list[np.ndarray]:
    return [val.cpu().numpy() for _, val in model.state_dict().items()]


def _set_model_parameters(model: RiskLSTM, parameters: list[np.ndarray]) -> None:
    params_dict = zip(model.state_dict().keys(), parameters, strict=False)
    state_dict = {k: torch.tensor(v) for k, v in params_dict}
    model.load_state_dict(state_dict, strict=True)


def _make_dataset(seed: int, samples: int = 64, seq_len: int = 12) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    x = rng.normal(size=(samples, seq_len, 4)).astype(np.float32)
    risk_signal = x[:, :, 1].mean(axis=1) + 0.4 * x[:, :, 2].mean(axis=1)
    y = (risk_signal > 0.0).astype(np.float32)
    return x, y


class FederatedClient(fl.client.NumPyClient):
    def __init__(self, cid: int, local_epochs: int):
        self.cid = cid
        self.local_epochs = local_epochs
        self.model = RiskLSTM()
        self.x_train, self.y_train = _make_dataset(seed=100 + cid)
        self.x_eval, self.y_eval = _make_dataset(seed=200 + cid, samples=32)

    def get_parameters(self, config):  # type: ignore[override]
        return _get_model_parameters(self.model)

    def fit(self, parameters, config):  # type: ignore[override]
        _set_model_parameters(self.model, parameters)
        for _ in range(self.local_epochs):
            train_epoch(self.model, self.x_train, self.y_train)
        return _get_model_parameters(self.model), len(self.x_train), {}

    def evaluate(self, parameters, config):  # type: ignore[override]
        _set_model_parameters(self.model, parameters)
        loss, acc = evaluate(self.model, self.x_eval, self.y_eval)
        return float(loss), len(self.x_eval), {"accuracy": float(acc)}


def run_federated_simulation(
    num_clients: int,
    num_rounds: int,
    local_epochs: int,
    model_dir: str,
) -> dict[str, float | str | int | None]:
    run_id = str(uuid.uuid4())
    strategy = fl.server.strategy.FedAvg(
        fraction_fit=1.0,
        fraction_evaluate=1.0,
        min_fit_clients=num_clients,
        min_evaluate_clients=num_clients,
        min_available_clients=num_clients,
    )
    history = fl.simulation.start_simulation(
        client_fn=lambda cid: FederatedClient(int(cid), local_epochs),  # type: ignore[arg-type]
        num_clients=num_clients,
        config=fl.server.ServerConfig(num_rounds=num_rounds),
        strategy=strategy,
        client_resources={"num_cpus": 1},
    )
    distributed_loss = history.losses_distributed[-1][1] if history.losses_distributed else None
    accuracy = None
    if "accuracy" in history.metrics_distributed and history.metrics_distributed["accuracy"]:
        accuracy = history.metrics_distributed["accuracy"][-1][1]

    artifact_dir = Path(model_dir)
    artifact_dir.mkdir(parents=True, exist_ok=True)
    model_path = artifact_dir / f"fl_model_{run_id}.pt"
    torch.save(RiskLSTM().state_dict(), model_path)

    return {
        "run_id": run_id,
        "num_clients": num_clients,
        "num_rounds": num_rounds,
        "loss": distributed_loss,
        "accuracy": accuracy,
        "artifact_path": str(model_path),
    }
