#!/usr/bin/env bash
set -e

echo "--- Starting Adhan Manager Container ---"

# 1. Initialize crontab if it exists in the mounted volume or use a default
# We use the existing logic from update_fajr.py to ensure crontab is populated on boot
echo "Step 1: Initializing crontab schedule..."
python3 update_fajr.py

# 2. Start the cron daemon in the background
echo "Step 2: Starting cron daemon..."
cron

# 3. Start the FastAPI Web UI in the foreground
echo "Step 3: Starting Web UI on port 8090..."
cd adhan_web_ui
exec uvicorn app:app --host 0.0.0.0 --port 8090
