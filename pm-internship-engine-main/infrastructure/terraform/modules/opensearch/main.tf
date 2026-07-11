# ============================================================
# OpenSearch Module - PM Internship Engine
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
  description = "Subnet IDs for OpenSearch"
  type        = list(string)
}

variable "allowed_security_groups" {
  description = "Security group IDs allowed to connect"
  type        = list(string)
}

variable "instance_type" {
  description = "OpenSearch instance type"
  type        = string
  default     = "r6g.large.search"
}

variable "instance_count" {
  description = "Number of data instances"
  type        = number
  default     = 2
}

variable "volume_size" {
  description = "EBS volume size in GB"
  type        = number
  default     = 50
}

variable "dedicated_master_enabled" {
  description = "Enable dedicated master nodes"
  type        = bool
  default     = false
}

# ─────────────────────────────────────────────
# Security Group
# ─────────────────────────────────────────────

resource "aws_security_group" "opensearch" {
  name        = "${var.project_name}-${var.environment}-opensearch-sg"
  description = "OpenSearch security group"
  vpc_id      = var.vpc_id

  ingress {
    description     = "HTTPS"
    from_port       = 443
    to_port         = 443
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
    Name = "${var.project_name}-${var.environment}-opensearch-sg"
  }
}

# ─────────────────────────────────────────────
# OpenSearch Domain
# ─────────────────────────────────────────────

resource "aws_opensearch_domain" "main" {
  domain_name    = "${var.project_name}-${var.environment}"
  engine_version = "OpenSearch_2.11"

  cluster_config {
    instance_type          = var.instance_type
    instance_count         = var.instance_count
    zone_awareness_enabled = var.instance_count > 1

    dedicated_master_enabled = var.dedicated_master_enabled
    dedicated_master_type    = var.dedicated_master_enabled ? "r6g.large.search" : null
    dedicated_master_count   = var.dedicated_master_enabled ? 3 : null

    warm_enabled = false
  }

  vpc_options {
    subnet_ids         = var.instance_count > 1 ? var.subnet_ids : [var.subnet_ids[0]]
    security_group_ids = [aws_security_group.opensearch.id]
  }

  ebs_options {
    ebs_enabled = true
    volume_type = "gp3"
    volume_size = var.volume_size
    iops        = 3000
    throughput  = 125
  }

  encrypt_at_rest {
    enabled = true
  }

  node_to_node_encryption {
    enabled = true
  }

  domain_endpoint_options {
    enforce_https       = true
    tls_security_policy = "Policy-Min-TLS-1-2-2019-07"
  }

  advanced_security_options {
    enabled                        = true
    anonymous_auth_enabled         = false
    internal_user_database_enabled = true

    master_user_options {
      master_user_name     = "admin"
      master_user_password = var.master_password
    }
  }

  log_publishing_options {
    cloudwatch_log_group_arn = aws_cloudwatch_log_group.opensearch_index_slow.arn
    log_type                 = "INDEX_SLOW_LOGS"
  }

  log_publishing_options {
    cloudwatch_log_group_arn = aws_cloudwatch_log_group.opensearch_search_slow.arn
    log_type                 = "SEARCH_SLOW_LOGS"
  }

  log_publishing_options {
    cloudwatch_log_group_arn = aws_cloudwatch_log_group.opensearch_application.arn
    log_type                 = "ES_APPLICATION_LOGS"
  }

  snapshot_options {
    automated_snapshot_start_hour = 3
  }

  tags = {
    Name = "${var.project_name}-${var.environment}"
  }
}

variable "master_password" {
  description = "Master password for OpenSearch"
  type        = string
  sensitive   = true
  default     = "Ch@ngeme1!"
}

# ─────────────────────────────────────────────
# CloudWatch Log Groups
# ─────────────────────────────────────────────

resource "aws_cloudwatch_log_group" "opensearch_index_slow" {
  name              = "/aws/opensearch/${var.project_name}-${var.environment}/index-slow"
  retention_in_days = 30
}

resource "aws_cloudwatch_log_group" "opensearch_search_slow" {
  name              = "/aws/opensearch/${var.project_name}-${var.environment}/search-slow"
  retention_in_days = 30
}

resource "aws_cloudwatch_log_group" "opensearch_application" {
  name              = "/aws/opensearch/${var.project_name}-${var.environment}/application"
  retention_in_days = 30
}

# ─────────────────────────────────────────────
# Access Policy
# ─────────────────────────────────────────────

resource "aws_opensearch_domain_policy" "main" {
  domain_name = aws_opensearch_domain.main.domain_name

  access_policies = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect    = "Allow"
        Principal = { AWS = "*" }
        Action    = "es:*"
        Resource  = "${aws_opensearch_domain.main.arn}/*"
        Condition = {
          IpAddress = {
            "aws:SourceIp" = ["10.0.0.0/8"]
          }
        }
      }
    ]
  })
}

# ─────────────────────────────────────────────
# Outputs
# ─────────────────────────────────────────────

output "endpoint" {
  value = aws_opensearch_domain.main.endpoint
}

output "dashboard_endpoint" {
  value = aws_opensearch_domain.main.dashboard_endpoint
}

output "domain_arn" {
  value = aws_opensearch_domain.main.arn
}

output "domain_name" {
  value = aws_opensearch_domain.main.domain_name
}

output "security_group_id" {
  value = aws_security_group.opensearch.id
}
