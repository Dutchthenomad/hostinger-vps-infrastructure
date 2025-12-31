# n8n on Hostinger VPS (Docker Manager)

This is a minimal learning setup using Docker Manager with n8n + Postgres.

## Files
- `/home/nomad/Desktop/VPS/docker-compose.yml`
- `/home/nomad/Desktop/VPS/.env`

## Steps (Compose manually)

1) Open Hostinger control panel → your VPS → **Docker Manager**.
2) Click **Compose manually**.
3) Paste the contents of `/home/nomad/Desktop/VPS/docker-compose.yml` into the editor.
4) Add environment variables from `/home/nomad/Desktop/VPS/.env`:
   - If the UI supports an env section, paste them there.
   - Otherwise, fill them in via the form fields (exact names/values).
5) Confirm ports:
   - `5678:5678`
6) Deploy the project.
7) Wait until both containers show **Running**.

## Access
Open in your browser:
```
http://72.62.160.2:5678
```

## Notes
- This uses HTTP on the server IP for now. When you add a domain, update:
  - `N8N_HOST`, `N8N_PROTOCOL`, `WEBHOOK_URL`
- Do not change `N8N_ENCRYPTION_KEY` unless you are OK resetting saved credentials.

## Later (when you get a domain)
Update `.env` values to:
```
N8N_HOST=n8n.yourdomain.com
N8N_PROTOCOL=https
WEBHOOK_URL=https://n8n.yourdomain.com/
```
Then redeploy the project in Docker Manager.
