# ============================================================
# Terraform Variables
# PM Internship Smart Allocation Engine
# ============================================================

# ─────────────────────────────────────────────
# General
# ─────────────────────────────────────────────

variable "project_name" {
  description = "Name of the project, used as prefix for all resources"
  type        = string
  default     = "pm-internship"
}

variable "environment" {
  description = "Deployment environment (development, staging, production)"
  type        = string
  validation {
    condition     = contains(["development", "staging", "production"], var.environment)
    error_message = "Environment must be one of: development, staging, production"
  }
}

variable "aws_region" {
  description = "AWS region for resource deployment"
  type        = string
  default     = "ap-south-1"
}

# ─────────────────────────────────────────────
# VPC
# ─────────────────────────────────────────────

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

# ─────────────────────────────────────────────
# Database (RDS PostgreSQL)
# ─────────────────────────────────────────────

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.medium"
}

variable "db_allocated_storage" {
  description = "Allocated storage in GB"
  type        = number
  default     = 20
}

variable "db_max_allocated_storage" {
  description = "Maximum allocated storage for autoscaling in GB"
  type        = number
  default     = 100
}

variable "db_name" {
  description = "Name of the PostgreSQL database"
  type        = string
  default     = "pm_internship"
}

variable "db_username" {
  description = "Master username for the database"
  type        = string
  default     = "pm_admin"
}

# ─────────────────────────────────────────────
# Cache (ElastiCache Redis)
# ─────────────────────────────────────────────

variable "redis_node_type" {
  description = "ElastiCache Redis node type"
  type        = string
  default     = "cache.t3.medium"
}

variable "redis_num_nodes" {
  description = "Number of Redis cache nodes"
  type        = number
  default     = 1
}

# ─────────────────────────────────────────────
# Search (OpenSearch)
# ─────────────────────────────────────────────

variable "opensearch_instance_type" {
  description = "OpenSearch instance type"
  type        = string
  default     = "r6g.large.search"
}

variable "opensearch_instance_count" {
  description = "Number of OpenSearch instances"
  type        = number
  default     = 2
}

variable "opensearch_volume_size" {
  description = "OpenSearch EBS volume size in GB"
  type        = number
  default     = 50
}

# ─────────────────────────────────────────────
# Backend (ECS Fargate)
# ─────────────────────────────────────────────

variable "backend_image" {
  description = "Docker image for the backend service"
  type        = string
}

variable "backend_cpu" {
  description = "Fargate task CPU units (256, 512, 1024, 2048, 4096)"
  type        = number
  default     = 1024
}

variable "backend_memory" {
  description = "Fargate task memory in MiB"
  type        = number
  default     = 2048
}

variable "backend_desired_count" {
  description = "Desired number of backend tasks"
  type        = number
  default     = 2
}

# ─────────────────────────────────────────────
# Frontend
# ─────────────────────────────────────────────

variable "frontend_domain" {
  description = "Custom domain for the frontend (leave empty for CloudFront default)"
  type        = string
  default     = ""
}

variable "api_domain_name" {
  description = "Domain name for API backend (for CloudFront origin)"
  type        = string
}

variable "acm_certificate_arn" {
  description = "ACM certificate ARN for HTTPS"
  type        = string
  default     = ""
}

# ─────────────────────────────────────────────
# Temporal
# ─────────────────────────────────────────────

variable "temporal_address" {
  description = "Temporal server address"
  type        = string
  default     = "temporal:7233"
}

# ─────────────────────────────────────────────
# Application
# ─────────────────────────────────────────────

variable "allowed_origins" {
  description = "CORS allowed origins"
  type        = string
  default     = "*"
}

variable "log_level" {
  description = "Application log level"
  type        = string
  default     = "info"
  validation {
    condition     = contains(["debug", "info", "warning", "error", "critical"], var.log_level)
    error_message = "Log level must be one of: debug, info, warning, error, critical"
  }
}

# ─────────────────────────────────────────────
# Security
# ─────────────────────────────────────────────

variable "enable_waf" {
  description = "Enable AWS WAF for CloudFront distribution"
  type        = bool
  default     = false
}

variable "waf_acl_arn" {
  description = "ARN of existing WAF Web ACL (if not creating one)"
  type        = string
  default     = ""
}

# ─────────────────────────────────────────────
# Monitoring
# ─────────────────────────────────────────────

variable "sns_alarm_topic_arn" {
  description = "SNS topic ARN for CloudWatch alarms"
  type        = string
  default     = ""
}
