output "web_url" {
  description = "Public URL for the web dashboard"
  value       = "http://${aws_lb.web.dns_name}"
}

output "api_url" {
  description = "Public URL for the API gateway"
  value       = "http://${aws_lb.api.dns_name}"
}

output "postgres_endpoint" {
  description = "RDS Postgres endpoint"
  value       = aws_db_instance.postgres.address
}

output "redis_endpoint" {
  description = "Redis endpoint"
  value       = aws_elasticache_cluster.redis.cache_nodes[0].address
}
