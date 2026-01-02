# New PC Restoration Guide

**Created:** 2026-01-01
**Purpose:** Step-by-step guide to restore development environment on new computer

---

## Prerequisites

Before starting, ensure you have:
- [ ] Ubuntu/Linux installation (tested on Ubuntu 24.04)
- [ ] Internet connection
- [ ] Access to VPS (72.62.160.2)
- [ ] Backup files from old PC (see "Required Backups" below)

---

## Required Backups (From Old PC)

### Critical Files to Copy

```bash
# From old PC, copy these to USB/cloud:

# 1. SSH Keys
~/.ssh/hostinger_vps
~/.ssh/hostinger_vps.pub
~/.ssh/config

# 2. VPS Documentation Folder
~/Desktop/VPS/

# 3. Game Recordings (optional, 401 MB)
~/rugs_recordings/

# 4. Knowledge Base (if not yet on VPS)
~/Desktop/claude-flow/knowledge/rugipedia/
~/Desktop/claude-flow/knowledge/rl-design/
```

---

## Phase 1: System Setup (30 min)

### 1.1 Install Essential Tools

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dev tools
sudo apt install -y git curl wget python3 python3-pip python3-venv nodejs npm

# Install Claude Code
npm install -g @anthropic-ai/claude-code

# Verify
claude --version
```

### 1.2 Configure SSH

```bash
# Create SSH directory
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# Copy SSH key from backup
cp /path/to/backup/hostinger_vps ~/.ssh/
cp /path/to/backup/hostinger_vps.pub ~/.ssh/
chmod 600 ~/.ssh/hostinger_vps

# Create SSH config
cat > ~/.ssh/config << 'EOF'
Host hostinger-vps
    HostName 72.62.160.2
    User root
    IdentityFile ~/.ssh/hostinger_vps
    StrictHostKeyChecking no
EOF

# Test connection
ssh hostinger-vps "echo 'VPS connection successful'"
```

### 1.3 Create Project Directory Structure

```bash
mkdir -p ~/Desktop
cd ~/Desktop

# Clone or restore projects
# (See Phase 2 for each project)
```

---

## Phase 2: Restore Projects (1 hour)

### 2.1 Clone claude-flow

```bash
cd ~/Desktop
git clone https://github.com/YOUR_USERNAME/claude-flow.git

# Or restore from backup
cp -r /path/to/backup/claude-flow ~/Desktop/
```

### 2.2 Clone REPLAYER

```bash
cd ~/Desktop
git clone https://github.com/YOUR_USERNAME/REPLAYER.git

# Create virtual environment
cd REPLAYER
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2.3 Clone rugs-rl-bot

```bash
cd ~/Desktop
git clone https://github.com/YOUR_USERNAME/rugs-rl-bot.git

# Create virtual environment
cd rugs-rl-bot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2.4 Restore VPS Documentation

```bash
# Copy VPS folder from backup
cp -r /path/to/backup/VPS ~/Desktop/

