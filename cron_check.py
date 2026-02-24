import json
import time
import os
import requests
from datetime import datetime

# --- CONFIGURATION ---
HA_URL = "http://192.168.1.22:8123/api/services/media_player/play_media"
HA_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI4YzJjOGFlMTFhNzU0MDQ0YjA4MTZhN2I0ZmM4NGQ0OSIsImlhdCI6MTc3MTM2NDU2MSwiZXhwIjoyMDg2NzI0NTYxfQ._TDC37qVaQUfTIxBbIpg8VbjSGN4Gie-n_DYCYQcD9Q"
HA_ENTITY_ID = "media_player.bedroom_speaker"
ADHAN_URL = "http://192.168.1.100:8002/adhan_final.mp3"
TAKBEER_URL = "http://192.168.1.100:8002/takbeer.mp3"
SCHEDULE_FILE = "projects/ramadhan_esp32/schedule.json"
STATE_FILE = "cron_state.json"
EID_DATE = "2026-03-20"

def trigger_audio(url, volume=0.8):
    headers = {"Authorization": f"Bearer {HA_TOKEN}", "Content-Type": "application/json"}
    # Set volume
    requests.post(HA_URL.replace("play_media", "volume_set"), 
                  json={"entity_id": HA_ENTITY_ID, "volume_level": volume}, 
                  headers=headers, timeout=5)
    # Play media
    requests.post(HA_URL, 
                  json={"entity_id": HA_ENTITY_ID, "media_content_id": url, "media_content_type": "music"}, 
                  headers=headers, timeout=10)
    print(f"[{datetime.now()}] Triggered: {url}")

def main():
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    h, m = now.hour, now.minute
    
    # Load state to avoid double-triggering
    state = {}
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            state = json.load(f)
    
    last_trigger = state.get("last_trigger_min", "")
    current_min_str = now.strftime("%Y-%m-%d %H:%M")
    
    if last_trigger == current_min_str:
        return # Already triggered this minute

    # Eid Logic
    if today_str == EID_DATE:
        if h == 4 and m == 35:
            trigger_audio(ADHAN_URL)
            state["last_trigger_min"] = current_min_str
        elif 7 <= h <= 9 and m % 15 == 0:
            if h < 9 or (h == 9 and m == 0):
                trigger_audio(TAKBEER_URL)
                state["last_trigger_min"] = current_min_str
    
    # Daily Schedule Logic
    else:
        try:
            with open(SCHEDULE_FILE, "r") as f:
                schedule = json.load(f)
                for day in schedule:
                    if day["date"] == today_str:
                        # Check Sahoor/Iftar
                        s_h, s_m = map(int, day["sahoor"].split(":"))
                        i_h, i_m = map(int, day["iftar"].split(":"))
                        if (h == s_h and m == s_m) or (h == i_h and m == i_m):
                            trigger_audio(ADHAN_URL)
                            state["last_trigger_min"] = current_min_str
                            break
        except Exception as e:
            print(f"Error reading schedule: {e}")

    # Save state
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

if __name__ == "__main__":
    main()
