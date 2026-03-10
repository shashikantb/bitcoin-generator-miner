import time
import csv
import os
import requests
import hashlib
import random
from bit import Key

# Configuration
WALLET_FILE = 'wallets.csv'
FOUND_FILE = 'found_wallets.csv'
STATS_FILE = 'wallet_stats.csv'
BATCH_SIZE = 20  # Reduced batch size for API compatibility
GENERATE_LIMIT = 100  # Generate 100 before checking (faster feedback loop for brainwallets)

# Common words for Brainwallets (simulated small dictionary)
COMMON_WORDS = [
    "password", "123456", "bitcoin", "satoshi", "nakamoto", "freedom", "love", "god",
    "secret", "money", "blockchain", "crypto", "wallet", "key", "private", "public",
    "access", "admin", "root", "user", "guest", "test", "demo", "hello", "world"
]

def create_wallet_database():
    """Creates the CSV file if it doesn't exist."""
    if not os.path.exists(WALLET_FILE):
        with open(WALLET_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp', 'Type', 'Private Key (WIF)', 'Address', 'Balance (BTC)', 'Total Received (BTC)'])
        print(f"Created wallet database: {WALLET_FILE}")

    if not os.path.exists(FOUND_FILE):
        with open(FOUND_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp', 'Type', 'Private Key (WIF)', 'Address', 'Balance (BTC)', 'Total Received (BTC)', 'Status'])
        print(f"Created found wallets database: {FOUND_FILE}")

    if not os.path.exists(STATS_FILE):
        with open(STATS_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Timestamp',
                'Total Wallets Generated',
                'Total BTC Balance',
                'Active Balance Wallets',
                'Used Wallets (History)',
                'Total Received (All Wallets)',
            ])
        print(f"Created wallet stats file: {STATS_FILE}")

def write_wallet_stats(total_wallets, total_balance, active_wallets, used_wallets, total_received):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(STATS_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Timestamp',
            'Total Wallets Generated',
            'Total BTC Balance',
            'Active Balance Wallets',
            'Used Wallets (History)',
            'Total Received (All Wallets)',
        ])
        writer.writerow([
            timestamp,
            total_wallets,
            f"{total_balance:.8f}",
            active_wallets,
            used_wallets,
            f"{total_received:.8f}",
        ])

def generate_brainwallet():
    """Generates a key from a random combination of words."""
    # Pick 1-3 words
    num_words = random.randint(1, 3)
    passphrase = " ".join(random.sample(COMMON_WORDS, num_words))
    
    # Add some salt occasionally
    if random.random() < 0.3:
        passphrase += str(random.randint(0, 999))
        
    # SHA256 hash of passphrase becomes the private key
    private_key_bytes = hashlib.sha256(passphrase.encode('utf-8')).digest()
    k = Key.from_bytes(private_key_bytes)
    return k, passphrase

def check_balance_blockchain_info(addresses):
    """Check multiple addresses via Blockchain.info and get Total Received too."""
    try:
        address_string = "|".join(addresses)
        url = f"https://blockchain.info/balance?active={address_string}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            results = {}
            for addr in addresses:
                if addr in data:
                    bal = data[addr]['final_balance'] / 100000000.0
                    received = data[addr]['total_received'] / 100000000.0
                    results[addr] = {'balance': bal, 'received': received}
            return results
    except Exception as e:
        print(f"Blockchain.info Error: {e}")
    return None

def check_balance_blockcypher(address):
    """Check single address via BlockCypher (backup)"""
    try:
        url = f"https://api.blockcypher.com/v1/btc/main/addrs/{address}/balance"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            bal = data['final_balance'] / 100000000.0
            received = data.get('total_received', 0) / 100000000.0
            return {'balance': bal, 'received': received}
    except Exception:
        pass
    return None

def start_mining_simulation():
    create_wallet_database()
    print("----------------------------------------------------------------")
    print("BTC Wallet Generator & Hunter (BRAINWALLET MODE)")
    print(f"Strategy: Mixing Random Keys + Brainwallets (Passphrases)")
    print(f"Goal: Find 'Used' wallets (History > 0) or Funded wallets")
    print("----------------------------------------------------------------")
    
    current_batch_wifs = []
    current_batch_addrs = []
    current_batch_types = []

    total_wallets_generated = 0
    total_btc_balance = 0.0
    active_balance_wallets = 0
    used_wallets_history = 0
    total_received_all = 0.0
    
    try:
        while True:
            # 1. Generation Phase (Mixed)
            print(f"Generating {GENERATE_LIMIT} wallets (Random + Brainwallets)...", end="\r")
            
            for i in range(GENERATE_LIMIT):
                # 50% chance of Brainwallet (Higher chance to find used wallets)
                if random.random() < 0.5:
                    k, phrase = generate_brainwallet()
                    w_type = f"Brain: {phrase}"
                else:
                    k = Key()
                    w_type = "Random"
                    
                current_batch_wifs.append(k.to_wif())
                current_batch_addrs.append(k.address)
                current_batch_types.append(w_type)
            
            print(f"Generated {GENERATE_LIMIT} wallets. Checking history & balances...")
            
            # 2. Batch Checking Phase
            final_results = {}
            
            for i in range(0, len(current_batch_addrs), BATCH_SIZE):
                chunk = current_batch_addrs[i:i + BATCH_SIZE]
                
                # Try Primary API (Batch)
                batch_results = check_balance_blockchain_info(chunk)
                
                if batch_results is not None:
                    final_results.update(batch_results)
                else:
                    # Fallback
                    for addr in chunk:
                        res = check_balance_blockcypher(addr)
                        if res is None:
                            res = {'balance': 0.0, 'received': 0.0}
                        final_results[addr] = res
                        time.sleep(0.5) 
                
                time.sleep(0.5) 
            
            # 3. Save Results
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            
            with open(WALLET_FILE, 'a', newline='') as f:
                writer = csv.writer(f)
                
                for wif, addr, w_type in zip(current_batch_wifs, current_batch_addrs, current_batch_types):
                    data = final_results.get(addr, {'balance': 0.0, 'received': 0.0})
                    bal = data['balance']
                    rec = data['received']
                    
                    writer.writerow([timestamp, w_type, wif, addr, bal, rec])
                    
                    status = None
                    if bal > 0:
                        status = "JACKPOT"
                        active_balance_wallets += 1
                        total_btc_balance += bal
                        print(f"\n[!!!] JACKPOT! FUNDS FOUND! Address: {addr} | Balance: {bal} BTC")
                    elif rec > 0:
                        status = "USED_HISTORY"
                        used_wallets_history += 1
                        print(f"\n[!] FOUND USED WALLET! Address: {addr} | History: {rec} BTC (Empty Now)")
                    
                    total_received_all += rec
                    total_wallets_generated += 1
                    
                    if status:
                        with open(FOUND_FILE, 'a', newline='') as f_found:
                            writer_found = csv.writer(f_found)
                            writer_found.writerow([timestamp, w_type, wif, addr, bal, rec, status])

            write_wallet_stats(
                total_wallets=total_wallets_generated,
                total_balance=total_btc_balance,
                active_wallets=active_balance_wallets,
                used_wallets=used_wallets_history,
                total_received=total_received_all,
            )
            
            print(f"Batch Complete. Checked {len(current_batch_addrs)} keys.")
            
            # Reset batch
            current_batch_wifs = []
            current_batch_addrs = []
            current_batch_types = []
                
    except KeyboardInterrupt:
        print("\nStopped.")

if __name__ == "__main__":
    start_mining_simulation()
