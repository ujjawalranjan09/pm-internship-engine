# ============================================================
# Terraform - Main Configuration
# PM Internship Smart Allocation Engine
# AWS Infrastructure
# ============================================================

terraform {
  required_version = ">= 1.7.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.40"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }

  backend "s3" {
    bucket         = "pm-internship-terraform-state"
    key            = "infrastructure/terraform.tfstate"
    region         = "ap-south-1"
    encrypt        = true
    dynamodb_table = "pm-internship-terraform-locks"
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "pm-internship-engine"
      Environment = var.environment
      ManagedBy   = "terraform"
      Team        = "pm-allocation"
    }
  }
}

# ─────────────────────────────────────────────
# Data Sources
# ─────────────────────────────────────────────

data "aws_caller_identity" "current" {}
data "aws_availability_zones" "available" {
  state = "available"
}

# ─────────────────────────────────────────────
# Random Resources
# ─────────────────────────────────────────────

resource "random_password" "db_password" {
  length  = 32
  special = false
}

resource "random_password" "redis_password" {
  length  = 32
  special = false
}

resource "random_password" "secret_key" {
  length  = 64
  special = true
}

# ─────────────────────────────────────────────
# VPC Module
# ─────────────────────────────────────────────

module "vpc" {
  source = "./modules/vpc"

  project_name       = var.project_name
  environment        = var.environment
  vpc_cidr           = var.vpc_cidr
  availability_zones = slice(data.aws_availability_zones.available.names, 0, 3)
  single_nat_gateway = var.environment != "production"
}

# ─────────────────────────────────────────────
# RDS PostgreSQL Module
# ─────────────────────────────────────────────

module "rds" {
  source = "./modules/rds"

  project_name       = var.project_name
  environment        = var.environment
  vpc_id             = module.vpc.vpc_id
  subnet_ids         = module.vpc.database_subnet_ids
  allowed_security_groups = [module.ecs.service_security_group_id]

  instance_class     = var.db_instance_class
  allocated_storage  = var.db_allocated_storage
  max_allocated_storage = var.db_max_allocated_storage
  db_name            = var.db_name
  db_username        = var.db_username
  db_password        = random_password.db_password.result
  multi_az           = var.environment == "production"
  backup_retention_period = var.environment == "production" ? 30 : 7
  deletion_protection = var.environment == "production"
}

# ─────────────────────────────────────────────
# ElastiCache Redis Module
# ─────────────────────────────────────────────

module "redis" {
  source = "./modules/redis"

  project_name       = var.project_name
  environment        = var.environment
  vpc_id             = module.vpc.vpc_id
  subnet_ids         = module.vpc.cache_subnet_ids
  allowed_security_groups = [module.ecs.service_security_group_id]

  node_type          = var.redis_node_type
  num_cache_nodes    = var.redis_num_nodes
  password           = random_password.redis_password.result
  automatic_failover_enabled = var.environment == "production"
}

# ─────────────────────────────────────────────
# OpenSearch Module
# ─────────────────────────────────────────────

module "opensearch" {
  source = "./modules/opensearch"

  project_name       = var.project_name
  environment        = var.environment
  vpc_id             = module.vpc.vpc_id
  subnet_ids         = slice(module.vpc.private_subnet_ids, 0, 2)
  allowed_security_groups = [module.ecs.service_security_group_id]

  instance_type      = var.opensearch_instance_type
  instance_count     = var.opensearch_instance_count
  volume_size        = var.opensearch_volume_size
  dedicated_master_enabled = var.environment == "production"
}

# ─────────────────────────────────────────────
# ECS Fargate Module (Backend)
# ─────────────────────────────────────────────

module "ecs" {
  source = "./modules/ecs"

  project_name       = var.project_name
  environment        = var.environment
  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
  public_subnet_ids  = module.vpc.public_subnet_ids

  container_image    = var.backend_image
  container_port     = 8000
  cpu                = var.backend_cpu
  memory             = var.backend_memory
  desired_count      = var.backend_desired_count

  health_check_path  = "/health"
  health_check_interval = 30

  environment_variables = {
    DATABASE_URL     = "postgresql+asyncpg://${var.db_username}:${random_password.db_password.result}@${module.rds.endpoint}:5432/${var.db_name}"
    REDIS_URL        = "redis://:${random_password.redis_password.result}@${module.redis.endpoint}:6379/0"
    OPENSEARCH_URL   = "https://${module.opensearch.endpoint}"
    TEMPORAL_ADDRESS = var.temporal_address
    ALLOWED_ORIGINS  = var.allowed_origins
    LOG_LEVEL        = var.log_level
    ENVIRONMENT      = var.environment
  }

  secrets = {
    SECRET_KEY = aws_secretsmanager_secret.app_secrets.arn
  }

  log_retention_days = var.environment == "production" ? 90 : 30
}

# ─────────────────────────────────────────────
# S3 + CloudFront (Frontend)
# ─────────────────────────────────────────────

resource "aws_s3_bucket" "frontend" {
  bucket = "${var.project_name}-frontend-${var.environment}"
}

