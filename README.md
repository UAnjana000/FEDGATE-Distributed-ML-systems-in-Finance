# AI Financial Risk Monitoring (FEDGATE)

Production-style research platform for privacy-preserving borrower risk monitoring with federated learning.

It combines:
- A microservices backend for scoring, orchestration, and alerts
- LSTM-based risk estimation with rule-based credit decision support
- A React dashboard for operations and monitoring
- Local Docker workflows and full AWS deployment automation

## What This Project Solves

This system is designed to:
- Detect early borrower distress using financial behavior patterns
- Simulate federated learning rounds for distributed model updates
- Serve real-time risk and alert data to a web dashboard
- Run reproducibly in local development and cloud production-style environments

## Core Architecture

### Application Services
- `api-gateway` (`:8000`): Public API entrypoint and service aggregator
- `risk-engine` (`:8001`): Risk scoring, FOIR/debt-burden logic, persistence, alert publishing
- `fl-orchestrator` (`:8002`): Federated simulation lifecycle and run metadata
- `alert-service` (`:8003`): Alert feed retrieval from Redis
- `web` (`:5173`): Dashboard UI for analysts and operators

### Data + Messaging
- PostgreSQL: borrower/snapshot/FL run persistence
- Redis: alert list and pub/sub style alert channel

## AWS Architecture (Deployed Stack)

The AWS deployment provisions and wires these components:

- **Networking**
  - VPC with 2 public subnets (multi-AZ)
  - Internet Gateway + public route table
  - Security groups for ALB, ECS, RDS, and Redis

- **Compute**
  - ECS Fargate cluster running all app services
  - Cloud Map service discovery for internal service-to-service DNS

- **Ingress**
  - API ALB (public) -> `api-gateway` ECS service
  - Web ALB (public) -> `web` ECS service

- **Stateful dependencies**
  - Amazon RDS PostgreSQL
  - Amazon ElastiCache Redis

- **Operations**
  - CloudWatch log groups per service
  - Terraform-managed infrastructure and service rollouts

### Request Flow in AWS
1. Browser calls Web ALB (`web` service).
2. Frontend calls API ALB (`api-gateway`).
3. API gateway routes requests to `risk-engine`, `fl-orchestrator`, and `alert-service` over Cloud Map DNS.
4. `risk-engine` stores snapshots in RDS and publishes alerts to Redis.
5. `alert-service` reads alerts from Redis for dashboard consumption.

## Tech Stack

- Python 3.11+
- FastAPI + Uvicorn
- SQLAlchemy + Psycopg
- Redis client
- PyTorch (LSTM)
- Flower (federated simulation)
- React + TypeScript + Vite
- Docker / Docker Compose
- Terraform + AWS CLI

## Requirements

### System Requirements
- Docker Desktop (or Docker Engine)
- Node.js 20+ (for local frontend workflows)
- Python 3.11+
- AWS CLI v2 (for cloud deployment)
- Terraform 1.6+ (1.14+ recommended)

### Python Dependencies

This repo now includes:
- `requirements.txt` (runtime dependencies)
- `requirements-dev.txt` (runtime + dev tooling)

You can install with:

```bash
pip install -r requirements.txt
```

For development:

```bash
pip install -r requirements-dev.txt
```

## Local Development (Docker)

1. Copy env file:
   - `cp .env.example .env`
2. Start all services:
   - `docker compose up --build`
3. Open dashboard:
   - `http://localhost:5173`
4. Check API:
   - `http://localhost:8000/health`
   - `http://localhost:8000/docs`
5. Trigger sample actions:
   - Seed borrowers: `POST /borrowers/seed`
   - Start FL rounds: `POST /federated/start`

## Cloud Deployment (AWS)

From repository root:

```powershell
.\deploy\aws\deploy.ps1 -Region ap-south-1 -NamePrefix fedgate -PostgresPassword "<strong-password>"
```

### Deployment Prerequisites
- `aws configure` already completed
- IAM principal with permissions for:
  - ECR, ECS, EC2 (VPC/networking), ELBv2
  - RDS, ElastiCache, CloudWatch Logs
  - IAM role creation/attachment for ECS task execution
  - Service discovery (Cloud Map)

### Deployment Outputs
On success, script prints:
- `Web URL`
- `API URL`
- Postgres and Redis endpoints (Terraform outputs)

### Destroy Cloud Resources

```powershell
terraform -chdir="deploy/aws/terraform" destroy -auto-approve
```

## API Endpoints (Gateway)

- `GET /` - API gateway status
- `GET /health` - health check
- `GET /docs` - Swagger UI
- `POST /borrowers/score` - score borrower risk
- `GET /borrowers/snapshots` - latest scored snapshots
- `GET /alerts` - alert feed
- `POST /borrowers/seed` - seed sample borrowers
- `POST /federated/start` - run federated simulation

## Repository Layout

- `services/`: FastAPI services and shared modules
- `ml/`: feature engineering, model logic, FL simulation code
- `apps/web/`: React dashboard app
- `infra/`: local DB init/migration scaffolding
- `deploy/aws/`: Terraform and deployment automation
- `data/`: sample datasets and artifacts

## Notes

- Terraform state is currently local (`deploy/aws/terraform`) unless you configure a remote backend.
- Re-run deployment script after application code changes to publish new images.
- If ALB returns `503`, check ECS service/task health and target group health first.