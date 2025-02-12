import streamlit as st # type: ignore
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Simulating stock price data
np.random.seed(42)
days = 200
prices = np.cumsum(np.random.randn(days)) + 100

# Streamlit app
st.title("💹 Quant Trading Game: Moving Average Crossover Strategy")

# User input for moving average window sizes
short_window = st.slider("Select Short Moving Average Window:", 2, 20, 5)
long_window = st.slider("Select Long Moving Average Window:", 10, 50, 20)

# Creating a DataFrame
df = pd.DataFrame({'Price': prices})
df['Short_MA'] = df['Price'].rolling(window=short_window).mean()
df['Long_MA'] = df['Price'].rolling(window=long_window).mean()

# Generating trading signals
df['Signal'] = 0  
df.loc[df['Short_MA'] > df['Long_MA'], 'Signal'] = 1  # Buy Signal
df.loc[df['Short_MA'] < df['Long_MA'], 'Signal'] = -1  # Sell Signal

def calculate_profit(df):
    capital = 10000  # Starting with $10,000
    position = 0
    for i in range(1, len(df)):
        if df['Signal'][i] == 1 and position == 0:  # Buy
            position = capital / df['Price'][i]
            capital = 0
        elif df['Signal'][i] == -1 and position > 0:  # Sell
            capital = position * df['Price'][i]
            position = 0
    return capital if capital > 0 else position * df['Price'].iloc[-1]

profit = calculate_profit(df)
st.metric("💰 Final Capital (Starting: $10,000)", f"${profit:.2f}")

# Plotting the stock price with moving averages and signals
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(df['Price'], label="Stock Price", color="black", linewidth=1)
ax.plot(df['Short_MA'], label=f"Short MA ({short_window} days)", linestyle="--", color="blue")
ax.plot(df['Long_MA'], label=f"Long MA ({long_window} days)", linestyle="--", color="red")
ax.scatter(df.index[df['Signal'] == 1], df['Price'][df['Signal'] == 1], marker="^", color="green", label="Buy Signal", alpha=1, s=100)
ax.scatter(df.index[df['Signal'] == -1], df['Price'][df['Signal'] == -1], marker="v", color="red", label="Sell Signal", alpha=1, s=100)
ax.set_title("Moving Average Crossover Strategy")
ax.set_xlabel("Days")
ax.set_ylabel("Stock Price")
ax.legend()
ax.grid()
st.pyplot(fig)

st.write("🎯 Try adjusting the moving averages and see how it affects your final capital! Can you optimize your strategy?")