resource "aws_s3_bucket_versioning" "frontend" {
  bucket = aws_s3_bucket.frontend.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "frontend" {
  bucket = aws_s3_bucket.frontend.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "frontend" {
  bucket                  = aws_s3_bucket.frontend.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_cloudfront_origin_access_identity" "frontend" {
  comment = "OAI for ${var.project_name} frontend ${var.environment}"
}

resource "aws_s3_bucket_policy" "frontend" {
  bucket = aws_s3_bucket.frontend.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "AllowCloudFrontAccess"
        Effect    = "Allow"
        Principal = {
          AWS = aws_cloudfront_origin_access_identity.frontend.iam_arn
        }
        Action   = "s3:GetObject"
        Resource = "${aws_s3_bucket.frontend.arn}/*"
      }
    ]
  })
}

resource "aws_cloudfront_distribution" "frontend" {
  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"
  price_class         = var.environment == "production" ? "PriceClass_All" : "PriceClass_100"
  aliases             = var.frontend_domain != "" ? [var.frontend_domain] : []
  web_acl_id          = var.waf_acl_arn

  origin {
    domain_name = aws_s3_bucket.frontend.bucket_regional_domain_name
    origin_id   = "S3-${aws_s3_bucket.frontend.id}"

    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.frontend.cloudfront_access_identity_path
    }
  }

  # API proxy origin
  origin {
    domain_name = var.api_domain_name
    origin_id   = "API-Backend"

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "https-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }

  default_cache_behavior {
    allowed_methods        = ["GET", "HEAD", "OPTIONS"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "S3-${aws_s3_bucket.frontend.id}"
    viewer_protocol_policy = "redirect-to-https"
    compress               = true

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }

    min_ttl     = 0
    default_ttl = 3600
    max_ttl     = 86400
  }

  # API route behavior
  ordered_cache_behavior {
    path_pattern           = "/api/*"
    allowed_methods        = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "API-Backend"
    viewer_protocol_policy = "https-only"

    forwarded_values {
      query_string = true
      headers      = ["Authorization", "Content-Type", "Accept"]
      cookies {
        forward = "all"
      }
    }

    min_ttl     = 0
    default_ttl = 0
    max_ttl     = 0
  }

  # SPA fallback
  custom_error_response {
    error_code         = 403
    response_code      = 200
    response_page_path = "/index.html"
  }

  custom_error_response {
    error_code         = 404
    response_code      = 200
    response_page_path = "/index.html"
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    acm_certificate_arn      = var.acm_certificate_arn
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1.2_2021"
  }
}

# ─────────────────────────────────────────────
# Secrets Manager
# ─────────────────────────────────────────────

resource "aws_secretsmanager_secret" "app_secrets" {
  name                    = "${var.project_name}/${var.environment}/app-secrets"
  description             = "Application secrets for PM Internship Engine"
  recovery_window_in_days = var.environment == "production" ? 30 : 0
}

resource "aws_secretsmanager_secret_version" "app_secrets" {
  secret_id = aws_secretsmanager_secret.app_secrets.id
  secret_string = jsonencode({
    SECRET_KEY    = random_password.secret_key.result
    DB_PASSWORD   = random_password.db_password.result
    REDIS_PASSWORD = random_password.redis_password.result
  })
}

# ─────────────────────────────────────────────
# WAF (optional, for production)
# ─────────────────────────────────────────────

resource "aws_wafv2_web_acl" "main" {
  count = var.enable_waf ? 1 : 0

  name        = "${var.project_name}-${var.environment}-waf"
  description = "WAF for PM Internship Engine"
  scope       = "CLOUDFRONT"

  default_action {
    allow {}
  }

  rule {
    name     = "RateLimit"
    priority = 1

    override_action {
      none {}
    }

    statement {
      rate_based_statement {
        limit              = 2000
        aggregate_key_type = "IP"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "${var.project_name}-rate-limit"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "AWSManagedRulesCommonRuleSet"
    priority = 2

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesCommonRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "${var.project_name}-common-rules"
      sampled_requests_enabled   = true
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "${var.project_name}-waf"
    sampled_requests_enabled   = true
  }
}

# ─────────────────────────────────────────────
# CloudWatch Alarms
# ─────────────────────────────────────────────

resource "aws_cloudwatch_metric_alarm" "backend_cpu_high" {
  alarm_name          = "${var.project_name}-${var.environment}-backend-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "Backend CPU utilization > 80% for 15 minutes"
  alarm_actions       = var.sns_alarm_topic_arn != "" ? [var.sns_alarm_topic_arn] : []

  dimensions = {
    ClusterName = module.ecs.cluster_name
    ServiceName = module.ecs.service_name
  }
}

resource "aws_cloudwatch_metric_alarm" "backend_memory_high" {
  alarm_name          = "${var.project_name}-${var.environment}-backend-memory-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "MemoryUtilization"
  namespace           = "AWS/ECS"
  period              = 300
  statistic           = "Average"
  threshold           = 85
  alarm_description   = "Backend memory utilization > 85% for 15 minutes"
  alarm_actions       = var.sns_alarm_topic_arn != "" ? [var.sns_alarm_topic_arn] : []

  dimensions = {
    ClusterName = module.ecs.cluster_name
    ServiceName = module.ecs.service_name
  }
}

resource "aws_cloudwatch_metric_alarm" "rds_cpu_high" {
  alarm_name          = "${var.project_name}-${var.environment}-rds-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "RDS CPU utilization > 80% for 15 minutes"
  alarm_actions       = var.sns_alarm_topic_arn != "" ? [var.sns_alarm_topic_arn] : []

  dimensions = {
    DBInstanceIdentifier = module.rds.instance_id
  }
}
