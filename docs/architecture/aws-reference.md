# AWS Reference Architecture (Optional)

This repository remains local-first and cloud-agnostic for core runtime.

## Suggested AWS Mapping (when needed)
- ECS/Fargate: host FastAPI services and React web container.
- RDS PostgreSQL: managed structured storage.
- ElastiCache Redis: managed alert cache/pubsub.
- ECR: container image registry.
- ALB: ingress to `api-gateway`.
- CloudWatch: service logs/metrics.

## Non-Locking Principle
- Keep the same Docker images and environment contracts used in local compose.
- No cloud-only SDK calls in core scoring/federated code paths.
