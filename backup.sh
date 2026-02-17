#!/bin/bash

# Kaluwala CSR Libraries - Database Backup Script
# Creates PostgreSQL backups with timestamp

set -e

# Configuration
BACKUP_DIR="/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="kaluwala_backup_${TIMESTAMP}.sql"
DB_NAME="kaluwala_db"
DB_USER="kaluwala"
DB_HOST="postgres"
RETENTION_DAYS=30

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting database backup...${NC}"

# Create backup directory if it doesn't exist
mkdir -p ${BACKUP_DIR}

# Create backup
echo "Backing up database: ${DB_NAME}"
pg_dump -h ${DB_HOST} -U ${DB_USER} -d ${DB_NAME} > ${BACKUP_DIR}/${BACKUP_FILE}

# Compress backup
echo "Compressing backup..."
gzip ${BACKUP_DIR}/${BACKUP_FILE}

# Check if backup was successful
if [ -f "${BACKUP_DIR}/${BACKUP_FILE}.gz" ]; then
    SIZE=$(du -h "${BACKUP_DIR}/${BACKUP_FILE}.gz" | cut -f1)
    echo -e "${GREEN}✓ Backup successful: ${BACKUP_FILE}.gz (${SIZE})${NC}"
else
    echo -e "${RED}✗ Backup failed!${NC}"
    exit 1
fi

# Delete old backups (keep last N days)
echo "Cleaning up old backups (keeping last ${RETENTION_DAYS} days)..."
find ${BACKUP_DIR} -name "kaluwala_backup_*.sql.gz" -type f -mtime +${RETENTION_DAYS} -delete

# List current backups
echo ""
echo "Current backups:"
ls -lh ${BACKUP_DIR}/kaluwala_backup_*.sql.gz 2>/dev/null || echo "No backups found"

echo -e "\n${GREEN}Backup complete!${NC}"

# Optional: Upload to S3 or cloud storage
# aws s3 cp ${BACKUP_DIR}/${BACKUP_FILE}.gz s3://your-bucket/backups/
