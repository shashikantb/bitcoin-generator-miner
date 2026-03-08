#!/bin/bash
if [ ! -d "venv" ]; then
    echo "Please run ./setup_vps.sh first!"
    exit 1
fi
source venv/bin/activate
echo "Starting Wallet Hunter (Brainwallet Mode)..."
python3 btc_manager.py
