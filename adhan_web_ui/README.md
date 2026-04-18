# Adhan Web UI

This app provides a web UI and API for managing adhan cron jobs that call:

`python3 /home/hammadkhan/.openclaw/workspace/projects/ramadhan_esp32/trigger_ha.py <audio_url> <volume>`

## What it does

- Lists cron jobs containing `trigger_ha.py`
- Preserves non-adhan cron entries
- Adds a label comment above each adhan job if missing, using common prayer-name inference
- Lets you enable or disable a job by commenting or uncommenting its cron line
- Lets you update the hour and minute in `HH:MM` format

## Run

From the workspace root:

```bash
./start_web_ui.sh
```

The UI binds to `0.0.0.0:8090`.

## Access

- Local machine: `http://localhost:8090`
- LAN on this setup: `http://192.168.1.100:8090`
- If Tailscale is enabled on the laptop, use the device's Tailscale IP on port `8090`

## API

- `GET /api/jobs`
- `PUT /api/jobs`

`PUT /api/jobs` body:

```json
{
  "jobs": [
    {
      "id": "abc123",
      "enabled": true,
      "time": "13:30"
    }
  ]
}
```
