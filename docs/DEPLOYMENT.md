# Deployment Guide

## Prerequisites

### Required Tools

| Tool | Version | Purpose |
|------|---------|---------|
| Docker | 24.0+ | Containerization |
| Docker Compose | 2.20+ | Multi-container orchestration |
| AWS CLI | 2.x | AWS resource management |
| Terraform | 1.5+ | Infrastructure as Code |
| Python | 3.12+ | Backend runtime |
| Node.js | 22+ | Frontend runtime |

### AWS Account Requirements

- AWS account with appropriate IAM permissions
- ECR repositories for backend and frontend images
- RDS PostgreSQL instance
- ElastiCache Redis cluster
- OpenSearch domain
- ECS Fargate cluster
- ALB (Application Load Balancer)
- S3 bucket for file uploads and backups

---

## Local Deployment

### Quick Start (Docker Compose)

```bash
# Clone the repository
git clone https://github.com/pm-internship/engine.git
cd engine

# Run one-command setup
./scripts/setup.sh

# Or manually:
cp .env.development .env
make dev
```

### Manual Local Setup

```bash
# 1. Start infrastructure services
cd infrastructure/docker
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d \
    postgres redis opensearch temporal temporal-ui

# 2. Wait for services to be ready
./scripts/health-check.sh

# 3. Set up Python environment
python3 -m venv backend/.venv
source backend/.venv/bin/activate
pip install -r backend/requirements.txt

# 4. Run database migrations
cd backend && alembic upgrade head && cd ..

# 5. Seed test data
python scripts/seed-data.py

# 6. Start application services
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d backend frontend
```

### Local Service URLs

| Service | URL | Credentials |
|---------|-----|-------------|
| Backend API | http://localhost:8000 | - |
| API Docs (Swagger) | http://localhost:8000/docs | - |
| Frontend | http://localhost:3000 | - |
| PgAdmin | http://localhost:5050 | admin@pm-internship.local / admin |
| Redis Commander | http://localhost:8082 | - |
| Temporal UI | http://localhost:8081 | - |
| OpenSearch | http://localhost:9200 | admin / admin |
| MailHog | http://localhost:8025 | - |

---

## Staging Deployment

Staging deployments are automated via GitHub Actions on pushes to the `develop` branch.

### GitHub Actions Workflow

**File:** `.github/workflows/deploy-staging.yml`

**Trigger:** Push to `develop` branch

**Steps:**
1. Run tests (backend + frontend)
2. Build Docker images
3. Push images to ECR
4. Update ECS task definitions
5. Deploy to staging ECS cluster
6. Run database migrations
7. Smoke test deployment

### Manual Staging Deploy

```bash
# Build and push images
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin <ACCOUNT_ID>.dkr.ecr.ap-south-1.amazonaws.com

docker build -t pm-internship-backend:staging -f infrastructure/docker/Dockerfile.backend --target production .
docker tag pm-internship-backend:staging <ACCOUNT_ID>.dkr.ecr.ap-south-1.amazonaws.com/pm-internship-backend:staging
docker push <ACCOUNT_ID>.dkr.ecr.ap-south-1.amazonaws.com/pm-internship-backend:staging

docker build -t pm-internship-frontend:staging -f infrastructure/docker/Dockerfile.frontend --target production .
docker tag pm-internship-frontend:staging <ACCOUNT_ID>.dkr.ecr.ap-south-1.amazonaws.com/pm-internship-frontend:staging
docker push <ACCOUNT_ID>.dkr.ecr.ap-south-1.amazonaws.com/pm-internship-frontend:staging

# Deploy via Terraform
cd infrastructure/terraform
terraform workspace select staging
terraform apply -var-file=staging.tfvars

# Run migrations
aws ecs run-task --cluster pm-staging --task-definition pm-migrate:latest --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx]}"
```

### Staging Environment Variables

Create `infrastructure/terraform/staging.tfvars`:

```hcl
environment        = "staging"
db_instance_class  = "db.t3.medium"
redis_node_type    = "cache.t3.micro"
ecs_cpu            = 512
ecs_memory         = 1024
desired_count      = 2
domain_name        = "staging.pm-internship.gov.in"
```

---

## Production Deployment

Production deployments require manual approval and are triggered on pushes to `main`.

### Pre-Deployment Checklist

- [ ] All staging tests passing
- [ ] Database migrations reviewed and tested
- [ ] Environment variables verified
- [ ] Rollback plan documented
- [ ] Team notified of deployment window
- [ ] Monitoring dashboards open

### GitHub Actions Workflow

**File:** `.github/workflows/deploy-production.yml`

**Trigger:** Push to `main` branch (with manual approval gate)

**Steps:**
1. Run full test suite
2. Build and tag Docker images with version
3. Push to ECR
4. Run database migrations (with backup)
5. Blue/Green ECS deployment
6. Health check verification
7. Route traffic to new version
8. Notify team of deployment status

### Manual Production Deploy

