#!/usr/bin/env sh

dbmate wait
dbmate status

echo "[INFO] Applying Migrations..."
if dbmate migrate ; then
    echo "[INFO] Migrations applied!"
    dbmate status
else
    echo "[INFO] Migrations failed!"
    dbmate status
    exit -1
fi

if [ -d ".venv" ]; then
    echo "[INFO] .venv dir does exists! Skipping..." 
else 
    python -m venv .venv
fi

source ./.venv/bin/activate 
pip install -r requirements.txt
fastapi dev src/main.py
# fastapi run