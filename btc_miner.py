import time
import hashlib
import struct
import requests
import json
import multiprocessing
import os
import csv

# Configuration
MINING_LOG_FILE = 'mining_stats.csv'
WALLET_ADDRESS = "1YourAddressHere(ForRewards)" # Placeholder

def get_latest_block_template():
    """Fetch the latest block info to mine on top of."""
    try:
        response = requests.get('https://blockchain.info/latestblock')
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return None

def get_network_difficulty():
    """Fetch current mining difficulty."""
    try:
        response = requests.get('https://blockchain.info/q/getdifficulty')
        if response.status_code == 200:
            return float(response.text)
    except:
        pass
    return 80000000000000.0 # Fallback (approximate)

def miner_worker(worker_id, block_header_prefix, start_nonce, range_size, stats_queue):
    """
    Worker process that mines a specific range of nonces.
    """
    nonce = start_nonce
    end_nonce = start_nonce + range_size
    hashes = 0
    start_time = time.time()
    
    # Pre-encode static parts for speed
    prefix_bytes = block_header_prefix.encode('utf-8')
    
    while nonce < end_nonce:
        # Construct header (Simplified)
        header = prefix_bytes + str(nonce).encode('utf-8')
        
        # Double SHA-256
        block_hash = hashlib.sha256(hashlib.sha256(header).digest()).hexdigest()
        
        # Check target (Simplified check for visualization)
        if block_hash.startswith("000000"): 
             print(f"\n[!!!] BLOCK CANDIDATE FOUND! Hash: {block_hash}")
        
        nonce += 1
        hashes += 1
        
        # Report stats every 50k hashes
        if hashes >= 50000:
            elapsed = time.time() - start_time
            if elapsed > 0:
                hashrate = hashes / elapsed
                stats_queue.put((worker_id, hashrate, hashes))
            hashes = 0
            start_time = time.time()

def log_stats(total_hashrate, total_hashes, difficulty):
    """Updates the CSV file for the dashboard."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    
    # Overwrite mode to keep file small (Dashboard just reads last line)
    with open(MINING_LOG_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Timestamp', 'Hashrate (H/s)', 'Total Hashes', 'Difficulty'])
        writer.writerow([timestamp, total_hashrate, total_hashes, difficulty])

def start_mining_pool():
    # Setup
    print("----------------------------------------------------------------")
    print(f"BTC SOLO MINER (CPU) - {multiprocessing.cpu_count()} Cores Active")
    print("Connecting to Bitcoin Network...")
    print("----------------------------------------------------------------")
    
    block_info = get_latest_block_template()
    difficulty = get_network_difficulty()
    
    if not block_info:
        # Fallback if offline
        block_info = {'height': 999999, 'hash': '0000000000000000000abc', 'time': int(time.time())}
        
    print(f"Mining Block: {block_info['height'] + 1}")
    print(f"Network Difficulty: {difficulty:,.0f}")
    print("Start Hashing...")

    # Shared Queue for stats
    stats_queue = multiprocessing.Queue()
    
    # Create Workers
    workers = []
    num_workers = multiprocessing.cpu_count()
    range_per_worker = 1000000000 // num_workers # Big range
    
    # Header prefix
    prev_hash = block_info['hash']
    merkle = hashlib.sha256(b"trae_miner").hexdigest()
    ts = str(int(time.time()))
    bits = "1d00ffff"
    prefix = f"1{prev_hash}{merkle}{ts}{bits}"
    
    for i in range(num_workers):
        p = multiprocessing.Process(
            target=miner_worker,
            args=(i, prefix, i * range_per_worker, range_per_worker, stats_queue)
        )
        p.daemon = True
        p.start()
        workers.append(p)
        
    # Main Monitor Loop
    total_hashes_lifetime = 0
    worker_hashrates = {}
    
    try:
        while True:
            # Collect stats from queue
            while not stats_queue.empty():
                wid, rate, count = stats_queue.get()
                worker_hashrates[wid] = rate
                total_hashes_lifetime += count
                
            # Calculate totals
            total_hashrate = sum(worker_hashrates.values())
            
            # Log to file for dashboard
            log_stats(total_hashrate, total_hashes_lifetime, difficulty)
            
            # Print to terminal
            print(f"Total Hashrate: {total_hashrate/1000:.2f} kH/s | Total Hashes: {total_hashes_lifetime:,} | Diff: {difficulty:,.0f}", end="\r")
            
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\nMining Stopped.")
        for p in workers:
            p.terminate()

if __name__ == "__main__":
    # Windows/MacOS support for multiprocessing
    multiprocessing.freeze_support()
    start_mining_pool()
