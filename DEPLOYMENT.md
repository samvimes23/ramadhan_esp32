# Adhan System Management

This project manages automated Adhan triggering on Home Assistant speakers and provides a web interface for schedule management.

## Components

### 1. Adhan Web UI (`adhan_web_ui/`)
A FastAPI-based web interface running on port **8090**.
- **Dashboard**: View current crontab status and last auto-update run.
- **Prayer Times**: Dedicated page to view the full 2026/2027 schedule from `prayer_times.json`.
- **API**: Endpoints for listing/updating jobs and playing test audio.

### 2. Auto-Updater (`update_adhan.py`)
Nightly script that:
1. Sychronizes local crontab with the static `prayer_times.json` for the current date.
2. Restarts the PM2 `adhan-manager` process.

### 3. Healthcheck System
A host-level bash script (`scripts/webpage_healthcheck.sh`) runs every 10 minutes to ensure all related services (Hub, Strava Proxy, Adhan Manager) are responding, auto-restarting via PM2 if needed.

## Configuration
- `prayer_times.json`: The source of truth for timings (sourced from Alislam.org for London).
- `trigger_ha.py`: Script called by cron to perform the actual Home Assistant service call.

## Deployment (PM2)
Manage the web interface via PM2:
```bash
pm2 start adhan_web_ui/app.py --name adhan-manager --interpreter adhan_web_ui/venv/bin/python3
```
