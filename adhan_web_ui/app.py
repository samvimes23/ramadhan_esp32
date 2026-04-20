from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from cron_manager import AdhanCronManager, CronError

from override_manager import OverrideManager

BASE_DIR = Path(__file__).resolve().parent
WORKSPACE_DIR = BASE_DIR.parent.parent.parent
FAJR_STATUS_FILE = WORKSPACE_DIR / "logs" / "fajr_update_status.json"
OVERRIDE_FILE = WORKSPACE_DIR / "logs" / "adhan_overrides.json"

app = FastAPI(title="Adhan Cron Manager")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

manager = AdhanCronManager()
overrides = OverrideManager(OVERRIDE_FILE)


class JobUpdate(BaseModel):
    id: str
    enabled: bool
    time: str = Field(pattern=r"^\d{2}:\d{2}$")
    manual_override: bool | None = None


class UpdateRequest(BaseModel):
    jobs: list[JobUpdate]


@app.post("/api/play")
def play_adhan() -> dict:
    import subprocess
    from pathlib import Path
    
    # Use trigger_ha.py with default audio and volume
    audio_url = "http://192.168.1.100:8000/audio/adhan_final.mp3"
    trigger_script = Path(__file__).resolve().parent.parent / "trigger_ha.py"
    
    try:
        subprocess.run(["python3", str(trigger_script), audio_url], check=True)
        return {"status": "playing"}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/prayer-times")
def get_prayer_times() -> dict:
    import json
    from pathlib import Path
    
    json_path = Path(__file__).resolve().parent.parent / "prayer_times.json"
    if not json_path.exists():
        return {"error": "prayer_times.json not found"}
        
    try:
        with open(json_path, "r") as f:
            return json.load(f)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/fajr-status")
def fajr_status() -> dict:
    import json

    if not FAJR_STATUS_FILE.exists():
        return {
            "ok": False,
            "result": "unknown",
            "lastRun": None,
            "summary": "No local status file yet."
        }

    try:
        with open(FAJR_STATUS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/")
@app.get("/adhan")
def index() -> FileResponse:
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.get("/api/jobs")
def list_jobs() -> dict:
    try:
        jobs = manager.list_jobs()
    except CronError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    current_overrides = overrides.get_overrides()
    return {
        "jobs": [
            {
                "id": job.job_id,
                "label": job.label,
                "enabled": job.enabled,
                "time": job.time,
                "audio_url": job.audio_url,
                "volume": job.volume,
                "manual_override": current_overrides.get(job.label, False) if job.label else False,
            }
            for job in jobs
        ]
    }


@app.put("/api/jobs")
def update_jobs(request: UpdateRequest) -> dict:
    try:
        jobs = manager.update_jobs([job.model_dump() for job in request.jobs])
        
        # Sync overrides
        all_jobs = manager.list_jobs()
        job_map = {j.job_id: j for j in all_jobs}
        for update in request.jobs:
            if update.manual_override is not None:
                job = job_map.get(update.id)
                if job and job.label:
                    overrides.set_override(job.label, update.manual_override)
                    
    except CronError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    current_overrides = overrides.get_overrides()
    return {
        "jobs": [
            {
                "id": job.job_id,
                "label": job.label,
                "enabled": job.enabled,
                "time": job.time,
                "audio_url": job.audio_url,
                "volume": job.volume,
                "manual_override": current_overrides.get(job.label, False) if job.label else False,
            }
            for job in jobs
        ]
    }
