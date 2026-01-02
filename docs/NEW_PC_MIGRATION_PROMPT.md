# New PC Migration - Claude Code Onboarding Prompt

**Date:** 2026-01-01
**Source:** Old workstation (Ubuntu)
**Target:** New workstation (Fresh Ubuntu install)

---

## Executive Summary

I am migrating from my old workstation to this new PC. I have two 64GB USB drives (ext4 formatted) containing my development environment, projects, and configuration files. Your job is to help me:

1. Restore files from the USB drives
2. Install all required dependencies in the correct order
3. Verify each project works after restoration

**IMPORTANT:** Follow a phased approach. Do not rush. Verify each step before proceeding.

---

## Phase 1: System Preparation (Before USB Restore)

### 1.1 Essential System Packages

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y \
    git curl wget unzip \
    build-essential \
    python3 python3-pip python3-venv \
    nodejs npm \
    docker.io docker-compose \
    chromium-browser \
    jq tree htop
```

### 1.2 Add User to Docker Group

```bash
sudo usermod -aG docker $USER
# Log out and back in for this to take effect
```

### 1.3 Create Standard Directory Structure

```bash
mkdir -p ~/Desktop
mkdir -p ~/.claude
mkdir -p ~/.ssh
chmod 700 ~/.ssh
```

---

## Phase 2: USB1 Restoration (Primary Projects)

### 2.1 Mount USB1

```bash
# Find the device (look for 57GB ext4 labeled MIGRATION_USB1)
lsblk -o NAME,SIZE,LABEL,FSTYPE

