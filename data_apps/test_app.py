import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import yfinance as yf

# --- Streamlit App ---
st.set_page_config(layout="wide")  # Set the page layout to wide mode
st.title("Financial Data Analysis")

# Define the ticker symbol
tickerSymbol = st.text_input("Enter Ticker Symbol based on Yahoo Finance", "EURUSD=X")

# Get data
tickerData = yf.Ticker(tickerSymbol)
df_1d = tickerData.history(period='2y', interval='1d')

# Drop unnecessary columns
df_1d = df_1d.drop(['Volume', 'Dividends', 'Stock Splits'], axis=1)

# --- Input for SMA and Bollinger Bands ---
sma_window = st.number_input("SMA Window", min_value=20, value=20)
bb_window = st.number_input("Bollinger Bands Window", min_value=20, value=50)

# Calculate SMA 
df_1d[f'sma{sma_window}'] = df_1d['Close'].rolling(window=sma_window).mean() 

# Calculate returns as var (%)
df_1d["returns"] = df_1d["Close"].pct_change() * 100
df_1d[f"returns_sma{sma_window}"] = (1 - (df_1d['Close'] / df_1d[f'sma{sma_window}'])) * 100

# Z-Scores
df_1d['zscores_close'] = (df_1d['returns'] - df_1d['returns'].mean()) / df_1d['returns'].std()
df_1d[f'zscores_sma{sma_window}'] = (df_1d[f'returns_sma{sma_window}'] - df_1d[f'returns_sma{sma_window}'].mean()) / df_1d[f'returns_sma{sma_window}'].std()

# Remove NaN values
df_1d.dropna(subset=["returns", f'returns_sma{sma_window}'], inplace=True)

# --- Calculate Bollinger Bands ---
df_1d[f'sma{bb_window}'] = df_1d['Close'].rolling(window=bb_window).mean()
df_1d[f'std{bb_window}'] = df_1d['Close'].rolling(window=bb_window).std()
df_1d[f'upper_ci{bb_window}'] = df_1d[f'sma{bb_window}'] + (2 * df_1d[f'std{bb_window}'])
df_1d[f'lower_ci{bb_window}'] = df_1d[f'sma{bb_window}'] - (2 * df_1d[f'std{bb_window}'])

# --- Plotting with Plotly ---

# Filter data for the past year for plotting
df_1d_plot = df_1d.copy()

# Create Plotly figure
fig = go.Figure()

# Close price line
fig.add_trace(go.Scatter(x=df_1d_plot.index, y=df_1d_plot['Close'], 
                         mode='lines', name='Close', line=dict(color='blue')))

# SMA line
fig.add_trace(go.Scatter(x=df_1d_plot.index, y=df_1d_plot[f'sma{sma_window}'], 
                         mode='lines', name=f'SMA {sma_window}', line=dict(color='orange')))

# Bollinger Bands
fig.add_trace(go.Scatter(x=df_1d_plot.index, y=df_1d_plot[f'upper_ci{bb_window}'], 
                         mode='lines', name=f'Upper Bollinger Band ({bb_window})', 
                         line=dict(color='gray', width=1)))
fig.add_trace(go.Scatter(x=df_1d_plot.index, y=df_1d_plot[f'lower_ci{bb_window}'], 
                         mode='lines', name=f'Lower Bollinger Band ({bb_window})', 
                         line=dict(color='gray', width=1)))

# Signals (using the selected SMA window)
df_1d['position'] = 'NONE'  # Initialize POSITION column
parameters = [1.618, 2, 3]

for i in parameters:
    for j in range(len(df_1d_plot)):
        if df_1d_plot[f'zscores_sma{sma_window}'].iloc[j] < -i:  # Short
            fig.add_vline(x=df_1d_plot.index[j], line_width=0.7, line_dash="dash", line_color="red", opacity=0.5)
            df_1d['position'].loc[df_1d_plot.index[j]] = 'SHORT'
        if df_1d_plot[f'zscores_sma{sma_window}'].iloc[j] > i:  # Long
            fig.add_vline(x=df_1d_plot.index[j], line_width=0.7, line_dash="dash", line_color="green", opacity=0.5)
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
df_st = df_1d[['Open', 'High', 'Low', 'Close', 'returns', f'zscores_sma{sma_window}', 'position']]
st.write(df_st.sort_index(ascending=False))