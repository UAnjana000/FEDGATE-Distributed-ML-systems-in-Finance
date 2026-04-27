# AWS Deployment Skeleton (Placeholder)

This folder is intentionally lightweight and non-binding.

Expected future structure:
- `terraform/` or `cdk/` for infra provisioning.
- `ecs-task-defs/` for service task specs.
- `env/` for stage-specific non-secret config templates.

Core application logic must stay portable and runnable via `docker compose` locally.
