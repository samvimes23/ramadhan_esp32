import subprocess
import os

APPLY_SCRIPT = "/home/hammadkhan/.openclaw/workspace/projects/ramadhan_esp32/apply_adhan_cron.py"
VENV_PYTHON = "/home/hammadkhan/.openclaw/workspace/projects/ramadhan_esp32/adhan_web_ui/venv/bin/python3"

def run():
    print(f"--- Adhan Update Start: {os.uname().nodename} ---")
    
    # 1. Apply from JSON
    # We skip scraping for now because we're using a manual/static yearly JSON lookup
    # that Hammad provides/edits.
    print("Step 1: Applying from prayer_times.json...")
    res2 = subprocess.run([VENV_PYTHON, APPLY_SCRIPT], capture_output=True, text=True)
    print(res2.stdout)
    if res2.returncode != 0:
        print(f"Apply failed: {res2.stderr}")
        # Note: If today is missing from JSON, it prints an error message but returns 0.
        # This is fine as it won't crash the cron job.

    # 2. Trigger PM2 restart to refresh Web UI (so it shows current crontab state)
    print("Step 2: Restarting adhan-manager (PM2)...")
    # Using absolute path for PM2 as cron environment might not have /home/linuxbrew/.linuxbrew/bin in PATH
    subprocess.run(["/home/linuxbrew/.linuxbrew/bin/pm2", "restart", "adhan-manager"], capture_output=True)

    print("--- Adhan Update Complete ---")

if __name__ == "__main__":
    run()
