import yfinance as yf
import pandas as pd
import numpy as np
from itertools import product
from tqdm import tqdm

# Parameters
TICKER = 'TSLA'
start_date = '2020-01-01'
end_date = '2024-12-31'

# Fetching data
df = yf.download(TICKER, start=start_date, end=end_date)
df['Price'] = df.get('Adj Close', df['Close'])

# Function to calculate profit
def calculate_profit(df, short_window, long_window):
    df['Short_MA'] = df['Price'].rolling(window=short_window).mean()
    df['Long_MA'] = df['Price'].rolling(window=long_window).mean()

    df['Signal'] = np.where(df['Short_MA'] > df['Long_MA'], 1, -1)
    df['Prev_Signal'] = df['Signal'].shift(1)
    df['Confirmed_Signal'] = np.where(df['Signal'] != df['Prev_Signal'], df['Signal'], 0)

    capital = 10000  # Starting capital
    position = 0

    for i in range(1, len(df)):
        if df['Confirmed_Signal'].iloc[i] == 1 and position == 0:
            position = capital / df['Price'].iloc[i]  # Buy
            capital = 0
        elif df['Confirmed_Signal'].iloc[i] == -1 and position > 0:
            capital = position * df['Price'].iloc[i]  # Sell
            position = 0

    return capital if capital > 0 else position * df['Price'].iloc[-1]

# Grid Search for Optimization
short_ma_range = range(5, 51, 1)    # Short MA: 5 to 50 (step 1)
long_ma_range = range(20, 201, 1)   # Long MA: 20 to 200 (step 1)

total_combinations = len(short_ma_range) * len(long_ma_range)

best_profit = -np.inf
best_params = (0, 0)

# Using tqdm for progress tracking
for short_window, long_window in tqdm(product(short_ma_range, long_ma_range), total=total_combinations):
    if short_window >= long_window:
        continue  # Skip invalid combinations

    profit = calculate_profit(df.copy(), short_window, long_window)

    if profit > best_profit:
        best_profit = profit
        best_params = (short_window, long_window)

# Display Results
print(f"Optimal Short MA Window: {best_params[0]} days")
print(f"Optimal Long MA Window: {best_params[1]} days")
print(f"Maximum Profit: ${best_profit:.2f}")