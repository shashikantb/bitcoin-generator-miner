import sys
from bit import Key

def transfer_bitcoin(private_key_wif, destination_address, amount_btc='balance'):
    """
    Transfers Bitcoin from the given private key to the destination address.
    If amount_btc is 'balance', it sends the entire available balance (sweep).
    """
    try:
        # Load the key
        k = Key(private_key_wif)
        print(f"Loaded Wallet Address: {k.address}")
        
        # Check balance
        balance_sats = k.get_balance('satoshi')
        balance_btc = k.get_balance('btc')
        print(f"Current Balance: {balance_btc} BTC ({balance_sats} sats)")
        
        if float(balance_btc) == 0:
            print("Error: Wallet has 0 balance. Cannot send.")
            return

        # Prepare transaction
        print(f"Preparing to send to: {destination_address}")
        
        if amount_btc == 'balance':
            # Send everything (minus fees)
            tx_hash = k.send([], leftover=destination_address)
        else:
            # Send specific amount
            amount = float(amount_btc)
            tx_hash = k.send([(destination_address, amount, 'btc')])
            
        print("------------------------------------------------")
        print("TRANSACTION SUCCESSFUL!")
        print(f"TX Hash: {tx_hash}")
        print("------------------------------------------------")
        
    except Exception as e:
        print(f"Transaction Failed: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 transfer.py <private_key_wif> <destination_address> [amount_btc]")
        print("Example (Sweep All): python3 transfer.py 5K... 1A1... balance")
        print("Example (Send 0.01): python3 transfer.py 5K... 1A1... 0.01")
    else:
        wif = sys.argv[1]
        dest = sys.argv[2]
        amt = sys.argv[3] if len(sys.argv) > 3 else 'balance'
        transfer_bitcoin(wif, dest, amt)
