import pandas as pd
import requests
import time
import os

# Configuration
WALLET_FILE = 'wallets.csv'
CHECKED_FILE = 'wallets_checked.csv'
BATCH_SIZE = 20  # Reduced batch size for stability across different APIs

# List of APIs to use in rotation
APIS = [
    {
        "name": "Blockchain.info",
        "url_template": "https://blockchain.info/balance?active={addresses}",
        "method": "GET",
        "parser": lambda data, addr: data[addr]['final_balance'] / 100000000.0
    },
    {
        "name": "Mempool.space",
        "url_template": "https://mempool.space/api/address/{address}", # Single address only
        "method": "SINGLE",
        "parser": lambda data: (data['chain_stats']['funded_txo_sum'] - data['chain_stats']['spent_txo_sum']) / 100000000.0
    }
]

def load_wallets():
    """Loads all generated wallets from CSV."""
    if not os.path.exists(WALLET_FILE):
        print("No wallet file found!")
        return []
    try:
        df = pd.read_csv(WALLET_FILE)
        # Ensure we have the Address column
        if 'Address' not in df.columns:
            print("Error: 'Address' column missing in CSV.")
            return []
        return df
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return []

def check_balance_blockchain_info(addresses):
    """Check multiple addresses via Blockchain.info"""
    try:
        address_string = "|".join(addresses)
        url = f"https://blockchain.info/balance?active={address_string}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            results = {}
            for addr in addresses:
                if addr in data:
                    results[addr] = data[addr]['final_balance'] / 100000000.0
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
            return data['final_balance'] / 100000000.0
    except Exception:
        pass
    return None

def recheck_all():
    print("----------------------------------------------------------------")
    print("Running COMPREHENSIVE RE-CHECK on all generated wallets...")
    print("Using APIs: Blockchain.info, BlockCypher (Backup)")
    print("----------------------------------------------------------------")
    
    df = load_wallets()
    if isinstance(df, list) and not df:
        return

    total_wallets = len(df)
    print(f"Loaded {total_wallets} wallets to check.")
    
    # We will update the 'Balance (BTC)' column
    # Convert to list for processing
    addresses = df['Address'].tolist()
    balances = {}
    
    # Process in batches
    for i in range(0, total_wallets, BATCH_SIZE):
        batch = addresses[i:i + BATCH_SIZE]
        print(f"Checking {i+1}-{min(i+BATCH_SIZE, total_wallets)} of {total_wallets}...", end="\r")
        
        try:
            # Try Primary API (Batch)
            batch_results = check_balance_blockchain_info(batch)
            
            if batch_results is not None:
                balances.update(batch_results)
            else:
                # Fallback to single checks if batch API fails
                print(f"\nBatch API failed at index {i}. Switching to individual checks for this batch...")
                for addr in batch:
                    bal = check_balance_blockcypher(addr)
                    if bal is None:
                        bal = 0.0 # Default if both fail
                    balances[addr] = bal
                    time.sleep(0.5) 
        except Exception as e:
            print(f"\nError processing batch {i}: {e}")

        # Save progress every 50 batches (1000 wallets)
        if (i // BATCH_SIZE) % 50 == 0:
            df['Balance (BTC)'] = df['Address'].map(balances).fillna(0.0)
            df.to_csv(WALLET_FILE, index=False)
            
        time.sleep(0.5) # Be nice to the API
        
    print("\n\nCheck Complete. Saving results...")
    
    # Update DataFrame
    df['Balance (BTC)'] = df['Address'].map(balances).fillna(0.0)
    
    # Save back to file
    df.to_csv(WALLET_FILE, index=False)
    print(f"Updated {WALLET_FILE} with verified balances.")
    
    # Summary
    found = df[df['Balance (BTC)'] > 0]
    if not found.empty:
        print(f"\n[!!!] SUCCESS! Found {len(found)} wallets with funds!")
        print(found)
    else:
        print("\nNo funds found in any of the existing wallets.")

if __name__ == "__main__":
    recheck_all()
