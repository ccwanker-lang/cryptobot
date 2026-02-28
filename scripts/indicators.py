import pandas as pd
import numpy as np

def moving_average(series, period):
    """Return moving average van een Pandas Series"""
    return series.rolling(period).mean()

def rsi(df, period=14):
    delta = df['close'].diff()
    gain = (delta.where(delta>0,0)).rolling(period).mean()
    loss = (-delta.where(delta<0,0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100/(1+rs))

def bollinger_bands(df, period=20, num_std=2):
    ma = df['close'].rolling(period).mean()
    std = df['close'].rolling(period).std()
    upper = ma + num_std*std
    lower = ma - num_std*std
    return upper, lower

def ema(series, period=10):
    return series.ewm(span=period, adjust=False).mean()

def macd(df, fast=12, slow=26, signal=9):
    ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
    ema_slow = df['close'].ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    return macd_line, signal_line

def stochastic(df, k_period=14, d_period=3):
    low_min = df['low'].rolling(k_period).min()
    high_max = df['high'].rolling(k_period).max()
    k = 100*(df['close']-low_min)/(high_max-low_min)
    d = k.rolling(d_period).mean()
    return k, d
