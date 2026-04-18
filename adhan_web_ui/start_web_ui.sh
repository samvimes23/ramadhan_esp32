#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="/home/hammadkhan/.openclaw/workspace"
APP_DIR="$WORKSPACE/projects/ramadhan_esp32/adhan_web_ui"
VENV_DIR="$WORKSPACE/.venv-adhan-web-ui"

cd "$WORKSPACE"

if [ ! -d "$VENV_DIR" ]; then
  python3 -m venv "$VENV_DIR"
fi

if ! "$VENV_DIR/bin/python" -c "import fastapi, uvicorn" >/dev/null 2>&1; then
  "$VENV_DIR/bin/pip" install --upgrade pip
  "$VENV_DIR/bin/pip" install -r "$APP_DIR/requirements.txt"
fi

exec "$VENV_DIR/bin/python" -m uvicorn app:app \
  --app-dir "$APP_DIR" \
  --host 0.0.0.0 \
  --port 8090
