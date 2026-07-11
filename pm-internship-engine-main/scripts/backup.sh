#!/bin/bash
# PostgreSQL backup script with rotation
set -e

# Configuration
BACKUP_DIR="${BACKUP_DIR:-./backups}"
DB_NAME="${DB_NAME:-pm_internship}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${DB_USER:-postgres}"
KEEP_BACKUPS="${KEEP_BACKUPS:-10}"
S3_BUCKET="${S3_BUCKET:-}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/${DB_NAME}_${TIMESTAMP}.sql.gz"

echo "💾 PM Internship Engine - Database Backup"
echo "=========================================="
echo "Database: $DB_NAME @ $DB_HOST:$DB_PORT"
echo "Backup:   $BACKUP_FILE"
echo ""

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Dump and compress
echo "📦 Creating backup..."
if command -v pg_dump &> /dev/null; then
    pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
        --format=plain --no-owner --no-privileges \
        | gzip > "$BACKUP_FILE"
elif command -v docker &> /dev/null; then
    # Try via Docker
    CONTAINER=$(docker ps --format '{{.Names}}' | grep -i postgres | head -1)
    if [ -n "$CONTAINER" ]; then
        docker exec "$CONTAINER" pg_dump -U "$DB_USER" -d "$DB_NAME" \
            --format=plain --no-owner --no-privileges \
            | gzip > "$BACKUP_FILE"
    else
        echo "❌ Cannot find PostgreSQL or Docker container"
        exit 1
    fi
else
    echo "❌ pg_dump not found and Docker not available"
    exit 1
fi

# Verify backup
FILESIZE=$(stat -f%z "$BACKUP_FILE" 2>/dev/null || stat -c%s "$BACKUP_FILE" 2>/dev/null || echo "0")
if [ "$FILESIZE" -gt 100 ]; then
    echo "✅ Backup created: $BACKUP_FILE ($(numfmt --to=iec $FILESIZE 2>/dev/null || echo "${FILESIZE} bytes"))"
else
    echo "❌ Backup file is suspiciously small ($FILESIZE bytes)"
    exit 1
fi

# Rotate old backups
echo "🔄 Rotating old backups (keeping last $KEEP_BACKUPS)..."
BACKUP_COUNT=$(ls -1 "${BACKUP_DIR}/${DB_NAME}_"*.sql.gz 2>/dev/null | wc -l)
if [ "$BACKUP_COUNT" -gt "$KEEP_BACKUPS" ]; then
    DELETE_COUNT=$((BACKUP_COUNT - KEEP_BACKUPS))
    ls -1t "${BACKUP_DIR}/${DB_NAME}_"*.sql.gz | tail -n "$DELETE_COUNT" | while read f; do
        echo "  Removing: $(basename "$f")"
        rm "$f"
    done
    echo "  Removed $DELETE_COUNT old backup(s)"
else
    echo "  No rotation needed ($BACKUP_COUNT backups, limit $KEEP_BACKUPS)"
fi

# Optional S3 upload
if [ -n "$S3_BUCKET" ]; then
    echo "☁️  Uploading to S3..."
    if command -v aws &> /dev/null; then
        aws s3 cp "$BACKUP_FILE" "s3://${S3_BUCKET}/backups/$(basename "$BACKUP_FILE")"
        echo "✅ Uploaded to s3://${S3_BUCKET}/backups/$(basename "$BACKUP_FILE")"
    else
        echo "⚠️  AWS CLI not found, skipping S3 upload"
    fi
fi

echo ""
echo "🎉 Backup complete!"
