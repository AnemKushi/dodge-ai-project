#!/bin/bash

# Ensure script exits if any command fails
set -e

# Activate virtual environment
source backend/venv/Scripts/activate || source backend/venv/bin/activate

# Install requirements (optional, but safe)
pip install -r backend/requirements.txt

# Run the FastAPI app with Uvicorn
uvicorn backend.run_server:app --host 0.0.0.0 --port $PORT
