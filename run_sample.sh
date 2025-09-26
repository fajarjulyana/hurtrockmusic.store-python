#!/bin/bash

# Nama direktori venv (ubah jika kamu pakai nama lain)
VENV_DIR="venv"

# 1. Buat virtual environment jika belum ada
if [ ! -d "$VENV_DIR" ]; then
  echo "Membuat virtual environment..."
  python3 -m venv $VENV_DIR
fi

# 2. Aktifkan virtual environment
source "$VENV_DIR/bin/activate"

# 3. Set SESSION_SECRET (gunakan generator random atau string tetap)
export SESSION_SECRET=$(openssl rand -hex 32)

# 4. Jalankan sample_data.py
echo "Menjalankan sample_data.py dengan SESSION_SECRET..."
python sample_data.py

