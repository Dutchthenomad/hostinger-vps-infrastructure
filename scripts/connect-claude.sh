#!/bin/bash
# Connect to Claude Code session on VPS
# Usage: ./connect-claude.sh
#
# This connects you to the persistent tmux session running Claude Code.
# The session stays alive even when you disconnect.
#
# Keyboard shortcuts once connected:
#   Ctrl+b d     - Detach (leave session running, exit SSH)
#   Ctrl+b c     - Create new window
#   Ctrl+b n     - Next window
#   Ctrl+b p     - Previous window
#   Ctrl+b [     - Scroll mode (q to exit)

VPS_HOST="hostinger-vps"
SESSION_NAME="claude-main"

echo "Connecting to Claude Code on VPS..."
echo "Session: $SESSION_NAME"
echo ""
echo "Tip: Press Ctrl+b then d to detach (keeps session running)"
echo ""

# Check if session exists, create if not
ssh -t $VPS_HOST "tmux has-session -t $SESSION_NAME 2>/dev/null || tmux new-session -d -s $SESSION_NAME -n workspace; tmux attach-session -t $SESSION_NAME"
