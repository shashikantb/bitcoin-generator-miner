#!/bin/bash
# Ensures script runs in virtual environment
if [ ! -d "venv" ]; then
    echo "Please run ./setup_vps.sh first!"
    exit 1
fi
source venv/bin/activate
echo "Starting Dashboard on Port 8501 (Accessible externally)..."
streamlit run dashboard.py --server.port 8501 --server.address 0.0.0.0
