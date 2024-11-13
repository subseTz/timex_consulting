import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf

# --- Streamlit App ---

st.title("Financial Data Analysis")

# Define the ticker symbol
tickerSymbol = st.text_input("Enter Ticker Symbol", "EURUSD=X")

# Get data
tickerData = yf.Ticker(tickerSymbol)
df_1d = tickerData.history(period='2y', interval='1d')

# Drop unnecessary columns
df_1d = df_1d.drop(['Volume', 'Dividends', 'Stock Splits'], axis=1)

# Calculate SMA 
df_1d['sma20'] = df_1d['Close'].rolling(window=20).mean() 

# Calculate returns as var (%)
df_1d["var_close"] = df_1d["Close"].pct_change(1) * 100
df_1d["var_sma"] = (1 - (df_1d['Close'] / df_1d['sma20'])) * 100 

# Z-Scores
df_1d['zscores_close'] = (df_1d['var_close'] - df_1d['var_close'].mean()) / df_1d['var_close'].std()
df_1d['zscores_sma'] = (df_1d['var_sma'] - df_1d['var_sma'].mean()) / df_1d['var_sma'].std()

# Remove NaN values
df_1d.dropna(subset=["var_close", "var_sma"], inplace=True)

# --- Plotting ---

fig, ax1 = plt.subplots(figsize=(12, 8))  # Create a single plot

ax1.set_title(f"Daily (1D) Time Series of {tickerSymbol}")
ax1.set_xlabel(f"Date")
ax1.set_ylabel(f"Close")

# Filter data for the past year for plotting
df_1d_plot = df_1d.last('1y')  
ax1.plot(df_1d_plot.index, df_1d_plot['Close'], label='Close')
ax1.plot(df_1d_plot.index, df_1d_plot['sma20'], label='SMA 20')

# Add vertical lines for signals
df_1d['POSITION'] = 'NONE'  # Initialize POSITION column
parameters = [1.618, 2, 3]

# Correct the loop to iterate through df_1d_plot
for i in parameters:
    for j in range(len(df_1d_plot)):  # Iterate through df_1d_plot
        if df_1d_plot['zscores_sma'].iloc[j] < -i:  # Short
            ax1.axvline(df_1d_plot.index[j], color='red', linestyle='--', linewidth=1, alpha=0.5)
            df_1d['POSITION'].loc[df_1d_plot.index[j]] = 'SHORT'
        if df_1d_plot['zscores_sma'].iloc[j] > i:  # Long
            ax1.axvline(df_1d_plot.index[j], color='green', linestyle='--', linewidth=1, alpha=0.5)
            df_1d['POSITION'].loc[df_1d_plot.index[j]] = 'LONG'

ax1.legend()
plt.tight_layout()

# Display the chart in Streamlit
st.pyplot(fig)

# Display the DataFrame in Streamlit
st.write(df_1d.sort_index(ascending=False))