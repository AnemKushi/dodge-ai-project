#!/bin/bash

# Install dependencies
pip install --upgrade pip
pip install -r backend/requirements.txt

# Start the server
# For local development: use 127.0.0.1
# For production (Railway, etc): use 0.0.0.0
HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8000}
RELOAD=${RELOAD:-false}

uvicorn backend.app.main:app --host $HOST --port $PORT --reload=$RELOAD
