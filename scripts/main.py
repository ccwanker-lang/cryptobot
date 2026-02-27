#!/usr/bin/env python3
import ccxt
import pandas as pd
import time
from indicators import moving_average, rsi, bollinger_bands
from trading_ai import reward_function

# Config inladen
import json
with open("configs/config.json") as f:
    config = json.load(f)

# Binance testnet
exchange = ccxt.binance({
    'apiKey': config["binance"]["api_key"],
    'secret': config["binance"]["api_secret"],
    'enableRateLimit': True,
})
exchange.set_sandbox_mode(True)

# Portefeuille simulatie
portfolio = {'USDT': 1000, 'BTC': 0}

# Historische data ophalen (OHLCV)
ohlcv = exchange.fetch_ohlcv('BTC/USDT', '1m', limit=100)
df = pd.DataFrame(ohlcv, columns=['timestamp','open','high','low','close','volume'])

# Indicatoren berekenen
df['MA20'] = moving_average(df, 20)
df['RSI14'] = rsi(df, 14)
df['BB_upper'], df['BB_lower'] = bollinger_bands(df, 20)

# Simpele AI loop
for i in range(20, len(df)):
    state = df.iloc[i][['close','MA20','RSI14','BB_upper','BB_lower','volume']]
    
    # Simpele rule-based “AI” voor nu
    if state['close'] > state['BB_upper']:
        action = 'SELL'
    elif state['close'] < state['BB_lower']:
        action = 'BUY'
    else:
        action = 'HOLD'
    
    # Trade simuleren
    trade = {'amount': portfolio['USDT']*0.1, 'profit': 0, 'too_soon': False}
    if action == 'BUY':
        trade['profit'] = 0  # later echte RL reward
        portfolio['BTC'] += trade['amount']/state['close']
        portfolio['USDT'] -= trade['amount']
    elif action == 'SELL':
        trade['profit'] = portfolio['BTC'] * state['close'] - trade['amount']
        portfolio['USDT'] += portfolio['BTC'] * state['close']
        portfolio['BTC'] = 0
    
    # Reward berekenen
    r = reward_function(portfolio['USDT'] + portfolio['BTC']*state['close'], trade)
    print(f"{i}: Action={action}, Reward={r}, Portfolio={portfolio}")
    
    time.sleep(1)
