import pandas as pd
import numpy as np

def moving_average(df, n=20):
    return df['close'].rolling(n).mean()

def rsi(df, n=14):
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(n).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(n).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def bollinger_bands(df, n=20):
    ma = df['close'].rolling(n).mean()
    std = df['close'].rolling(n).std()
    upper = ma + 2*std
    lower = ma - 2*std
    return upper, lower
