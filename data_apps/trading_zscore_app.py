import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf

# --- Streamlit App ---
st.set_page_config(layout="wide")  # Set the page layout to wide mode
st.title("Financial Data Analysis")

# Define the ticker symbol
tickerSymbol = st.text_input("Enter Ticker Symbol based on Yahoo Finance", "EURUSD=X")

# --- Functions for calculations and plotting ---
def calculate_data(df, sma_window, bb_window):
    """Calculates SMA, Bollinger Bands, and z-scores."""
    df[f'sma{sma_window}'] = df['Close'].rolling(window=sma_window).mean()
    df["returns"] = df["Close"].pct_change() * 100
    df[f"returns_sma{sma_window}"] = (1 - (df['Close'] / df[f'sma{sma_window}'])) * 100
    df['zscores_close'] = (df['returns'] - df['returns'].mean()) / df['returns'].std()
    df[f'zscores_sma{sma_window}'] = (df[f'returns_sma{sma_window}'] - df[f'returns_sma{sma_window}'].mean()) / df[f'returns_sma{sma_window}'].std()

    df[f'sma{bb_window}'] = df['Close'].rolling(window=bb_window).mean()
    df[f'std{bb_window}'] = df['Close'].rolling(window=bb_window).std()
    df[f'upper_ci{bb_window}'] = df[f'sma{bb_window}'] + (2 * df[f'std{bb_window}'])
    df[f'lower_ci{bb_window}'] = df[f'sma{bb_window}'] - (2 * df[f'std{bb_window}'])
    return df

def plot_data(df, sma_window, bb_window, tickerSymbol, timeframe):
    """Plots the financial data with signals."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], 
                            mode='lines', name='Close', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=df.index, y=df[f'sma{sma_window}'], 
                            mode='lines', name=f'SMA {sma_window}', line=dict(color='orange')))
    fig.add_trace(go.Scatter(x=df.index, y=df[f'upper_ci{bb_window}'], 
                            mode='lines', name=f'Upper Bollinger Band ({bb_window})', 
                            line=dict(color='gray', width=1)))
    fig.add_trace(go.Scatter(x=df.index, y=df[f'lower_ci{bb_window}'], 
                            mode='lines', name=f'Lower Bollinger Band ({bb_window})', 
                            line=dict(color='gray', width=1)))

    df['position'] = 'NONE'  # Initialize POSITION column
    parameters = [2, 3]

    for i in parameters:
        for j in range(len(df)):
            if df[f'zscores_sma{sma_window}'].iloc[j] < -i:  # Short
                fig.add_vline(x=df.index[j], line_width=0.7, line_dash="dash", line_color="red", opacity=0.5)
                df['position'].loc[df.index[j]] = 'SHORT'
            if df[f'zscores_sma{sma_window}'].iloc[j] > i:  # Long
                fig.add_vline(x=df.index[j], line_width=0.7, line_dash="dash", line_color="green", opacity=0.5)
                df['position'].loc[df.index[j]] = 'LONG'

    fig.update_layout(
        title=f"Timex Z-Score Mean Reversal Model for {tickerSymbol} - {timeframe}",
        xaxis_title="Date",
        yaxis_title="Close Price",
        xaxis_rangeslider_visible=True  # Add a range slider for zooming
    )
    st.plotly_chart(fig, use_container_width=True)
    return df

# --- Daily Data ---
# Get Daily data
tickerData = yf.Ticker(tickerSymbol)
df_1d = tickerData.history(period='2y', interval='1d')
df_1d = df_1d.drop(['Volume', 'Dividends', 'Stock Splits'], axis=1)

# --- Header --- #
st.header("Daily (1D) Timeframe Calculations and Parameters", divider=True)

# --- Input for SMA and Bollinger Bands ---
sma_window_1d = st.number_input("SMA Window (1D)", min_value=20, value=50, key="sma_1d")
bb_window_1d = st.number_input("Bollinger Bands Window (1D)", min_value=20, value=50, key="bb_1d")

# Calculate and plot daily data
df_1d = calculate_data(df_1d, sma_window_1d, bb_window_1d)
df_1d = plot_data(df_1d, sma_window_1d, bb_window_1d, tickerSymbol, "1D")

# Display the DataFrame in Streamlit
df_st_1d = df_1d[['Open', 'High', 'Low', 'Close', 'returns', f'zscores_sma{sma_window_1d}', 'position']]
st.write(f"Dataframe of Daily (1H) values of {tickerSymbol}")
st.write(df_st_1d.sort_index(ascending=False).head(10))

# --- Hourly Data ---
# Get Hourly data
df_1h = tickerData.history(period='6mo', interval='1h')
df_1h = df_1h.drop(['Volume', 'Dividends', 'Stock Splits'], axis=1)

# --- Header --- #
st.header("Hourly (1H) Timeframe Calculations and Parameters", divider=True)

# --- Input for SMA and Bollinger Bands ---
sma_window_1h = st.number_input("SMA Window (1H)", min_value=20, value=20, key="sma_1h")
bb_window_1h = st.number_input("Bollinger Bands Window (1H)", min_value=20, value=20, key="bb_1h")

# Calculate and plot hourly data
df_1h = calculate_data(df_1h, sma_window_1h, bb_window_1h)
df_1h = plot_data(df_1h, sma_window_1h, bb_window_1h, tickerSymbol, "1H")

# Display the DataFrame in Streamlit
df_st_1h = df_1h[['Open', 'High', 'Low', 'Close', 'returns', f'zscores_sma{sma_window_1h}', 'position']]
st.write(f"Dataframe of Daily (1H) values of {tickerSymbol}")
st.write(df_st_1h.sort_index(ascending=False).head(10))