```bash
# 1. Create database backup
./scripts/backup.sh

# 2. Build production images
docker build -t pm-internship-backend:v1.2.3 -f infrastructure/docker/Dockerfile.backend --target production .
docker build -t pm-internship-frontend:v1.2.3 -f infrastructure/docker/Dockerfile.frontend --target production .

# 3. Push to ECR
docker tag pm-internship-backend:v1.2.3 <ACCOUNT_ID>.dkr.ecr.ap-south-1.amazonaws.com/pm-internship-backend:v1.2.3
docker push <ACCOUNT_ID>.dkr.ecr.ap-south-1.amazonaws.com/pm-internship-backend:v1.2.3

# 4. Deploy infrastructure
cd infrastructure/terraform
terraform workspace select production
terraform plan -var-file=production.tfvars -out=plan.tfplan
terraform apply plan.tfplan

# 5. Run migrations
aws ecs run-task --cluster pm-production --task-definition pm-migrate:latest ...

# 6. Update ECS service
aws ecs update-service --cluster pm-production --service pm-backend --task-definition pm-backend:v1.2.3 --force-new-deployment

# 7. Verify
./scripts/health-check.sh https://api.pm-internship.gov.in
```

### Production Environment Variables

Create `infrastructure/terraform/production.tfvars`:

```hcl
environment        = "production"
db_instance_class  = "db.r6g.large"
redis_node_type    = "cache.r6g.large"
ecs_cpu            = 1024
ecs_memory         = 2048
desired_count      = 3
domain_name        = "pm-internship.gov.in"
enable_waf         = true
enable_cdn         = true
backup_retention   = 30
```

---

## Environment Variables Reference

### Application

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `APP_NAME` | Application name | `PM Internship Allocation Engine` | No |
| `ENVIRONMENT` | Deployment environment | `development` | Yes |
| `SECRET_KEY` | JWT signing key (generate: `openssl rand -hex 64`) | `change-me` | **Yes** |
| `ALLOWED_ORIGINS` | CORS allowed origins (comma-separated) | `http://localhost:3000` | Yes |
| `LOG_LEVEL` | Logging level | `info` | No |
| `DEBUG` | Enable debug mode | `false` | No |

### Database

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | PostgreSQL connection URL | `postgresql+asyncpg://...` | **Yes** |
| `DB_POOL_SIZE` | Connection pool size | `20` | No |
| `DB_MAX_OVERFLOW` | Max overflow connections | `10` | No |
| `DB_POOL_TIMEOUT` | Pool checkout timeout (seconds) | `30` | No |
| `DB_POOL_RECYCLE` | Connection recycle time (seconds) | `1800` | No |

### Redis

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379/0` | **Yes** |
| `CACHE_TTL` | Default cache TTL (seconds) | `3600` | No |

### OpenSearch

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OPENSEARCH_URL` | OpenSearch endpoint | `http://localhost:9200` | Yes |
| `OPENSEARCH_USERNAME` | OpenSearch username | `admin` | Yes |
| `OPENSEARCH_PASSWORD` | OpenSearch password | - | **Yes** |

### Matching Algorithm

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `MATCHING_WEIGHT_SKILLS` | Skill matching weight | `0.30` | No |
| `MATCHING_WEIGHT_LOCATION` | Location matching weight | `0.15` | No |
| `MATCHING_WEIGHT_SECTOR` | Sector matching weight | `0.20` | No |
| `MATCHING_WEIGHT_QUALIFICATIONS` | Qualification matching weight | `0.15` | No |
| `MATCHING_WEIGHT_FAIRNESS` | Fairness matching weight | `0.20` | No |
| `MATCH_MIN_THRESHOLD` | Minimum match score threshold | `0.3` | No |

### Fairness Policy

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `FAIRNESS_ENABLED` | Enable fairness-aware allocation | `true` | No |
| `FAIRNESS_MIN_REPRESENTATION` | Min allocation % for underrepresented groups | `0.30` | No |
| `FAIRNESS_GEO_DIVERSITY_TARGET` | Geographic diversity target | `0.40` | No |
| `FAIRNESS_SES_BOOST` | Socioeconomic priority boost factor | `1.2` | No |

### AWS (Production)

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `AWS_REGION` | AWS region | `ap-south-1` | Yes |
| `AWS_ACCESS_KEY_ID` | AWS access key | - | Prod only |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | - | Prod only |
| `S3_BUCKET` | S3 bucket for uploads | - | Prod only |

### Frontend

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:8000` | Yes |
| `NEXT_PUBLIC_WS_URL` | WebSocket URL | `ws://localhost:8000` | No |
| `NEXT_PUBLIC_APP_NAME` | Application display name | `PM Internship Smart Allocation Engine` | No |

---

## Database Migration Guide

### Using Alembic

