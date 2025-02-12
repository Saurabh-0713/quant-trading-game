import streamlit as st  # type: ignore
import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

# Streamlit app
st.title("💹 Quant Trading Game: Moving Average Crossover Strategy with Real Stock Data")

# User input for stock ticker and date range
st.sidebar.header("Stock Data Settings")
ticker = st.sidebar.text_input("Enter Stock Ticker (e.g., TSLA, AAPL, MSFT):", value="TSLA")
start_date = st.sidebar.date_input("Start Date:", pd.to_datetime("2020-01-01"))
end_date = st.sidebar.date_input("End Date:", pd.to_datetime("2024-12-31"))

# Fetching real stock data
try:
    df = yf.download(ticker, start=start_date, end=end_date)
    if df.empty:
        st.error("No data found for the given ticker and date range.")
    else:
        # Check if 'Adj Close' exists, else fallback to 'Close'
        if 'Adj Close' in df.columns:
            df['Price'] = df['Adj Close']
        else:
            df['Price'] = df['Close']

        # User input for moving average window sizes
        short_window = st.slider("Select Short Moving Average Window:", 2, 20, 5)
        long_window = st.slider("Select Long Moving Average Window:", 10, 50, 20)

        # Calculating moving averages
        df['Short_MA'] = df['Price'].rolling(window=short_window).mean()
        df['Long_MA'] = df['Price'].rolling(window=long_window).mean()

        # Generating trading signals
        df['Signal'] = 0
        df.loc[df['Short_MA'] > df['Long_MA'], 'Signal'] = 1  # Buy Signal
        df.loc[df['Short_MA'] < df['Long_MA'], 'Signal'] = -1  # Sell Signal

        # Calculating profit
        def calculate_profit(df):
            capital = 10000  # Starting with $10,000
            position = 0
            for i in range(1, len(df)):
                if df['Signal'].iloc[i] == 1 and position == 0:  # Buy
                    position = capital / df['Price'].iloc[i]
                    capital = 0
                elif df['Signal'].iloc[i] == -1 and position > 0:  # Sell
                    capital = position * df['Price'].iloc[i]
                    position = 0
            return capital if capital > 0 else position * df['Price'].iloc[-1]

        profit = calculate_profit(df)
        st.metric("💰 Final Capital (Starting: $10,000)", f"${profit:.2f}")

        # Plotting the stock price with moving averages and signals
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(df['Price'], label=f"{ticker} Stock Price", color="black", linewidth=1)
        ax.plot(df['Short_MA'], label=f"Short MA ({short_window} days)", linestyle="--", color="blue")
        ax.plot(df['Long_MA'], label=f"Long MA ({long_window} days)", linestyle="--", color="red")
        ax.scatter(df.index[df['Signal'] == 1], df['Price'][df['Signal'] == 1], marker="^", color="green", label="Buy Signal", s=100)
        ax.scatter(df.index[df['Signal'] == -1], df['Price'][df['Signal'] == -1], marker="v", color="red", label="Sell Signal", s=100)

        ax.set_title(f"Moving Average Crossover Strategy for {ticker}")
        ax.set_xlabel("Date")
        ax.set_ylabel("Price")
        ax.legend()
        ax.grid()
        st.pyplot(fig)

        st.write("🎯 Adjust the moving averages and explore different stocks to optimize your strategy!")

except Exception as e:
    st.error(f"Error fetching data: {e}")
