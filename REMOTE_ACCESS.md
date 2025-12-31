# Remote Access to Claude Code on VPS

Your VPS is configured with Claude Code running in a persistent tmux session.
Connect from **any device** to continue your work.

## Quick Connect Commands

### From your Desktop (with SSH config)
```bash
# Option 1: Use the connect script
cd ~/Desktop/VPS
./scripts/connect-claude.sh

# Option 2: Manual SSH + tmux attach
ssh hostinger-vps
tmux attach -t claude-main
```

### From any device (phone, laptop, work PC)
```bash
# SSH directly to VPS
ssh root@72.62.160.2 -i /path/to/your/key

# Then attach to the Claude session
tmux attach -t claude-main
```

### Using Tailscale (if on your Tailscale network)
```bash
ssh root@100.113.138.27
tmux attach -t claude-main
```

## Tmux Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+b d` | **Detach** (exit but keep session running) |
| `Ctrl+b c` | Create new window |
| `Ctrl+b n` | Next window |
| `Ctrl+b p` | Previous window |
| `Ctrl+b [` | Scroll mode (press `q` to exit) |
| `Ctrl+b &` | Kill current window |

## Syncing Project Files

### Push projects TO VPS
```bash
cd ~/Desktop/VPS

# Sync a specific project
./scripts/sync-to-vps.sh REPLAYER

# Preview what would sync (dry run)
./scripts/sync-to-vps.sh REPLAYER --dry-run

# Sync all projects
./scripts/sync-to-vps.sh all
```

### Pull projects FROM VPS
```bash
cd ~/Desktop/VPS
./scripts/sync-from-vps.sh REPLAYER
```

## VPS Details

| Property | Value |
|----------|-------|
| IP Address | 72.62.160.2 |
| Tailscale IP | 100.113.138.27 |
| SSH User | root |
| SSH Key | `~/.ssh/config` → hostinger-vps |
| Projects Dir | `~/projects/` |
| tmux Session | `claude-main` |

## Starting Claude Code

Once connected to the tmux session:
```bash
# Start Claude Code
claude

# Start in a specific project
cd ~/projects/REPLAYER
claude
```

## Troubleshooting

### Session doesn't exist?
```bash
# Create a new session
tmux new-session -s claude-main -n workspace

# Set the API key
export ANTHROPIC_API_KEY="your-key-here"
```

### Check if session is running
```bash
tmux list-sessions
```

### View session without attaching
```bash
tmux capture-pane -t claude-main -p
```

## Phone Access (Termux on Android)

1. Install Termux from F-Droid
2. Install OpenSSH: `pkg install openssh`
3. Copy your SSH key to Termux
4. Connect: `ssh root@72.62.160.2`
5. Attach: `tmux attach -t claude-main`

## Work PC Access (if SSH available)

If your work PC has SSH (Git Bash, WSL, or native):
```bash
ssh root@72.62.160.2
tmux attach -t claude-main
```

If behind firewall, use Tailscale:
1. Install Tailscale on work PC
2. Connect to your Tailscale network
3. `ssh root@100.113.138.27`
