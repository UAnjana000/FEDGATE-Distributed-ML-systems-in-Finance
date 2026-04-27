# AWS Deployment

This folder now contains a complete deploy flow for AWS:
- Builds and pushes all service images to ECR.
- Provisions VPC, ECS Fargate, ALB, RDS Postgres, and ElastiCache Redis with Terraform.
- Deploys backend first, then rebuilds the web app with the live API URL.

## Prerequisites
- Docker running locally
- AWS CLI configured (`aws configure`)
- Terraform installed
- IAM user/role with permissions for ECR, ECS, EC2 networking, ELB, CloudWatch Logs, RDS, ElastiCache, IAM (task roles), and Cloud Map

## Deploy
From repository root:

```powershell
.\deploy\aws\deploy.ps1 -Region ap-south-1 -NamePrefix fedgate -PostgresPassword "<strong-password>"
```

After completion, the script prints:
- Public web URL
- Public API URL

## Notes
- Terraform state is local in `deploy/aws/terraform` by default.
- To tear down the stack:
  1. Go to `deploy/aws/terraform`
  2. Run `terraform destroy -auto-approve`
- If you change app code, rerun `deploy.ps1` to rebuild and redeploy.
