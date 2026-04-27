# AI Financial Risk Monitoring (Federated LSTM)

Production-grade research prototype for privacy-preserving EMI risk monitoring.

## Stack
- Python 3.11+
- FastAPI microservices
- PyTorch LSTM
- Flower federated learning
- PostgreSQL + Redis
- React + TypeScript
- Docker Compose

## Quickstart
1. Copy `.env.example` to `.env`.
2. Start services:
   - `docker compose up --build`
3. Trigger federated rounds:
   - `curl -X POST http://localhost:8002/fl/start -H "Content-Type: application/json" -d "{\"num_clients\":3,\"num_rounds\":2}"`
4. Open dashboard:
   - `http://localhost:5173`

## Services
- `api-gateway` (`:8000`): public ingestion and query API.
- `risk-engine` (`:8001`): feature engineering, scoring, persistence.
- `fl-orchestrator` (`:8002`): Flower simulation lifecycle + model metadata.
- `alert-service` (`:8003`): Redis-backed alert feed API.

## Repo Layout
- `services/`: FastAPI services + shared Python package.
- `ml/`: model, features, federated simulation utilities.
- `apps/web/`: React dashboard.
- `infra/`: database init and migration placeholders.
- `deploy/aws/`: optional AWS-ready reference artifacts.