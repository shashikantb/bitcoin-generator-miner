import streamlit as st
import pandas as pd
import time
import os
import plotly.express as px

# Configuration
WALLET_FILE = 'wallets.csv'
FOUND_FILE = 'found_wallets.csv'
WALLET_STATS_FILE = 'wallet_stats.csv'
MINING_LOG_FILE = 'mining_stats.csv'
REFRESH_RATE = 2  # Seconds

st.set_page_config(
    page_title="Bitcoin Generator Dashboard",
    page_icon="₿",
    layout="wide"
)

# Custom CSS for Matrix-like effect
st.markdown("""
<style>
    .stApp {
        background-color: #0E1117;
        color: #00FF41;
    }
    .metric-card {
        background-color: #1E1E1E;
        border: 1px solid #333;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    .success-text {
        color: #00FF41 !important;
        font-weight: bold;
    }
    .warning-text {
        color: #FFA500 !important;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

st.title("₿ Bitcoin Generator & Miner Dashboard")
st.markdown("### Real-time Monitoring Dashboard")

# --- MINING STATS ---
st.subheader("⛏️ CPU Miner Status (Real-time)")
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
with col_m1:
    hashrate_ph = st.empty()
with col_m2:
    total_hashes_ph = st.empty()
with col_m3:
    difficulty_ph = st.empty()
with col_m4:
    win_prob_ph = st.empty()

st.divider()

# --- WALLET HUNTER STATS ---
st.subheader("🕵️ Wallet Hunter Status")
# Placeholders for real-time metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    total_wallets_ph = st.empty()
with col2:
    total_balance_ph = st.empty()
with col3:
    found_wallets_ph = st.empty()
with col4:
    used_wallets_ph = st.empty()

# Placeholder for recent wallets table
st.subheader("Recent Generated Wallets")
recent_wallets_ph = st.empty()

# Placeholder for FOUND wallets (VIP)
st.subheader("🏆 Found Wallets (VIP List - Balance > 0 or Used)")
found_wallets_table_ph = st.empty()

# Placeholder for charts
chart_ph = st.empty()

def load_found_data():
    if not os.path.exists(FOUND_FILE):
        return pd.DataFrame()
    try:
        return pd.read_csv(FOUND_FILE)
    except:
        return pd.DataFrame()

def load_mining_data():
    if not os.path.exists(MINING_LOG_FILE):
        return None
    try:
        # Just read the last line for speed
        df = pd.read_csv(MINING_LOG_FILE)
        if not df.empty:
            return df.iloc[-1]
    except:
        pass
    return None

def load_data():
    if not os.path.exists(WALLET_FILE):
        # Create empty with new structure
        return pd.DataFrame(columns=['Timestamp', 'Type', 'Private Key (WIF)', 'Address', 'Balance (BTC)', 'Total Received (BTC)'])
    
    try:
        df = pd.read_csv(WALLET_FILE)
        # Ensure new columns exist if loading old file (though we deleted it)
        if 'Total Received (BTC)' not in df.columns:
            df['Total Received (BTC)'] = 0.0
        if 'Type' not in df.columns:
            df['Type'] = 'Random'
        return df
    except Exception as e:
        # st.error(f"Error reading wallet database: {e}")
        return pd.DataFrame()

def load_wallet_stats():
    if not os.path.exists(WALLET_STATS_FILE):
        return None
    try:
        df = pd.read_csv(WALLET_STATS_FILE)
        if df.empty:
            return None
        return df.iloc[-1]
    except:
        return None

def load_recent_wallet_rows(max_rows=10, max_lines=400):
    if not os.path.exists(WALLET_FILE):
        return pd.DataFrame()
    try:
        from collections import deque
        lines = deque(maxlen=max_lines)
        with open(WALLET_FILE, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                lines.append(line)

        text = "".join(lines)
        import io
        df = pd.read_csv(io.StringIO(text))
        if df.empty:
            return pd.DataFrame()
        cols_to_show = ['Timestamp', 'Type', 'Address', 'Balance (BTC)', 'Total Received (BTC)']
        existing_cols = [c for c in cols_to_show if c in df.columns]
        return df.tail(max_rows)[existing_cols].iloc[::-1]
    except:
        return pd.DataFrame()

# Main Loop
while True:
    # Update Mining Stats
    mining_data = load_mining_data()
    if mining_data is not None:
        try:
            hashrate = float(mining_data['Hashrate (H/s)'])
            total_hashes = int(mining_data['Total Hashes'])
            
            # Difficulty (Check if column exists, else default)
            difficulty = 80000000000000.0
            if 'Difficulty' in mining_data:
                difficulty = float(mining_data['Difficulty'])

            hashrate_ph.metric(label="Current Hashrate", value=f"{hashrate/1000:.2f} kH/s", delta="Mining Active")
            total_hashes_ph.metric(label="Total Hashes (Guesses)", value=f"{total_hashes:,}")
            difficulty_ph.metric(label="Network Difficulty", value=f"{difficulty:,.0f}")
            
            # Probability Calculation
            # Probability of finding a block = Hashrate / (Difficulty * 2^32) per second
            # But roughly, time to find a block = Difficulty * 2^32 / Hashrate
            if hashrate > 0:
                seconds_to_win = (difficulty * (2**32)) / hashrate
                years_to_win = seconds_to_win / (3600 * 24 * 365)
                win_prob_ph.metric(label="Est. Time to Win", value=f"{years_to_win:,.0f} Years", delta="Solo Mining is Hard", delta_color="inverse")
            else:
                win_prob_ph.metric(label="Est. Time to Win", value="Infinity")

        except Exception as e:
            hashrate_ph.warning(f"Stats Error: {e}")
    else:
        hashrate_ph.metric("Current Hashrate", "0 H/s")
        total_hashes_ph.metric("Total Hashes", "0")
        difficulty_ph.metric("Network Difficulty", "Offline")
        win_prob_ph.error("Miner Offline")

    # Update Wallet Hunter Stats
    df_stats = load_wallet_stats()
    df_found = load_found_data()

    if df_stats is not None:
        try:
            total_wallets = int(df_stats['Total Wallets Generated'])
            total_balance = float(df_stats['Total BTC Balance'])
            active_wallets = int(df_stats['Active Balance Wallets'])
            used_wallets = int(df_stats['Used Wallets (History)'])
        except:
            total_wallets = 0
            total_balance = 0.0
            active_wallets = 0
            used_wallets = 0

        total_wallets_ph.metric(label="Total Wallets Generated", value=f"{total_wallets:,}")
        total_balance_ph.metric(label="Total BTC Balance", value=f"{total_balance:.8f} BTC")
        found_wallets_ph.metric(label="Active Balance", value=f"{active_wallets:,}" if active_wallets else "0")
        used_wallets_ph.metric(label="Used Wallets (History)", value=f"{used_wallets:,}" if used_wallets else "0")
        recent_df = load_recent_wallet_rows(max_rows=10)
        if not recent_df.empty:
            recent_wallets_ph.dataframe(recent_df, use_container_width=True, hide_index=True)
        else:
            recent_wallets_ph.info("No recent wallet rows available yet.")
    else:
        total_wallets_ph.metric(label="Total Wallets Generated", value="0")
        total_balance_ph.metric(label="Total BTC Balance", value="0.00000000 BTC")
        found_wallets_ph.metric(label="Active Balance", value="0")
        used_wallets_ph.metric(label="Used Wallets (History)", value="0")
        recent_wallets_ph.info("No wallet stats yet. Start the wallet hunter so it can create wallet_stats.csv.")

    if not df_found.empty:
        display_df = df_found.copy()

        def get_verdict(row):
            if row['Balance (BTC)'] > 0:
                return "💰 JACKPOT - WITHDRAW NOW!"
            elif row['Total Received (BTC)'] > 0:
                return "💀 EMPTY (History Only)"
            return "Unknown"

        display_df['Verdict'] = display_df.apply(get_verdict, axis=1)
        cols = ['Verdict'] + [c for c in display_df.columns if c != 'Verdict']
        found_wallets_table_ph.dataframe(display_df[cols].iloc[::-1], use_container_width=True, hide_index=True)
    else:
        found_wallets_table_ph.info("No VIP wallets yet (Balance > 0 or Used).")

    time.sleep(REFRESH_RATE)
