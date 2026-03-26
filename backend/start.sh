#!/bin/bash
# Go to backend folder
cd backend

# Activate virtualenv (optional, can skip if Railway installs requirements automatically)
# source ../venv/Scripts/activate

# Run FastAPI app
uvicorn app.main:app --host 0.0.0.0 --port $PORT
