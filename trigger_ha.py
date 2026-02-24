import sys
import requests
import json

HA_URL = "http://192.168.1.22:8123/api/services/media_player/play_media"
HA_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI4YzJjOGFlMTFhNzU0MDQ0YjA4MTZhN2I0ZmM4NGQ0OSIsImlhdCI6MTc3MTM2NDU2MSwiZXhwIjoyMDg2NzI0NTYxfQ._TDC37qVaQUfTIxBbIpg8VbjSGN4Gie-n_DYCYQcD9Q"
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
        print("Usage: python3 trigger_ha.py <media_url>")
    else:
        trigger(sys.argv[1])
