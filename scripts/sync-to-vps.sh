#!/bin/bash
# Sync local project folders to VPS
# Usage: ./sync-to-vps.sh <project-name> [--dry-run]
#
# Examples:
#   ./sync-to-vps.sh REPLAYER          # Sync REPLAYER project
#   ./sync-to-vps.sh rugs-rl-bot       # Sync rugs-rl-bot project
#   ./sync-to-vps.sh VPS               # Sync VPS project
#   ./sync-to-vps.sh all               # Sync all projects
#   ./sync-to-vps.sh REPLAYER --dry-run # Preview what would sync

set -e

VPS_HOST="hostinger-vps"
VPS_PROJECTS_DIR="~/projects"
LOCAL_BASE="/home/nomad/Desktop"

# Project mappings (local folder name)
PROJECTS=(
    "REPLAYER"
    "rugs-rl-bot"
    "CV-BOILER-PLATE-FORK"
    "VPS"
    "claude-flow"
)

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

sync_project() {
    local project=$1
    local dry_run=$2
    local local_path="$LOCAL_BASE/$project"

    if [ ! -d "$local_path" ]; then
        echo "Error: Project '$project' not found at $local_path"
        return 1
    fi

    echo "========================================="
    echo "Syncing: $project"
    echo "From:    $local_path"
    echo "To:      $VPS_HOST:$VPS_PROJECTS_DIR/$project"
    echo "========================================="

    local rsync_opts="-avz --progress --delete"
    if [ "$dry_run" = "--dry-run" ]; then
        rsync_opts="$rsync_opts --dry-run"
        echo "[DRY RUN MODE - No changes will be made]"
    fi

    rsync $rsync_opts $EXCLUDE_ARGS "$local_path/" "$VPS_HOST:$VPS_PROJECTS_DIR/$project/"

    echo ""
    echo "Done: $project"
    echo ""
}

show_usage() {
    echo "Usage: $0 <project-name|all> [--dry-run]"
    echo ""
    echo "Available projects:"
    for p in "${PROJECTS[@]}"; do
        if [ -d "$LOCAL_BASE/$p" ]; then
            echo "  - $p ✓"
        else
            echo "  - $p (not found locally)"
        fi
    done
    echo "  - all (sync all projects)"
    echo ""
    echo "Options:"
    echo "  --dry-run    Preview changes without syncing"
}

# Main
if [ -z "$1" ]; then
    show_usage
    exit 1
fi

PROJECT=$1
DRY_RUN=$2

if [ "$PROJECT" = "all" ]; then
    for p in "${PROJECTS[@]}"; do
        if [ -d "$LOCAL_BASE/$p" ]; then
            sync_project "$p" "$DRY_RUN"
        fi
    done
elif [ "$PROJECT" = "--help" ] || [ "$PROJECT" = "-h" ]; then
    show_usage
else
    # Check if project is in the list or exists
    found=false
    for p in "${PROJECTS[@]}"; do
        if [ "$p" = "$PROJECT" ]; then
            found=true
            break
        fi
    done

    if [ "$found" = false ] && [ -d "$LOCAL_BASE/$PROJECT" ]; then
        echo "Warning: '$PROJECT' not in predefined list, but exists. Syncing anyway."
    fi

    sync_project "$PROJECT" "$DRY_RUN"
fi
