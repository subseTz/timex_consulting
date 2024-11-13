import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf

# Define the ticker symbol for Bitcoin
tickerSymbol = 'EURUSD=X'

# Get data on this ticker
tickerData = yf.Ticker(tickerSymbol)

# Get the historical prices for this ticker
df = tickerData.history(period='2y', interval='1d')
# 'Date' is already datetime index

# Drop 'Volume', 'Dividends', 'Stock Splits'
df = df.drop(['Volume', 'Dividends', 'Stock Splits'], axis=1)

# Define the weights for the WMA
weights = np.arange(1, 21)  # This creates an array [1, 2, 3, ..., 20]

def calculate_wma(data):
    return np.sum(weights * data) / np.sum(weights)

def calculate_sma(data, close='Close', window=20):
    return data[close].rolling(20).mean()

# Calculate the WMA
df['WMA_21'] = df['Close'].rolling(20).apply(calculate_wma, raw=True)

# Calculating returns as var (%) Inferential Statistics
df["var_close"] = df["Close"].pct_change(1) * 100
df["var_wma"] = (1 - (df['Close'] / df['WMA_21'])) * 100 

# Z-Scores
df['Z-Scores_close'] = (df['var_close'] - df['var_close'].mean()) / df['var_close'].std()
df['Z-Scores_wma'] = (df['var_wma'] - df['var_wma'].mean()) / df['var_wma'].std()

# Remove NaN (important for plotting and calculations)
df.dropna(subset=["var_close", "var_wma"], inplace=True)

# --- Plotting ---

# 1. Line Chart with Moving Average
plt.figure(figsize=(15, 5))
plt.plot(df['Close'], label='Close Price')
plt.plot(df['WMA_21'], label='WMA (21)')
plt.title(f'{tickerSymbol} - Closing Price and WMA')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend()
plt.show()

# 2. Z-Scores Plots
df[['Z-Scores_close', 'Z-Scores_wma']].plot(figsize = (15, 5))
plt.title(f'{tickerSymbol} - Z-Scores (Close and WMA)')
plt.show()

# 3. Z-Scores Histograms
df[['Z-Scores_close', 'Z-Scores_wma']].hist(figsize = (15, 5), bins = 100)
plt.show()

# --- Z-Score Thresholds ---

parameters = [1.618, 2, 3]

for i in parameters:
    if i == 1.618:
        df_Zclose_1618_short = df[df['Z-Scores_close'] <= 1.618].sort_values(by = 'Z-Scores_close', ascending=False) 
        df_Zclose_1618_long = df[df['Z-Scores_close'] >= (-1 * 1.618)].sort_values(by = 'Z-Scores_close', ascending=True)
        
        df_Zwma_1618_long = df[df['Z-Scores_wma'] <= 1.618].sort_values(by = 'Z-Scores_wma', ascending=False)
        df_Zwma_1618_short = df[df['Z-Scores_wma'] >= (-1 * 1.618)].sort_values(by = 'Z-Scores_wma', ascending=True)
        
    elif i == 2:
        df_Zclose_2_short = df[df['Z-Scores_close'] <= 2].sort_values(by = 'Z-Scores_close', ascending=False) 
        df_Zclose_2_long = df[df['Z-Scores_close'] >= (-1 * 2)].sort_values(by = 'Z-Scores_close', ascending=True)
        
        df_Zwma_2_long = df[df['Z-Scores_wma'] <= 2].sort_values(by = 'Z-Scores_wma', ascending=False)
        df_Zwma_2_short = df[df['Z-Scores_wma'] >= (-1 * 2)].sort_values(by = 'Z-Scores_wma', ascending=True)
    
    else:
        df_Zclose_3_short = df[df['Z-Scores_close'] <= 3].sort_values(by = 'Z-Scores_close', ascending=False)
        df_Zclose_3_long = df[df['Z-Scores_close'] >= (-1 * 3)].sort_values(by = 'Z-Scores_close', ascending=True)
        
        df_Zwma_3_long = df[df['Z-Scores_wma'] <= 3].sort_values(by = 'Z-Scores_wma', ascending=False)
        df_Zwma_3_short = df[df['Z-Scores_wma'] >= (-1 * 3)].sort_values(by = 'Z-Scores_wma', ascending=True)

# --- Displaying DataFrames ---

print("df_Zclose_1618_short:")
print(df_Zclose_1618_short.head().to_markdown(index=False, numalign="left", stralign="left"))

print("\ndf_Zclose_1618_long:")
print(df_Zclose_1618_long.head().to_markdown(index=False, numalign="left", stralign="left"))

# ... (similarly print other DataFrames) ...


print(f''' *** LONG OPERATIONS (BUY) and SHORT OPERATIONS (SELL), Consider buying or selling *** {tickerSymbol} *** when the var(%) reaches the following levels. Keep in mind that POSITIVE number are for selling and NEGATIVE ones are for buying:
        
     *** Z-Score Definition: It is common to rescale a normal distribution so that the mean is 0 and the standard deviation is 1, which is known as *standard normal distribution*. This makes it easy to compare the spread of one normal distributiom to another normal distribution, even if they have different means and variances. 
         To sum up, the Z-Score expresses all x-values in terms of standard deviations. 
         
     *** Formula: Z = (x (data point) - mu (standard deviation)) / theta (standard deviation)
         
         Z-Score based on Closing of 1.618: *Sell* at variation (%) = {df_Zclose_1618_short['var_close'][0].round(4)}
         Z-Score based on Closing of 1.618: *Buy* at variation (%) = {df_Zclose_1618_long['var_close'][0].round(4)}
         
         Z-Score based on Closing of 2: *Sell* at variation (%) = {df_Zclose_2_short['var_close'][0].round(4)}
         Z-Score based on Closing of 2: *Buy* at variation (%) = {df_Zclose_2_long['var_close'][0].round(4)}
         
         Z-Score based on Closing of 3: *Sell* at variation (%) = {df_Zclose_3_short['var_close'][0].round(4)}
         Z-Score based on Closing of 3: *Buy* at variation (%) = {df_Zclose_3_long['var_close'][0].round(4)}
         
         ---------------------
         
         Z-Score based on Distance Closing x WMA of 1.618: *Sell* at variation (%) = {df_Zwma_1618_short['var_close'][0].round(4)}
         Z-Score based on Distance Closing x WMA of 1.618: *Buy* at variation (%) = {df_Zwma_1618_long['var_close'][0].round(4)}
         
         Z-Score based on Distance Closing x WMA of 2: *Sell* at variation (%) = {df_Zwma_2_short['var_close'][0].round(4)}
         Z-Score based on Distance Closing x WMA of 2: *Buy* at variation (%) = {df_Zwma_2_long['var_close'][0].round(4)}
         
         Z-Score based on Distance Closing x WMA of 3: *Sell* at variation (%) = {df_Zwma_3_short['var_close'][0].round(4)}
         Z-Score based on Distance Closing x WMA of 3: *Buy* at variation (%) = {df_Zwma_3_long['var_close'][0].round(4)}
         
         ''')