```bash
# Activate virtual environment
source backend/.venv/bin/activate

# Check current migration status
cd backend && alembic current

# View migration history
alembic history

# Create a new migration (auto-generate from model changes)
alembic revision --autogenerate -m "add_candidates_table"

# Apply all pending migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>

# Generate SQL without applying (for review)
alembic upgrade head --sql > migration.sql
```

### Migration Best Practices

1. **Always review auto-generated migrations** before applying
2. **Test migrations on staging** before production
3. **Create backups** before running migrations in production
4. **Use `--sql` flag** to review the generated SQL
5. **Never modify** an already-applied migration file
6. **Name migrations descriptively**: `add_index_on_candidates_state`

### Production Migration Process

```bash
# 1. Backup database
./scripts/backup.sh

# 2. Review migration SQL
cd backend && alembic upgrade head --sql

# 3. Apply migration
alembic upgrade head

# 4. Verify
alembic current
```

---

## Monitoring Setup

### Health Check Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Application health check |
| `GET /health/db` | Database connectivity |
| `GET /health/redis` | Redis connectivity |
| `GET /health/opensearch` | OpenSearch connectivity |

### Sentry Integration

```bash
# Set DSN in environment
SENTRY_DSN=https://xxx@sentry.io/yyy
```

Errors are automatically captured and reported to Sentry with:
- Request context (URL, method, headers)
- User context (ID, email, role)
- Stack traces
- Breadcrumbs (recent events)

### OpenTelemetry

Traces are exported to the configured OTLP endpoint:

```bash
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
```

### CloudWatch Logs

In production, logs are streamed to CloudWatch:

```bash
# View logs
aws logs tail /ecs/pm-backend --follow --region ap-south-1

# Search logs
aws logs filter-log-events \
  --log-group-name /ecs/pm-backend \
  --filter-pattern "ERROR" \
  --start-time 1705312800000
```

### Prometheus Metrics

Metrics are exposed on port 9090:

```bash
METRICS_PORT=9090
```

Key metrics:
- `http_requests_total` - Total HTTP requests by method/path/status
- `http_request_duration_seconds` - Request latency histogram
- `matching_pipeline_duration_seconds` - Matching pipeline execution time
- `allocation_cycle_duration_seconds` - Allocation cycle execution time
- `db_pool_connections` - Active database connections

---

## Troubleshooting

### Common Issues

#### Database Connection Refused

```
sqlalchemy.exc.OperationalError: connection refused
```

**Solution:**
1. Check PostgreSQL is running: `docker ps | grep postgres`
2. Verify `DATABASE_URL` in `.env`
3. Check connection pool exhaustion: `SELECT count(*) FROM pg_stat_activity;`
4. Restart if needed: `docker restart pm-postgres`

#### Migration Conflicts

```
alembic.util.exc.CommandError: Multiple head revisions
```

**Solution:**
```bash
# Merge heads
cd backend && alembic merge heads -m "merge conflicting migrations"
alembic upgrade head
```

#### Redis Connection Timeout

```
redis.exceptions.ConnectionError: Error connecting to Redis
```

**Solution:**
1. Check Redis is running: `docker ps | grep redis`
2. Verify `REDIS_URL` in `.env`
3. Check memory: `docker exec pm-redis redis-cli info memory`
4. Flush if needed: `docker exec pm-redis redis-cli flushall`

#### OpenSearch Cluster Red

```
opensearchpy.ConnectionError: Connection error
```

**Solution:**
1. Check cluster health: `curl http://localhost:9200/_cluster/health?pretty`
2. Check disk space: `curl http://localhost:9200/_cat/allocation?v`
3. Restart if needed: `docker restart pm-opensearch`

#### Out of Memory (ECS)

```
Task stopped reason: OutOfMemoryError
```

**Solution:**
1. Increase ECS task memory in Terraform: `ecs_memory = 4096`
2. Check for memory leaks in profiling
3. Reduce `DB_POOL_SIZE` if database connections consume too much memory

#### Frontend Build Failures

```
Error: Build failed with errors
```

**Solution:**
```bash
cd frontend
rm -rf .next node_modules
npm install
npm run build
```

#### JWT Token Expired

```
401 Unauthorized: Token has expired
```

**Solution:** Use the refresh token endpoint to obtain new tokens:
```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "<your_refresh_token>"}'
```

---

## Rollback Procedures

### Application Rollback (ECS)

```bash
# List recent task definitions
aws ecs list-task-definitions --family-prefix pm-backend --sort DESC --max-items 5

# Rollback to previous version
aws ecs update-service \
  --cluster pm-production \
  --service pm-backend \
  --task-definition pm-backend:<previous_revision>
```

### Database Rollback

```bash
# Rollback last migration
cd backend && alembic downgrade -1

# Or restore from backup
pg_restore -h <host> -U pm_admin -d pm_internship backup_20250115_140000.sql.gz
```

### Terraform Rollback

```bash
# Revert to previous state
cd infrastructure/terraform
terraform plan -var-file=production.tfvars -target=<resource>
terraform apply -var-file=production.tfvars
```
