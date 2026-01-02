#!/bin/bash
#
# MIGRATION TRANSFER SCRIPT
# Transfers selected projects to USB drives for system migration
# Run this script and let it complete - no babysitting needed
#
# Usage: ./migration_transfer.sh
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
USB1_MOUNT="/media/nomad/USB321FD"
USB2_MOUNT="/media/nomad/MIGRATION_USB2"
USB1_DEST="$USB1_MOUNT/MIGRATION_USB1"
USB2_DEST="$USB2_MOUNT/MIGRATION_USB2"
LOG_FILE="/tmp/migration_transfer_$(date +%Y%m%d_%H%M%S).log"

# Projects for USB1 (Large Desktop projects ~49GB)
USB1_DESKTOP_PROJECTS=(
    "claude-flow"
    "CODEX"
    "CV-BOILER-PLATE-FORK"
    "JUPYTER-CENTRAL-FOLDER"
    "VECTRA-PLAYER"
    "rugs-rl-bot"
)

# Projects for USB2 (Remaining Desktop projects)
USB2_DESKTOP_PROJECTS=(
    "3d2a-repos"
    "FIGMA"
    "jupyter-ai-container"
    "LANGCHAIN"
    "REPLAYER"
    "VPS"
)

# Home directories to transfer (USB2)
HOME_DIRS=(
    ".claude"
    ".ssh"
    ".gitconfig"
    ".bashrc"
    ".zshrc"
    ".profile"
    ".jupyter"
    ".ipython"
    "mcp-server"
    "rugs_recordings"
    "rugs_data"
    "rugs_recordings_normalized"
    "rugs_roboflow_data"
    "rugs_training_data"
    "rugs_tui_sessions"
    "rugs_ab_testing"
)

log() {
    echo -e "${GREEN}[$(date '+%H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

warn() {
    echo -e "${YELLOW}[$(date '+%H:%M:%S')] WARNING:${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[$(date '+%H:%M:%S')] ERROR:${NC} $1" | tee -a "$LOG_FILE"
}

header() {
    echo -e "\n${BLUE}============================================${NC}" | tee -a "$LOG_FILE"
    echo -e "${BLUE} $1${NC}" | tee -a "$LOG_FILE"
    echo -e "${BLUE}============================================${NC}\n" | tee -a "$LOG_FILE"
}

check_space() {
    local mount=$1
    local required=$2
    local available=$(df -BG "$mount" | tail -1 | awk '{print $4}' | sed 's/G//')

    if [ "$available" -lt "$required" ]; then
        error "Not enough space on $mount. Need ${required}GB, have ${available}GB"
        return 1
    fi
    log "Space check passed: ${available}GB available on $mount"
    return 0
}

copy_with_progress() {
    local src=$1
    local dest=$2
    local name=$(basename "$src")

    if [ -e "$dest/$name" ]; then
        warn "$name already exists at destination, skipping..."
        return 0
    fi

    log "Copying: $name"
    rsync -ah --progress "$src" "$dest/" 2>&1 | tee -a "$LOG_FILE"
    log "Completed: $name"
}

# ============================================
# MAIN SCRIPT
# ============================================

header "MIGRATION TRANSFER SCRIPT"
log "Log file: $LOG_FILE"
log "Started at: $(date)"

# Check USB drives are mounted
header "Checking USB Drives"

if [ ! -d "$USB1_MOUNT" ]; then
    error "USB1 not mounted at $USB1_MOUNT"
    echo "Please mount USB1 and try again"
    exit 1
fi
log "USB1 mounted at: $USB1_MOUNT"

if [ ! -d "$USB2_MOUNT" ]; then
    warn "USB2 not mounted at $USB2_MOUNT"
    echo ""
    echo "USB2 needs to be formatted and mounted:"
    echo "  sudo umount /dev/sdc"
    echo "  sudo mkfs.exfat -n 'MIGRATION_USB2' /dev/sdc"
    echo "  # Then unplug and replug the drive"
    echo ""
    read -p "Press Enter after USB2 is mounted, or Ctrl+C to abort..."

    if [ ! -d "$USB2_MOUNT" ]; then
        error "USB2 still not mounted. Aborting."
        exit 1
    fi
fi
log "USB2 mounted at: $USB2_MOUNT"

# Create destination directories
mkdir -p "$USB1_DEST/Desktop"
mkdir -p "$USB2_DEST/Desktop"
mkdir -p "$USB2_DEST/home_nomad"

# ============================================
# USB1: Large Desktop Projects
# ============================================
header "USB1: Large Desktop Projects"

check_space "$USB1_MOUNT" 50 || exit 1

for project in "${USB1_DESKTOP_PROJECTS[@]}"; do
    src="/home/nomad/Desktop/$project"
    if [ -d "$src" ]; then
        copy_with_progress "$src" "$USB1_DEST/Desktop"
    else
        warn "Project not found: $src"
    fi
done

# ============================================
# USB2: Remaining Desktop Projects
# ============================================
header "USB2: Remaining Desktop Projects"

check_space "$USB2_MOUNT" 40 || exit 1

for project in "${USB2_DESKTOP_PROJECTS[@]}"; do
    src="/home/nomad/Desktop/$project"
    if [ -d "$src" ]; then
        copy_with_progress "$src" "$USB2_DEST/Desktop"
    else
        warn "Project not found: $src"
    fi
done

# ============================================
# USB2: Home Directory Contents
# ============================================
header "USB2: Home Directory Contents"

for item in "${HOME_DIRS[@]}"; do
    src="/home/nomad/$item"
    if [ -e "$src" ]; then
        copy_with_progress "$src" "$USB2_DEST/home_nomad"
    else
        warn "Not found: $src"
    fi
done

# ============================================
# Copy README to both drives
# ============================================
header "Copying Documentation"

# README is already on USB1, update it
log "README already on USB1"

# Copy README to USB2
if [ -f "$USB1_DEST/README.md" ]; then
    cp "$USB1_DEST/README.md" "$USB2_DEST/"
    log "README copied to USB2"
fi

# ============================================
# Summary
# ============================================
header "TRANSFER COMPLETE"

echo ""
log "USB1 contents:"
du -sh "$USB1_DEST"/* 2>/dev/null | tee -a "$LOG_FILE"

echo ""
log "USB2 contents:"
du -sh "$USB2_DEST"/* 2>/dev/null | tee -a "$LOG_FILE"

echo ""
log "Transfer completed at: $(date)"
log "Log saved to: $LOG_FILE"

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN} MIGRATION TRANSFER COMPLETE!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo "Next steps:"
echo "1. Safely eject both USB drives"
echo "2. Insert into new machine"
echo "3. Follow README.md instructions"
echo ""
