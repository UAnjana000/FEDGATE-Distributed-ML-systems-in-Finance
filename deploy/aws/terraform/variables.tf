variable "region" {
  description = "AWS region for deployment"
  type        = string
  default     = "ap-south-1"
}

variable "name_prefix" {
  description = "Name prefix for all cloud resources"
  type        = string
  default     = "fedgate"
}

variable "postgres_db" {
  description = "Postgres database name"
  type        = string
  default     = "fedrisk"
}

variable "postgres_user" {
  description = "Postgres username"
  type        = string
  default     = "fedrisk"
}

variable "postgres_password" {
  description = "Postgres password"
  type        = string
  sensitive   = true
}

variable "api_gateway_image" {
  description = "ECR image URI for api-gateway"
  type        = string
}

variable "risk_engine_image" {
  description = "ECR image URI for risk-engine"
  type        = string
}

variable "fl_orchestrator_image" {
  description = "ECR image URI for fl-orchestrator"
  type        = string
}

variable "alert_service_image" {
  description = "ECR image URI for alert-service"
  type        = string
}

variable "web_image" {
  description = "ECR image URI for web dashboard"
  type        = string
}

variable "tags" {
  description = "Additional tags to add to resources"
  type        = map(string)
  default     = {}
}
