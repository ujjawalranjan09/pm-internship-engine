# ============================================================
# Terraform Outputs
# PM Internship Smart Allocation Engine
# ============================================================

# ─────────────────────────────────────────────
# VPC
# ─────────────────────────────────────────────

output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "vpc_cidr" {
  description = "VPC CIDR block"
  value       = module.vpc.vpc_cidr
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = module.vpc.public_subnet_ids
}

output "private_subnet_ids" {
  description = "Private subnet IDs"
  value       = module.vpc.private_subnet_ids
}

output "database_subnet_ids" {
  description = "Database subnet IDs"
  value       = module.vpc.database_subnet_ids
}

# ─────────────────────────────────────────────
# ECS
# ─────────────────────────────────────────────

output "ecs_cluster_name" {
  description = "ECS cluster name"
  value       = module.ecs.cluster_name
}

output "ecs_service_name" {
  description = "ECS service name"
  value       = module.ecs.service_name
}

output "ecs_task_definition_arn" {
  description = "ECS task definition ARN"
  value       = module.ecs.task_definition_arn
}

output "backend_security_group_id" {
  description = "Backend service security group ID"
  value       = module.ecs.service_security_group_id
}

output "alb_dns_name" {
  description = "Application Load Balancer DNS name"
  value       = module.ecs.alb_dns_name
}

output "backend_url" {
  description = "Backend API URL"
  value       = "https://${module.ecs.alb_dns_name}"
}

# ─────────────────────────────────────────────
# RDS PostgreSQL
# ─────────────────────────────────────────────

output "rds_endpoint" {
  description = "RDS PostgreSQL endpoint"
  value       = module.rds.endpoint
}

output "rds_port" {
  description = "RDS PostgreSQL port"
  value       = module.rds.port
}

output "rds_instance_id" {
  description = "RDS instance ID"
  value       = module.rds.instance_id
}

output "database_url" {
  description = "Full database connection URL"
  value       = "postgresql://${var.db_username}:<redacted>@${module.rds.endpoint}:5432/${var.db_name}"
  sensitive   = false
}

# ─────────────────────────────────────────────
# ElastiCache Redis
# ─────────────────────────────────────────────

output "redis_endpoint" {
  description = "ElastiCache Redis endpoint"
  value       = module.redis.endpoint
}

output "redis_port" {
  description = "ElastiCache Redis port"
  value       = module.redis.port
}

# ─────────────────────────────────────────────
# OpenSearch
# ─────────────────────────────────────────────

output "opensearch_endpoint" {
  description = "OpenSearch domain endpoint"
  value       = module.opensearch.endpoint
}

output "opensearch_dashboard_endpoint" {
  description = "OpenSearch Dashboards endpoint"
  value       = module.opensearch.dashboard_endpoint
}

# ─────────────────────────────────────────────
# Frontend (S3 + CloudFront)
# ─────────────────────────────────────────────

output "frontend_s3_bucket" {
  description = "S3 bucket name for frontend assets"
  value       = aws_s3_bucket.frontend.id
}

output "cloudfront_distribution_id" {
  description = "CloudFront distribution ID"
  value       = aws_cloudfront_distribution.frontend.id
}

output "cloudfront_domain_name" {
  description = "CloudFront distribution domain name"
  value       = aws_cloudfront_distribution.frontend.domain_name
}

output "frontend_url" {
  description = "Frontend URL"
  value       = var.frontend_domain != "" ? "https://${var.frontend_domain}" : "https://${aws_cloudfront_distribution.frontend.domain_name}"
}

# ─────────────────────────────────────────────
# Secrets
# ─────────────────────────────────────────────

output "secrets_manager_arn" {
  description = "Secrets Manager secret ARN"
  value       = aws_secretsmanager_secret.app_secrets.arn
}

# ─────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────

output "deployment_summary" {
  description = "Deployment summary"
  value = {
    environment = var.environment
    region      = var.aws_region
    backend_url = "https://${module.ecs.alb_dns_name}"
    frontend_url = var.frontend_domain != "" ? "https://${var.frontend_domain}" : "https://${aws_cloudfront_distribution.frontend.domain_name}"
    database    = module.rds.endpoint
    cache       = module.redis.endpoint
    search      = module.opensearch.endpoint
  }
}
