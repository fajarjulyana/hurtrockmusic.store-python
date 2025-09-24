#!/bin/bash
set -e

APP_DIR="/home/fajarjulyana/Documents/hurtrockmusic.store-python"
VENV_DIR="$APP_DIR/.venv"
ENV_FILE="$APP_DIR/.env"
LOG_FILE="$APP_DIR/hurtrock.log"
PID_FILE="$APP_DIR/app.pid"

# --- Fungsi logging ---
log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"; }

# --- Setup venv ---
log "[INFO] Activating venv..."
if [ ! -d "$VENV_DIR" ]; then
    log "[INFO] Creating venv..."
    python -m venv "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"

pip install -r "$APP_DIR/requirements.txt"

# --- Generate .env kalau belum ada ---
if [ ! -f "$ENV_FILE" ]; then
    log "[INFO] .env not found, generating..."

    SESSION_SECRET=$(openssl rand -hex 32)
    DATABASE_URL="postgresql://fajar:fajar@localhost:5432/hurtrock"
    REDIS_URL="redis://:fajar@localhost:6379/0"
    DJANGO_SECRET_KEY=$(openssl rand -hex 32)

    cat > "$ENV_FILE" <<EOF
# Auto-generated on $(date)

# Flask
SESSION_SECRET=$SESSION_SECRET
FLASK_APP=server.py
FLASK_ENV=development
PORT=5000

# Database
DATABASE_URL=$DATABASE_URL
REDIS_URL=$REDIS_URL

# Django
DJANGO_SECRET_KEY=$DJANGO_SECRET_KEY
DJANGO_DEBUG=True
EOF

    log "[OK] .env generated at $ENV_FILE"
else
    log "[INFO] Using existing .env"
fi

# --- Export env ---
set -a
source "$ENV_FILE"
set +a

# --- Subcommand handler ---
case "$1" in
  start)
    log "[INFO] Starting Flask service..."
    nohup python "$APP_DIR/server.py" > "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"
    log "[OK] Flask started (PID $(cat $PID_FILE), Port $PORT)"
    ;;

  stop)
    if [ -f "$PID_FILE" ]; then
      kill -9 $(cat "$PID_FILE") 2>/dev/null || true
      rm -f "$PID_FILE"
      log "[INFO] Flask stopped"
    else
      log "[WARN] No PID file found"
    fi
    ;;

  restart)
    $0 stop
    $0 start
    ;;

  status)
    if [ -f "$PID_FILE" ] && ps -p $(cat "$PID_FILE") > /dev/null 2>&1; then
      log "[OK] Flask is running (PID $(cat $PID_FILE), Port $PORT)"
    else
      log "[ERROR] Flask not running"
    fi
    ;;

  logs)
    tail -f "$LOG_FILE"
    ;;

  sample-data)
    log "[INFO] Running sample_data.py..."
    python "$APP_DIR/sample_data.py"
    log "[OK] Sample data loaded"
    ;;

  *)
    echo "Usage: $0 {start|stop|restart|status|logs|sample-data}"
    exit 1
    ;;
esac
