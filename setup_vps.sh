#!/bin/bash

# 1. Update System
echo "Updating system packages..."
sudo apt-get update && sudo apt-get upgrade -y

# 2. Install Python, Git, Tmux (for background tasks)
echo "Installing Python, Git, and Tmux..."
sudo apt-get install -y python3 python3-pip python3-venv git tmux htop

# 3. Set up Virtual Environment
echo "Setting up Python Virtual Environment..."
python3 -m venv venv
source venv/bin/activate

# 4. Install Dependencies
echo "Installing Python libraries..."
pip install -r requirements.txt

echo "----------------------------------------------------------------"
echo "SETUP COMPLETE!"
echo "----------------------------------------------------------------"
echo "To start the Dashboard (Accessible via Browser):"
echo "  streamlit run dashboard.py --server.port 8501 --server.address 0.0.0.0"
echo ""
echo "To start the Miner:"
echo "  python3 btc_miner.py"
echo ""
echo "To start the Wallet Hunter:"
echo "  python3 btc_manager.py"
echo "----------------------------------------------------------------"
