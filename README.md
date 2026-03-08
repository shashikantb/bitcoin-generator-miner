# Bitcoin Wallet Generator & Hunter

This toolset provides a continuous Bitcoin wallet generator and a transfer utility.

## 🚀 Features

1.  **Continuous Generation**: `btc_manager.py` runs infinitely, generating new wallets (Private Key + Address).
2.  **Storage**: All generated wallets are saved to `wallets.csv`.
3.  **Balance Check**: Can check online for existing balances (Default: Disabled for safety).
4.  **Transfer Tool**: Easily transfer funds from any generated private key to another wallet.

## 🛠️ Installation

```bash
pip install -r requirements.txt
```

## 🏃‍♂️ Usage

### 1. Start the Generator

Run the main script to start generating wallets:

```bash
python3 btc_manager.py
```

-   **Output**: It will print generated addresses to the console.
-   **Storage**: Check `wallets.csv` for the saved keys.
-   **Online Check**: To enable real-time balance checking, edit `btc_manager.py` and change `CHECK_BALANCE_ONLINE = False` to `True`. *Warning: API rate limits apply.*

### 2. Transfer Bitcoin

If you find a wallet with a balance (or want to test with a funded private key), use the transfer tool:

```bash
# Transfer EVERYTHING (Sweep) to a destination address
python3 transfer.py <PRIVATE_KEY_WIF> <DESTINATION_ADDRESS>

# Transfer a specific amount (e.g., 0.005 BTC)
python3 transfer.py <PRIVATE_KEY_WIF> <DESTINATION_ADDRESS> 0.005
```

## ⚠️ Important Disclaimer

-   **Probability**: The chance of generating a random private key that already has Bitcoin on it is astronomically low (near zero).
-   **Safety**: Never share your private keys.
-   **Legitimacy**: This tool generates valid keys using standard cryptography. It does not "hack" the blockchain.
