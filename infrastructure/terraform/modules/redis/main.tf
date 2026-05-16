# ============================================================
# ElastiCache Redis Module - PM Internship Engine
# ============================================================

variable "project_name" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "subnet_ids" {
  description = "Cache subnet IDs"
  type        = list(string)
}

variable "allowed_security_groups" {
  description = "Security group IDs allowed to connect"
  type        = list(string)
}

variable "node_type" {
  description = "ElastiCache node type"
  type        = string
  default     = "cache.t3.medium"
}

variable "num_cache_nodes" {
  description = "Number of cache nodes"
  type        = number
  default     = 1
}

variable "password" {
  description = "Redis AUTH password"
  type        = string
  sensitive   = true
}

variable "automatic_failover_enabled" {
  description = "Enable automatic failover (requires num_cache_nodes >= 2)"
  type        = bool
  default     = false
}

# ─────────────────────────────────────────────
# Subnet Group
# ─────────────────────────────────────────────

resource "aws_elasticache_subnet_group" "main" {
  name       = "${var.project_name}-${var.environment}-redis"
  subnet_ids = var.subnet_ids

  tags = {
    Name = "${var.project_name}-${var.environment}-redis-subnet"
  }
}

# ─────────────────────────────────────────────
# Security Group
# ─────────────────────────────────────────────

resource "aws_security_group" "redis" {
  name        = "${var.project_name}-${var.environment}-redis-sg"
  description = "ElastiCache Redis security group"
  vpc_id      = var.vpc_id

  ingress {
    description     = "Redis"
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = var.allowed_security_groups
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-redis-sg"
  }
}

# ─────────────────────────────────────────────
# Parameter Group
# ─────────────────────────────────────────────

resource "aws_elasticache_parameter_group" "main" {
  name   = "${var.project_name}-${var.environment}-redis7"
  family = "redis7"

  parameter {
    name  = "maxmemory-policy"
    value = "allkeys-lru"
  }

  parameter {
    name  = "notify-keyspace-events"
    value = "Ex"
  }

  parameter {
    name  = "timeout"
    value = "300"
  }

  parameter {
    name  = "tcp-keepalive"
    value = "300"
  }
}

# ─────────────────────────────────────────────
# Replication Group (Redis Cluster)
# ─────────────────────────────────────────────

resource "aws_elasticache_replication_group" "main" {
  replication_group_id = "${var.project_name}-${var.environment}"
  description          = "Redis cluster for ${var.project_name} ${var.environment}"

  node_type            = var.node_type
  num_cache_clusters   = var.automatic_failover_enabled ? max(var.num_cache_nodes, 2) : var.num_cache_nodes
  port                 = 6379

  parameter_group_name = aws_elasticache_parameter_group.main.name
  subnet_group_name    = aws_elasticache_subnet_group.main.name
  security_group_ids   = [aws_security_group.redis.id]

  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  auth_token                 = var.password

  automatic_failover_enabled = var.automatic_failover_enabled
  multi_az_enabled           = var.automatic_failover_enabled

  snapshot_retention_limit = var.environment == "production" ? 7 : 1
  snapshot_window          = "03:00-05:00"
  maintenance_window       = "sun:05:00-sun:07:00"

  auto_minor_version_upgrade = true

  apply_immediately = var.environment != "production"

  tags = {
    Name = "${var.project_name}-${var.environment}-redis"
  }
}

# ─────────────────────────────────────────────
# CloudWatch Alarms
# ─────────────────────────────────────────────

resource "aws_cloudwatch_metric_alarm" "memory" {
  alarm_name          = "${var.project_name}-${var.environment}-redis-memory-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "DatabaseMemoryUsagePercentage"
  namespace           = "AWS/ElastiCache"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "Redis memory usage above 80%"

  dimensions = {
    CacheClusterId = aws_elasticache_replication_group.main.id
  }
}

resource "aws_cloudwatch_metric_alarm" "cpu" {
  alarm_name          = "${var.project_name}-${var.environment}-redis-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "EngineCPUUtilization"
  namespace           = "AWS/ElastiCache"
  period              = 300
  statistic           = "Average"
  threshold           = 75
  alarm_description   = "Redis CPU usage above 75%"

  dimensions = {
    CacheClusterId = aws_elasticache_replication_group.main.id
  }
}

# ─────────────────────────────────────────────
# Outputs
# ─────────────────────────────────────────────

output "endpoint" {
  value = aws_elasticache_replication_group.main.primary_endpoint_address
}

output "reader_endpoint" {
  value = aws_elasticache_replication_group.main.reader_endpoint_address
}

output "port" {
  value = 6379
}

output "security_group_id" {
  value = aws_security_group.redis.id
}
