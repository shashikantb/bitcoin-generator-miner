#!/bin/bash
if [ ! -d "venv" ]; then
    echo "Please run ./setup_vps.sh first!"
    exit 1
fi
source venv/bin/activate
echo "Starting Bitcoin Miner (CPU)..."
python3 btc_miner.py
