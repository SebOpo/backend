#!/bin/bash
alembic upgrade heads
python populate_db.py

reload=""
if [ "$UVICORN__RELOAD" == "1" ]; then
    echo "Running in development mode"
    reload="--reload"
fi


uvicorn app.main:app --host 0.0.0.0 --port 7000 $reload