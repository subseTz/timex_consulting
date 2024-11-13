import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import yfinance as yf

# --- Streamlit App ---

st.title("Financial Data Analysis")

# Define the ticker symbol
tickerSymbol = st.text_input("Enter Ticker Symbol based on Yahoo Finance", "EURUSD=X")

# Get data
tickerData = yf.Ticker(tickerSymbol)
df_1d = tickerData.history(period='2y', interval='1d')

# Drop unnecessary columns
df_1d = df_1d.drop(['Volume', 'Dividends', 'Stock Splits'], axis=1)

# Calculate SMA 
df_1d['sma20'] = df_1d['Close'].rolling(window=20).mean() 

# Calculate returns as var (%)
df_1d["returns"] = df_1d["Close"].pct_change() * 100
df_1d["returns_sma"] = (1 - (df_1d['Close'] / df_1d['sma20'])) * 100

# Z-Scores
df_1d['zscores_close'] = (df_1d['returns'] - df_1d['returns'].mean()) / df_1d['returns'].std()
df_1d['zscores_sma'] = (df_1d['returns_sma'] - df_1d['returns_sma'].mean()) / df_1d['returns_sma'].std()

# Remove NaN values
df_1d.dropna(subset=["returns", "returns_sma"], inplace=True)

# --- Plotting with Plotly ---

# Filter data for the past year for plotting
df_1d_plot = df_1d.last('1y')

# Create Plotly figure
fig = go.Figure()

# Close price line
fig.add_trace(go.Scatter(x=df_1d_plot.index, y=df_1d_plot['Close'], 
                         mode='lines', name='Close', line=dict(color='blue')))

# SMA 20 line
fig.add_trace(go.Scatter(x=df_1d_plot.index, y=df_1d_plot['sma20'], 
                         mode='lines', name='SMA 20', line=dict(color='orange')))

# Signals
df_1d['position'] = 'NONE'  # Initialize POSITION column
parameters = [1.618, 2, 3]

for i in parameters:
    for j in range(len(df_1d_plot)):
        if df_1d_plot['zscores_sma'].iloc[j] < -i:  # Short
            fig.add_vline(x=df_1d_plot.index[j], line_width=1, line_dash="dash", line_color="red")
            df_1d['position'].loc[df_1d_plot.index[j]] = 'SHORT'
        if df_1d_plot['zscores_sma'].iloc[j] > i:  # Long
            fig.add_vline(x=df_1d_plot.index[j], line_width=1, line_dash="dash", line_color="green")
            df_1d['position'].loc[df_1d_plot.index[j]] = 'LONG'

# Update layout
fig.update_layout(
    title=f"Daily (1D) Time Series of {tickerSymbol}",
    xaxis_title="Date",
    yaxis_title="Close Price",
    xaxis_rangeslider_visible=True  # Add a range slider for zooming
)

# Display the chart in Streamlit
st.plotly_chart(fig, use_container_width=True)

# Display the DataFrame in Streamlit
df_st = df_1d[['Open', 'High', 'Low', 'Close', 'returns', 'zscores_close', 'zscores_sma', 'position']]
st.write(df_st.sort_index(ascending=False))

