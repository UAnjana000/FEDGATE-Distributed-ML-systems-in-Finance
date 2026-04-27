from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from ml.federated.simulation import run_federated_simulation
from services.common.config import settings
from services.common.logging import configure_logging
from services.common.models import Base, FederatedRound
from services.common.schemas import FederatedRunRequest, FederatedRunResponse
from services.common.storage import engine, get_db

configure_logging("fl-orchestrator")
app = FastAPI(title="FL Orchestrator", version="0.1.0")


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "fl-orchestrator"}


@app.post("/fl/start", response_model=FederatedRunResponse)
async def start_federated_run(
    req: FederatedRunRequest,
    db: Session = Depends(get_db),
) -> FederatedRunResponse:
    result = run_federated_simulation(
        num_clients=req.num_clients,
        num_rounds=req.num_rounds,
        local_epochs=req.local_epochs,
        model_dir=settings.model_dir,
    )
    db.add(
        FederatedRound(
            run_id=str(result["run_id"]),
            round_count=req.num_rounds,
            num_clients=req.num_clients,
            accuracy=float(result["accuracy"]) if result["accuracy"] is not None else None,
            loss=float(result["loss"]) if result["loss"] is not None else None,
        )
    )
    db.commit()
    return FederatedRunResponse(
        run_id=str(result["run_id"]),
        num_clients=req.num_clients,
        num_rounds=req.num_rounds,
        accuracy=float(result["accuracy"]) if result["accuracy"] is not None else None,
        loss=float(result["loss"]) if result["loss"] is not None else None,
    )
