#!/bin/bash

# Install dependencies
pip install --upgrade pip
pip install -r backend/requirements.txt


# Start the server
uvicorn backend.run_server:app --host 0.0.0.0 --port $PORT
