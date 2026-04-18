import os
import sys
import requests
import json

HA_URL = "http://192.168.1.22:8123/api/services/media_player/play_media"
def _load_ha_token():
    token = os.getenv("HA_TOKEN")
    if token:
        return token
    try:
        with open(os.path.expanduser("~/.config/home-assistant/config.json"), "r", encoding="utf-8") as f:
            return json.load(f)["token"]
    except Exception as exc:
        raise RuntimeError("Set HA_TOKEN or configure ~/.config/home-assistant/config.json") from exc

HA_TOKEN = _load_ha_token()

HA_ENTITY_ID = "media_player.bedroom_speaker"

def trigger(media_url, volume=0.8):
    headers = {
        "Authorization": f"Bearer {HA_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Set volume
    vol_data = {"entity_id": HA_ENTITY_ID, "volume_level": volume}
    requests.post(HA_URL.replace("play_media", "volume_set"), json=vol_data, headers=headers)
    
    # Play media
    play_data = {
        "entity_id": HA_ENTITY_ID,
        "media_content_id": media_url,
        "media_content_type": "music"
    }
    r = requests.post(HA_URL, json=play_data, headers=headers)
    print(f"Triggered {media_url}, Status: {r.status_code}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 trigger_ha.py <media_url> [volume]")
    else:
        vol = float(sys.argv[2]) if len(sys.argv) > 2 else 0.8
        trigger(sys.argv[1], vol)
