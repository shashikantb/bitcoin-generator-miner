import streamlit as st
import pandas as pd
import time
import os
import plotly.express as px

# Configuration
WALLET_FILE = 'wallets.csv'
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

# Placeholder for charts
chart_ph = st.empty()

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
    df = load_data()
    
    if not df.empty:
        # Metrics
        total_wallets = len(df)
        total_balance = df['Balance (BTC)'].sum()
        wallets_with_balance = df[df['Balance (BTC)'] > 0]
        wallets_used = df[df['Total Received (BTC)'] > 0]
        
        # Update metrics using placeholders
        total_wallets_ph.metric(label="Total Wallets Generated", value=f"{total_wallets:,}")
        total_balance_ph.metric(label="Total BTC Balance", value=f"{total_balance:.8f} BTC")
        
        if not wallets_with_balance.empty:
            found_wallets_ph.metric(label="Active Balance", value=f"{len(wallets_with_balance)}", delta="JACKPOT!", delta_color="normal")
        else:
            found_wallets_ph.metric(label="Active Balance", value="0")
            
        if not wallets_used.empty:
            used_wallets_ph.metric(label="Used Wallets (History)", value=f"{len(wallets_used)}", delta="FOUND!", delta_color="normal")
        else:
            used_wallets_ph.metric(label="Used Wallets (History)", value="0")

        # Recent Wallets Table (Show last 10)
        # Handle cases where new columns might be missing in very fresh race condition
        cols_to_show = ['Timestamp', 'Type', 'Address', 'Balance (BTC)', 'Total Received (BTC)']
        existing_cols = [c for c in cols_to_show if c in df.columns]
        
        recent_df = df.tail(10)[existing_cols].iloc[::-1]
        recent_wallets_ph.dataframe(recent_df, use_container_width=True, hide_index=True)

        # Alert if funds found
        if not wallets_with_balance.empty:
            st.success(f"🚨 FUNDS FOUND! {len(wallets_with_balance)} wallet(s) have a balance! Check wallets.csv immediately.")
            st.dataframe(wallets_with_balance, use_container_width=True)
            
        # Alert if used wallets found (but empty)
        if not wallets_used.empty and wallets_with_balance.empty:
             st.info(f"👀 Found {len(wallets_used)} wallets that were used in the past! (Balance is 0 now)")

    time.sleep(REFRESH_RATE)
