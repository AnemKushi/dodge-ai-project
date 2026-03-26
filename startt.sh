#!/bin/bash
set -e

# Install Python dependencies
pip install --upgrade pip
pip install -r backend/requirements.txt

# Run FastAPI app
uvicorn backend.run_server:app --host 0.0.0.0 --port $PORT