# Mount it (replace sdX with actual device)
sudo mkdir -p /media/$USER/MIGRATION_USB1
sudo mount /dev/sdX /media/$USER/MIGRATION_USB1
```

### 2.2 USB1 Contents

| Project | Size | Description |
|---------|------|-------------|
| claude-flow | 11GB | Claude orchestration, RAG pipeline, knowledge base |
| CODEX | 6GB | Codex project |
| CV-BOILER-PLATE-FORK | 7.8GB | Computer vision, YOLO training for Rugs.fun |
| JUPYTER-CENTRAL-FOLDER | 8.1GB | Jupyter notebooks collection |
| VECTRA-PLAYER | 8.7GB | Rugs.fun game viewer/recorder |
| rugs-rl-bot | 7.7GB | Reinforcement learning trading bot |

### 2.3 Restore USB1 Projects

```bash
# Restore all projects to Desktop
rsync -ah --progress /media/$USER/MIGRATION_USB1/Desktop/* ~/Desktop/

# Verify
ls -la ~/Desktop/
du -sh ~/Desktop/*
```

### 2.4 Safely Eject USB1

```bash
sync && sudo umount /media/$USER/MIGRATION_USB1
```

---

## Phase 3: USB2 Restoration (Configs + Remaining Projects)

### 3.1 Mount USB2

```bash
sudo mkdir -p /media/$USER/MIGRATION_USB2
sudo mount /dev/sdX /media/$USER/MIGRATION_USB2
```

### 3.2 USB2 Contents

**Desktop Projects:**
- 3d2a-repos
- FIGMA
- jupyter-ai-container
- LANGCHAIN
- REPLAYER (Rugs.fun replay system)
- VPS (Infrastructure configs)

**Home Configs:**
- .claude (Claude Code configuration)
- .ssh (SSH keys - CRITICAL)
- .gitconfig
- .bashrc, .zshrc, .profile
- .jupyter, .ipython

**Data Directories:**
- mcp-server
- rugs_recordings (~929 game recordings)
- rugs_data, rugs_recordings_normalized
- rugs_roboflow_data, rugs_training_data
- rugs_tui_sessions, rugs_ab_testing

### 3.3 Restore USB2 Contents

```bash
# Restore Desktop projects
rsync -ah --progress /media/$USER/MIGRATION_USB2/Desktop/* ~/Desktop/

# Restore home configs (CAREFUL - these overwrite existing)
rsync -ah --progress /media/$USER/MIGRATION_USB2/home_nomad/.claude ~/
rsync -ah --progress /media/$USER/MIGRATION_USB2/home_nomad/.ssh ~/
rsync -ah --progress /media/$USER/MIGRATION_USB2/home_nomad/.gitconfig ~/
rsync -ah --progress /media/$USER/MIGRATION_USB2/home_nomad/.bashrc ~/
rsync -ah --progress /media/$USER/MIGRATION_USB2/home_nomad/.zshrc ~/
rsync -ah --progress /media/$USER/MIGRATION_USB2/home_nomad/.jupyter ~/
rsync -ah --progress /media/$USER/MIGRATION_USB2/home_nomad/.ipython ~/

# Restore data directories to home
rsync -ah --progress /media/$USER/MIGRATION_USB2/home_nomad/mcp-server ~/
rsync -ah --progress /media/$USER/MIGRATION_USB2/home_nomad/rugs_recordings ~/
rsync -ah --progress /media/$USER/MIGRATION_USB2/home_nomad/rugs_data ~/
# ... etc for other rugs_* directories

# Fix SSH permissions
chmod 700 ~/.ssh
chmod 600 ~/.ssh/*
chmod 644 ~/.ssh/*.pub
```

### 3.4 Safely Eject USB2

```bash
sync && sudo umount /media/$USER/MIGRATION_USB2
```

---

## Phase 4: Python Environment Setup

### 4.1 Verify Python Version

```bash
python3 --version  # Should be 3.10+
```

### 4.2 Project Virtual Environments

Each project has its own `.venv`. You may need to recreate them:

```bash
# For each project that needs it:
cd ~/Desktop/PROJECT_NAME
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt  # if exists
# OR
pip install -e .  # if setup.py/pyproject.toml exists
```

### 4.3 Key Python Dependencies (Global or per-project)

```bash
# ML/AI
pip install torch torchvision  # or pytorch-cpu if no GPU
pip install ultralytics  # YOLOv8
pip install gymnasium stable-baselines3
pip install scikit-learn pandas numpy

# Web/Automation
pip install playwright
playwright install chromium

# Data
pip install influxdb-client
pip install easyocr pytesseract
```

---

## Phase 5: Node.js Setup

### 5.1 Install Node Version Manager (Recommended)

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc
nvm install --lts
nvm use --lts
```

### 5.2 Key Node Projects

- `~/mcp-server` - MCP server for Claude
- `~/Desktop/VPS/api-n8n-node` - n8n Hostinger node

```bash
cd ~/mcp-server && npm install
cd ~/Desktop/VPS/api-n8n-node && npm install
```

---

## Phase 6: Git & SSH Configuration

### 6.1 Verify Git Config

```bash
git config --global user.name
git config --global user.email
```

### 6.2 Test SSH Keys

```bash
# Test GitHub access
ssh -T git@github.com

# If keys don't work, they may need to be re-added to ssh-agent:
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519  # or your key name
```

---

## Phase 7: Project Verification Checklist

After restoration, verify each critical project:

### 7.1 REPLAYER
```bash
cd ~/Desktop/REPLAYER
./run.sh  # or python3 -m pytest src/tests/ -v
```

### 7.2 rugs-rl-bot
```bash
cd ~/Desktop/rugs-rl-bot
source .venv/bin/activate
python -m pytest tests/ -v
```

### 7.3 CV-BOILER-PLATE-FORK
```bash
cd ~/Desktop/CV-BOILER-PLATE-FORK
source .venv/bin/activate
python3 -m pytest tests/ -v
```

### 7.4 VECTRA-PLAYER
```bash
cd ~/Desktop/VECTRA-PLAYER
source .venv/bin/activate
python -m pytest -v
```

### 7.5 claude-flow
```bash
cd ~/Desktop/claude-flow
# Check RAG pipeline
ls -la rag-pipeline/
```

---

## Phase 8: Optional - Docker Services

If needed for development:

```bash
# Start Docker
sudo systemctl start docker
sudo systemctl enable docker

# Verify
docker ps
```

---

## Known Issues & Fixes

### Virtual Environments May Need Recreation
If `.venv` directories have broken symlinks (Python path changed), delete and recreate:
```bash
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Playwright Browsers
Playwright needs to download browser binaries:
```bash
playwright install chromium
```

### Permission Issues
If files have wrong ownership:
```bash
sudo chown -R $USER:$USER ~/Desktop/
sudo chown -R $USER:$USER ~/rugs_*
```

---

## Project Priority Order

1. **SSH keys + Git** - Required for everything
2. **REPLAYER** - Most actively used
3. **rugs-rl-bot** - Active development
4. **VECTRA-PLAYER** - Related to REPLAYER
5. **CV-BOILER-PLATE-FORK** - YOLO training
6. **claude-flow** - RAG infrastructure
7. **VPS** - Server configs (reference only)

---

## Questions to Ask User

Before proceeding, clarify:
1. Does this PC have a GPU? (Affects PyTorch installation)
2. Which projects are highest priority?
3. Should we verify each project before moving to the next, or restore all first?
4. Any specific configurations that differ from old machine?

---

## Success Criteria

Migration is complete when:
- [ ] All USB contents restored to correct locations
- [ ] SSH keys working (can push to GitHub)
- [ ] Git configured with correct identity
- [ ] Python venvs working for priority projects
- [ ] At least one project's test suite passes
- [ ] Claude Code can access project CLAUDE.md files

---

*Generated by Claude Code on old workstation, 2026-01-01*
