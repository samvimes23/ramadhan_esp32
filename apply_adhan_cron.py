import os
import json
import subprocess
import re
from datetime import datetime

# Adjacency - we need to reach adhan_web_ui because its cron_manager logic is solid
import sys
sys.path.append("/home/hammadkhan/.openclaw/workspace/projects/ramadhan_esp32/adhan_web_ui")
from cron_manager import AdhanCronManager

LOOKUP_FILE = "/home/hammadkhan/.openclaw/workspace/projects/ramadhan_esp32/prayer_times.json"

def apply_updates():
    if not os.path.exists(LOOKUP_FILE):
        print(f"Lookup file {LOOKUP_FILE} not found.")
        return

    with open(LOOKUP_FILE, 'r') as f:
        data = json.load(f)
    
    # Get current date info
    now = datetime.now()
    year_str = str(now.year)
    month_str = now.strftime("%B") # e.g. "April"
    day_str = str(now.day)

    # Navigate: year -> month -> day
    year_data = data.get(year_str, {})
    month_data = year_data.get(month_str, {})
    day_times = month_data.get(day_str, {})

    if not day_times:
        print(f"No prayer times found for {day_str} {month_str} {year_str} in {LOOKUP_FILE}")
        return

    # Load Overrides
    OVERRIDE_FILE = "/home/hammadkhan/.openclaw/workspace/logs/adhan_overrides.json"
    overrides = {}
    if os.path.exists(OVERRIDE_FILE):
        try:
            with open(OVERRIDE_FILE, "r") as f:
                overrides = json.load(f)
        except Exception:
            pass

    manager = AdhanCronManager()
    current_jobs = manager.list_jobs()
    
    updates = []
    for job in current_jobs:
        prayer_name = job.label # Fajr, Dhuhr, Asr, Maghrib, Isha
        
        # Skip if manual override is active for this prayer
        if overrides.get(prayer_name):
            print(f"Skipping {prayer_name} update (Manual Override active).")
            continue

        if prayer_name in day_times:
            new_time = day_times[prayer_name]
            # Ensure the job stays enabled when updating from the reliable JSON
            is_enabled = True 
            if job.time != new_time or not job.enabled:
                print(f"Updating {prayer_name}: {job.time} (enabled={job.enabled}) -> {new_time} (enabled=True)")
                updates.append({
                    "id": job.job_id,
                    "time": new_time,
                    "enabled": is_enabled
                })
            else:
                print(f"{prayer_name} is already up to date ({new_time}).")
        else:
            print(f"No update found for {prayer_name} in JSON for today.")

    if updates:
        manager.update_jobs(updates)
        print("Crontab updated successfully from JSON.")
    else:
        print("No crontab changes needed today.")

if __name__ == "__main__":
    apply_updates()
