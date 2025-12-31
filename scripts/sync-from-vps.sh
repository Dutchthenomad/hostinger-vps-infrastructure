#!/bin/bash
# Sync project folders FROM VPS back to local
# Usage: ./sync-from-vps.sh <project-name> [--dry-run]
#
# WARNING: This will overwrite local files with VPS versions!
# Use --dry-run first to preview changes.

set -e

VPS_HOST="hostinger-vps"
VPS_PROJECTS_DIR="~/projects"
LOCAL_BASE="/home/nomad/Desktop"

# Exclusions (don't sync these)
EXCLUDES=(
    ".git"
    "__pycache__"
    "*.pyc"
    ".venv"
    "venv"
    "node_modules"
    ".pytest_cache"
    "*.egg-info"
    "dist"
    "build"
    ".mypy_cache"
    "*.log"
    ".DS_Store"
)

# Build exclude args
EXCLUDE_ARGS=""
for exc in "${EXCLUDES[@]}"; do
    EXCLUDE_ARGS="$EXCLUDE_ARGS --exclude=$exc"
done

sync_from_vps() {
    local project=$1
    local dry_run=$2
    local local_path="$LOCAL_BASE/$project"

    echo "========================================="
    echo "Syncing FROM VPS: $project"
    echo "From:    $VPS_HOST:$VPS_PROJECTS_DIR/$project"
    echo "To:      $local_path"
    echo "========================================="

    local rsync_opts="-avz --progress"
    if [ "$dry_run" = "--dry-run" ]; then
        rsync_opts="$rsync_opts --dry-run"
        echo "[DRY RUN MODE - No changes will be made]"
    else
        echo "WARNING: This will overwrite local files!"
        read -p "Continue? (y/N) " confirm
        if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
            echo "Cancelled."
            return 0
        fi
    fi

    rsync $rsync_opts $EXCLUDE_ARGS "$VPS_HOST:$VPS_PROJECTS_DIR/$project/" "$local_path/"

    echo ""
    echo "Done: $project"
    echo ""
}

if [ -z "$1" ]; then
    echo "Usage: $0 <project-name> [--dry-run]"
    echo ""
    echo "List projects on VPS:"
    ssh $VPS_HOST "ls -la ~/projects/"
    exit 1
fi

sync_from_vps "$1" "$2"
