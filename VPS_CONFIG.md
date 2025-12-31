# VPS Configuration - Single Source of Truth

> **Last Updated**: 2025-12-27
> **Server**: srv1216617 (Hostinger VPS)

---

## Quick Access

### From Any Device (Mobile, Laptop, etc.)

1. Install **Tailscale** on your device: https://tailscale.com/download
2. Log in with the same account used on the VPS
3. Access services via Tailscale IP:

| Service | URL |
|---------|-----|
| **n8n** | http://100.113.138.27:5678 |
| **SSH** | `ssh root@100.113.138.27` |

### From Local Workstation (with SSH key)

```bash
ssh hostinger-vps
```

---

## Server Details

| Property | Value |
|----------|-------|
| Hostname | srv1216617 |
| Public IP | 72.62.160.2 |
| Tailscale IP | 100.113.138.27 |
| IPv6 | 2a02:4780:2d:afd2::1 |
| OS | Ubuntu 24.04.3 LTS |
| CPU | 1 core |
| RAM | 3.8 GB |
| Disk | 48 GB |
| Swap | 2 GB (configured 2025-12-27) |

---

## Firewall Rules (UFW)

| Port | Service | Access |
|------|---------|--------|
| 22 | SSH | Public (protected by fail2ban) |
| 5678 | n8n | Public |
| * | Tailscale | All traffic over VPN allowed |

---

## Running Services

### Docker Containers

| Container | Image | Internal Port | External Port | Purpose |
|-----------|-------|---------------|---------------|---------|
| n8n | n8nio/n8n:latest | 5678 | 5678 | Workflow automation |
| n8n-postgres | postgres:16 | 5432 | - | n8n database |

### System Services

| Service | Status | Purpose |
|---------|--------|---------|
| docker | active | Container runtime |
| tailscaled | active | VPN mesh network |
| fail2ban | active | SSH brute-force protection |
| monarx-agent | active | Security scanner |
| ufw | active | Firewall |

---

## Security

### SSH Access

- **Method**: Ed25519 key-based authentication
- **Password auth**: Disabled (TODO)
- **Fail2ban**: Enabled - blocks IPs after 5 failed attempts

### Authorized SSH Keys

| Name | Added | Purpose |
|------|-------|---------|
| claude-devops@hostinger-vps | 2025-12-27 | Claude Code DevOps access |

### Adding a New Device

**Option A: Tailscale (Recommended for mobile/simple access)**
1. Install Tailscale on the device
2. Sign in with your Tailscale account
3. Device automatically joins your network
4. Access VPS via 100.113.138.27

**Option B: SSH Key (For computers needing terminal access)**
1. Generate key on device: `ssh-keygen -t ed25519`
2. Send public key to admin
3. Admin adds to VPS: `echo "KEY" >> ~/.ssh/authorized_keys`
4. Connect: `ssh root@72.62.160.2` or `ssh root@100.113.138.27`

---

## Credentials & Secrets

### Database (Postgres)

| Property | Value |
|----------|-------|
| Host | n8n-postgres (docker internal) |
| Port | 5432 |
| User | n8n |
| Password | n8npass123 |
| Database | n8n |

### n8n

| Property | Value |
|----------|-------|
| URL | http://72.62.160.2:5678 |
| Tailscale URL | http://100.113.138.27:5678 |
| Encryption Key | local-dev-key-please-change-2025-01 |
| Timezone | America/New_York |

---

## Backup Strategy

> TODO: Configure automated backups

---

## Maintenance Commands

```bash
# Connect to VPS
ssh hostinger-vps

# Check Docker containers
docker ps -a

# View n8n logs
docker logs n8n --tail 100

# Restart n8n
docker restart n8n

# Check disk space
df -h

# Check memory
free -h

# Check firewall status
sudo ufw status

# Check fail2ban status
sudo fail2ban-client status sshd

# View blocked IPs
sudo fail2ban-client status sshd | grep "Banned IP"
```

---

## Change Log

| Date | Change | By |
|------|--------|-----|
| 2025-12-27 | Initial VPS setup with n8n + Postgres | User |
| 2025-12-27 | Added SSH key, UFW firewall, fail2ban, swap | Claude DevOps |