# Verify critical files
ls ~/Desktop/VPS/docs/
# Should see: SYSTEM_ARCHITECTURE.md, RAG_MIGRATION_PLAN.md, etc.
```

### 2.5 Restore Game Recordings (Optional)

```bash
# If you have the recordings backup
mkdir -p ~/rugs_recordings
cp -r /path/to/backup/rugs_recordings/* ~/rugs_recordings/

# Or sync from VPS (if already uploaded)
rsync -avz hostinger-vps:/root/knowledge/game-events/ ~/rugs_recordings/
```

---

## Phase 3: Configure Claude Code (15 min)

### 3.1 Install Claude Code Plugin

```bash
# Create plugins directory
mkdir -p ~/.claude/plugins

# Symlink claude-flow plugin
ln -s ~/Desktop/claude-flow/.claude-plugin ~/.claude/plugins/claude-flow
```

### 3.2 Configure MCP Servers

```bash
# Add VPS RAG MCP server
claude mcp add rugs-rag http://72.62.160.2:5678/mcp

# Verify
claude mcp list
```

### 3.3 Copy CLAUDE.md

```bash
# Ensure home CLAUDE.md exists
cat > ~/CLAUDE.md << 'EOF'
# Project: Quantitative Analysis & Trading Tools

## Quick Reference

### VPS Connection
```bash
ssh hostinger-vps
```

### Projects
- claude-flow: ~/Desktop/claude-flow
- REPLAYER: ~/Desktop/REPLAYER
- rugs-rl-bot: ~/Desktop/rugs-rl-bot
- VPS docs: ~/Desktop/VPS

### MCP Servers
- rugs-rag: http://72.62.160.2:5678/mcp

See ~/Desktop/VPS/docs/SYSTEM_ARCHITECTURE.md for full details.
EOF
```

---

## Phase 4: Verify VPS RAG System (15 min)

### 4.1 Check VPS Services

```bash
# SSH to VPS
ssh hostinger-vps

# Check all containers running
docker ps

# Expected output:
# - n8n
# - n8n-postgres
# - qdrant
# - rabbitmq
# - timescaledb
```

### 4.2 Test Qdrant

```bash
# From VPS
curl "http://localhost:6333/collections" | jq .

# Should see: rugs_protocol, rl_design, external_docs
```

### 4.3 Test RAG Query

```bash
# From VPS
curl "http://localhost:5678/webhook/rag/query?q=gameStateUpdate"

# Should return relevant chunks
```

### 4.4 Test MCP from Local

```bash
# From new PC
claude

# In Claude, test RAG
> Use the rugs-rag MCP to query "what is gameStateUpdate"
```

---

## Phase 5: Verify Local Development (15 min)

### 5.1 Test REPLAYER

```bash
cd ~/Desktop/REPLAYER
./run.sh

# Should launch GUI
# Test: Load a recording, verify playback works
```

### 5.2 Test rugs-rl-bot

```bash
cd ~/Desktop/rugs-rl-bot
source .venv/bin/activate

# Run tests
python -m pytest tests/ -v

# Should pass all tests
```

### 5.3 Test claude-flow

```bash
cd ~/Desktop/claude-flow

# Verify plugin structure
ls -la .claude-plugin/

# Test with Claude
claude
> /tdd "test"  # Should invoke TDD skill
```

---

## Troubleshooting

### SSH Connection Failed

```bash
# Check key permissions
chmod 600 ~/.ssh/hostinger_vps

# Check SSH config
cat ~/.ssh/config

# Test verbose
ssh -v hostinger-vps
```

### VPS Services Not Running

```bash
# SSH to VPS
ssh hostinger-vps

# Restart all services
cd /root/rag-stack
docker-compose down
docker-compose up -d

# Check logs
docker-compose logs -f
```

### Qdrant Empty

```bash
# Re-run ingestion
ssh hostinger-vps
python3 /root/scripts/ingest_knowledge.py
```

### MCP Not Working

```bash
# Remove and re-add
claude mcp remove rugs-rag
claude mcp add rugs-rag http://72.62.160.2:5678/mcp

# Check n8n MCP workflow is active
# Visit: http://72.62.160.2:5678 (n8n UI)
```

---

## Verification Checklist

### System
- [ ] SSH to VPS works
- [ ] Claude Code installed
- [ ] Python 3.10+ available
- [ ] Node.js available

### Projects
- [ ] claude-flow cloned/restored
- [ ] REPLAYER cloned/restored
- [ ] rugs-rl-bot cloned/restored
- [ ] VPS docs folder present

### Claude Code
- [ ] Plugin symlinked
- [ ] MCP server added
- [ ] CLAUDE.md in home

### VPS RAG
- [ ] All 5 containers running
- [ ] Qdrant has vectors
- [ ] RAG query works
- [ ] MCP accessible from local

### Local Dev
- [ ] REPLAYER launches
- [ ] rugs-rl-bot tests pass
- [ ] /tdd skill works

---

## Quick Reference After Restoration

### Daily Commands

```bash
# Connect to VPS
ssh hostinger-vps

# Run REPLAYER
cd ~/Desktop/REPLAYER && ./run.sh

# Run rugs-rl-bot tests
cd ~/Desktop/rugs-rl-bot && .venv/bin/python -m pytest tests/ -v

# Query RAG
curl "http://72.62.160.2:5678/webhook/rag/query?q=YOUR_QUERY"
```

### Key Documentation

| Document | Location |
|----------|----------|
| System Architecture | ~/Desktop/VPS/docs/SYSTEM_ARCHITECTURE.md |
| RAG Migration Plan | ~/Desktop/VPS/docs/RAG_MIGRATION_PLAN.md |
| VPS Credentials | ~/Desktop/VPS/CREDENTIALS.md |
| Protocol Spec | ~/Desktop/claude-flow/knowledge/rugipedia/canon/WEBSOCKET_EVENTS_SPEC.md |

---

*Guide created: 2026-01-01*
*For system architecture details, see: SYSTEM_ARCHITECTURE.md*
