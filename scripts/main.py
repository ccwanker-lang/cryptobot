#!/usr/bin/env python3

import ccxt
import pandas as pd
import random
import json
import time
import pickle

from indicators import moving_average, rsi, bollinger_bands, ema, macd, stochastic

# ===============================
# Reward functie
# ===============================
def reward_function(total_value, prev_value):
    return total_value - prev_value

# ===============================
# Q-learning config
# ===============================
actions = ['HOLD', 'BUY', 'SELL']

# Load bestaande Q-table indien bestaat
try:
    with open("q_table.pkl", "rb") as f:
        q_table = pickle.load(f)
        print("Q-table geladen")
except:
    q_table = {}
    print("Nieuwe Q-table gemaakt")

alpha = 0.1
gamma = 0.95
epsilon = 0.3

def discretize_state(state):
    return tuple(state)

def choose_action(state):
    s = discretize_state(state)
    if s not in q_table:
        q_table[s] = {a:0 for a in actions}
    if random.random() < epsilon:
        return random.choice(actions)
    return max(q_table[s], key=q_table[s].get)

# ===============================
# Config laden
# ===============================
with open("configs/config.json") as f:
    config = json.load(f)

exchange = ccxt.binance({
    'apiKey': config["binance"]["api_key"],
    'secret': config["binance"]["api_secret"],
    'enableRateLimit': True,
    'options': {
        'defaultType': 'spot',
    },
    'urls': {
        'api': {
            'public': 'https://testnet.binance.vision/api',
            'private': 'https://testnet.binance.vision/api',
        }
    }
})
# ===============================
# Portfolio
# ===============================
portfolio = {'USDT': 1000, 'BTC': 0}
portfolio_values = []

# ===============================
# Historische data ophalen
# ===============================
print("Market data ophalen...")

ohlcv = exchange.fetch_ohlcv('BTC/USDT', '1m', limit=500)
df = pd.DataFrame(ohlcv, columns=['timestamp','open','high','low','close','volume'])

# Indicatoren berekenen
df['MA20'] = moving_average(df['close'], 20)
df['MA50'] = moving_average(df['close'], 50)
df['RSI14'] = rsi(df, 14)
df['MACD'], df['MACD_signal'] = macd(df)
df.fillna(method="bfill", inplace=True)

print("Bot gestart...")

# ===============================
# Oneindige training loop
# ===============================
i = 50

while True:
    row = df.iloc[i % len(df)]
    price = row['close']

    # Simpele state
    state = [
        int(row['RSI14'] > 50),
        int(price > row['MA20']),
        int(row['MA20'] > row['MA50']),
        int(row['MACD'] > row['MACD_signal']),
        int(portfolio['BTC'] > 0)
    ]

    action = choose_action(state)
    prev_value = portfolio['USDT'] + portfolio['BTC'] * price
    trade_amount = portfolio['USDT'] * 0.1
    trade_profit = 0

    # ===============================
    # Trade uitvoeren
    # ===============================
    if action == "BUY" and portfolio['USDT'] >= trade_amount:
        btc_bought = trade_amount / price
        portfolio['BTC'] += btc_bought
        portfolio['USDT'] -= trade_amount

    elif action == "SELL" and portfolio['BTC'] > 0:
        sell_value = portfolio['BTC'] * price
        portfolio['USDT'] += sell_value
        portfolio['BTC'] = 0

    # HOLD gebeurt, geen print
    total_value = portfolio['USDT'] + portfolio['BTC'] * price
    reward = reward_function(total_value, prev_value)

    # ===============================
    # Alleen loggen bij BUY of SELL
    # ===============================
    if action in ["BUY", "SELL"]:
        trade_profit = total_value - prev_value
        print(
            f"{action} | Price={price:.2f} | Profit={trade_profit:.2f} USDT | "
            f"Total={total_value:.2f} USDT | BTC={portfolio['BTC']:.6f} | Epsilon={epsilon:.3f}"
        )

    # ===============================
    # Next state
    # ===============================
    next_row = df.iloc[(i + 1) % len(df)]
    next_price = next_row['close']
    next_state = [
        int(next_row['RSI14'] > 50),
        int(next_price > next_row['MA20']),
        int(next_row['MA20'] > next_row['MA50']),
        int(next_row['MACD'] > next_row['MACD_signal']),
        int(portfolio['BTC'] > 0)
    ]

    s = discretize_state(state)
    s_next = discretize_state(next_state)

    if s not in q_table:
        q_table[s] = {a:0 for a in actions}
    if s_next not in q_table:
        q_table[s_next] = {a:0 for a in actions}

    # ===============================
    # Q-learning update
    # ===============================
    q_table[s][action] = q_table[s][action] + alpha * (
        reward + gamma * max(q_table[s_next].values()) - q_table[s][action]
    )

    portfolio_values.append(total_value)

    # ===============================
    # Portfolio reset bij crash
    # ===============================
    if total_value < 500:
        portfolio = {'USDT': 1000, 'BTC': 0}
        print("Portfolio reset")

    # ===============================
    # Q-table opslaan elke 100 stappen
    # ===============================
    if i % 100 == 0:
        with open("q_table.pkl", "wb") as f:
            pickle.dump(q_table, f)
        print("Q-table opgeslagen")

    # ===============================
    # Epsilon decay & loop increment
    # ===============================
    epsilon = max(0.01, epsilon * 0.9995)
    i += 1
    time.sleep(0.01)
