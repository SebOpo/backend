#!/bin/bash
alembic upgrade heads
python populate_db.py
uvicorn app.main:app --host 0.0.0.0 --port 7000