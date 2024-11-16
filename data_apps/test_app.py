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

### Daily Data
#========================================================================================
# Get Daily data
tickerData = yf.Ticker(tickerSymbol)
df_1d = tickerData.history(period='2y', interval='1d')

# Drop unnecessary columns
df_1d = df_1d.drop(['Volume', 'Dividends', 'Stock Splits'], axis=1)

# --- Input for SMA and Bollinger Bands ---
sma_window = st.number_input("SMA Window", min_value=20, value=50)
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
parameters = [2, 3]

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
    title=f"Timex Z-Score Mean Reversal Model for {tickerSymbol}",
    xaxis_title="Date",
    yaxis_title="Close Price",
    xaxis_rangeslider_visible=True  # Add a range slider for zooming
)

# Display the chart in Streamlit
st.plotly_chart(fig, use_container_width=True)


### Hourly Data
#========================================================================================
# Get Hourly data
tickerData_1h = yf.Ticker(tickerSymbol)
df_1h = tickerData.history(period='2y', interval='1h')

# Drop unnecessary columns
df_1h = df_1h.drop(['Volume', 'Dividends', 'Stock Splits'], axis=1)

# --- Input for SMA and Bollinger Bands ---
sma_window_1h_1h = st.number_input("SMA Window", min_value=20, value=50)
bb_window_1h = st.number_input("Bollinger Bands Window", min_value=20, value=50)

# Calculate SMA 
df_1h[f'sma{sma_window_1h_1h}'] = df_1h['Close'].rolling(window=sma_window_1h).mean() 

# Calculate returns as var (%)
df_1h["returns"] = df_1h["Close"].pct_change() * 100
df_1h[f"returns_sma{sma_window_1h_1h}"] = (1 - (df_1h['Close'] / df_1h[f'sma{sma_window_1h_1h}'])) * 100

# Z-Scores
df_1h['zscores_close'] = (df_1h['returns'] - df_1h['returns'].mean()) / df_1h['returns'].std()
df_1h[f'zscores_sma{sma_window_1h}'] = (df_1h[f'returns_sma{sma_window_1h}'] - df_1h[f'returns_sma{sma_window_1h}'].mean()) / df_1h[f'returns_sma{sma_window_1h}'].std()

# Remove NaN values
df_1h.dropna(subset=["returns", f'returns_sma{sma_window_1h}'], inplace=True)

# --- Calculate Bollinger Bands ---
df_1h[f'sma{bb_window}'] = df_1h['Close'].rolling(window=bb_window).mean()
df_1h[f'std{bb_window}'] = df_1h['Close'].rolling(window=bb_window).std()
df_1h[f'upper_ci{bb_window}'] = df_1h[f'sma{bb_window}'] + (2 * df_1h[f'std{bb_window}'])
df_1h[f'lower_ci{bb_window}'] = df_1h[f'sma{bb_window}'] - (2 * df_1h[f'std{bb_window}'])

# --- Plotting with Plotly ---

# Filter data for the past year for plotting
df_1h_plot = df_1h.copy()

# Create Plotly figure
fig = go.Figure()

# Close price line
fig.add_trace(go.Scatter(x=df_1h_plot.index, y=df_1h_plot['Close'], 
                         mode='lines', name='Close', line=dict(color='blue')))

# SMA line
fig.add_trace(go.Scatter(x=df_1h_plot.index, y=df_1h_plot[f'sma{sma_window_1h}'], 
                         mode='lines', name=f'SMA {sma_window_1h}', line=dict(color='orange')))

# Bollinger Bands
fig.add_trace(go.Scatter(x=df_1h_plot.index, y=df_1h_plot[f'upper_ci{bb_window}'], 
                         mode='lines', name=f'Upper Bollinger Band ({bb_window})', 
                         line=dict(color='gray', width=1)))
fig.add_trace(go.Scatter(x=df_1h_plot.index, y=df_1h_plot[f'lower_ci{bb_window}'], 
                         mode='lines', name=f'Lower Bollinger Band ({bb_window})', 
                         line=dict(color='gray', width=1)))

# Signals (using the selected SMA window)
df_1h['position'] = 'NONE'  # Initialize POSITION column
parameters = [2, 3]

for i in parameters:
    for j in range(len(df_1h_plot)):
        if df_1h_plot[f'zscores_sma{sma_window_1h}'].iloc[j] < -i:  # Short
            fig.add_vline(x=df_1h_plot.index[j], line_width=0.7, line_dash="dash", line_color="red", opacity=0.5)
            df_1h['position'].loc[df_1h_plot.index[j]] = 'SHORT'
        if df_1h_plot[f'zscores_sma{sma_window_1h}'].iloc[j] > i:  # Long
            fig.add_vline(x=df_1h_plot.index[j], line_width=0.7, line_dash="dash", line_color="green", opacity=0.5)
            df_1h['position'].loc[df_1h_plot.index[j]] = 'LONG'

# Update layout
fig.update_layout(
    title=f"Timex Z-Score Mean Reversal Model for {tickerSymbol} - 1H",
    xaxis_title="Date",
    yaxis_title="Close Price",
    xaxis_rangeslider_visible=True  # Add a range slider for zooming
)






# Display the DataFrame in Streamlit
df_st = df_1d[['Open', 'High', 'Low', 'Close', 'returns', f'zscores_sma{sma_window}', 'position']]
st.write(f"Dataframe of Daily (1D) values of {tickerSymbol}")
st.write(df_st.sort_index(ascending=False))