#!/bin/bash
# Backup all git repos to VPS backup location
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/root/backups/$DATE"
mkdir -p "$BACKUP_DIR"

echo "Starting backup: $DATE"

cd /root/projects
for repo in */; do
  repo=${repo%/}
  if [ -d "$repo/.git" ]; then
    echo "Backing up $repo..."
    tar -czf "$BACKUP_DIR/$repo.tar.gz" "$repo/"
    echo "  ✓ $repo.tar.gz created"
  fi
done

du -sh "$BACKUP_DIR"
find /root/backups -maxdepth 1 -type d -mtime +7 -exec rm -rf {} + 2>/dev/null
echo "Backup complete: $BACKUP_DIR"
