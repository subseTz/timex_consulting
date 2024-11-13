### Importing necessary libraries

import MetaTrader5 as mt5
from datetime import date, datetime, timedelta
import pandas as pd
import numpy as np
np.set_printoptions(suppress=True)
import os
import time



### Connecting Python to MetaTrader5 

# display data on the MetaTrader 5 package
print("MetaTrader5 package author: ",mt5.__author__)
print("MetaTrader5 package version: ",mt5.__version__)
 
# establish connection to MetaTrader 5 terminal
if not mt5.initialize():
    print("initialize() failed, error code =",mt5.last_error())
    quit()
    
# login(
#    login,                    // account number
#    password="PASSWORD",      // password
#    server="SERVER",          // server name as it is specified in the terminal
#    timeout=TIMEOUT           // timeout
#    )

acc_number = 54093793
password = 'SQLPocketGuide@3690'
server = 'XPMT5-DEMO'

log = mt5.login(acc_number, password, server)

if log:
    print(f'Successfully connected to the {server} using the account #{acc_number}')
else:
    print(f'Failed to connect at account #{account}, error code: {mt5.last_error()}')



### Extracting data from a portfolio in real time. Timeframe = 1 minute (M1)

# today's date
data_to = datetime.today()
# subtract 3 days from today's date to get 'data_from'
data_from = data_to - timedelta(days=504)
print(f'From *{data_from}* to *{data_to}*\n')

# setting the ticker
stock = 'CMIG4'

df = mt5.copy_rates_range(stock, mt5.TIMEFRAME_D1, data_from, data_to)
df = pd.DataFrame(df) # selecting 'time' and transforming that variable
df['time'] = pd.to_datetime(df['time'], unit='s') # setting index as 'time'
df.set_index('time', inplace=True)
print(f'Actual {stock} closing price at time *{df.index[-1]}* is: $ {df["close"].iloc[-1]}')


### Getting the returns
df['daily_returns'] = df['close'].pct_change()
df = df.dropna(); df

### Calculating some Quantitative Indicators
# Sharpe Ratio = Mean of Excess Returns / Sigmap, where:
#                                           Rp = Expected return of Portfolio. 
#                                           Rf = Risk-free rate.
#                                           Excess Returns = Rp - Rf 
#                                           Sigmap = Standard deviation of the portfolio's excess returns

# defining functions
def sharpe_ratio(returns, benchmark_returns):
    excess_returns = (returns - benchmark_returns)
    avg_excess_returns = np.mean(excess_returns)
    sigmap = np.std(excess_returns) 
    sharpe = avg_excess_returns / sigmap
    return sharpe
    
def annualized_sharpe_ratio(returns, benchmark_returns):
    excess_returns = (returns - benchmark_returns)
    avg_excess_returns = np.mean(excess_returns)
    sigmap = np.std(excess_returns) 
    sharpe = avg_excess_returns / sigmap
    annualized_sharpe = np.sqrt(252) * sharpe
    return annualized_sharpe

def riskfree_daily_rate(annual_rate):
    return (1 + annual_rate)**(1/252) - 1


#working on the calculations
rf = riskfree_daily_rate(0.1265)

sharpe = sharpe_ratio(df['daily_returns'], rf)
annual_sharpe = annualized_sharpe_ratio(df['daily_returns'], rf)

print(f'Sharpe Ratio of {stock} is {round(sharpe, 3)}\n')
print(f'The Annualized Sharpe Ratio of {stock} is {round(annual_sharpe, 3)}')



### Create a dataframe with 3 moving averages

def moving_average(data, window_size):
    cumsum = [0]
    moving_avg = []
    
    for i, x in enumerate(data, 1):
        cumsum.append(cumsum[i-1] + x)
        if i >= window_size:
            moving_avg.append((cumsum[i] - cumsum[i - window_size]) / window_size)

    return moving_avg

######
# Adding the moving averages to the DataFrame
df['mma21'] = df['close'].rolling(window=21).mean()
df['mma50'] = df['close'].rolling(window=50).mean()
df['mma80'] = df['close'].rolling(window=80).mean()

df = df.dropna()
print(df.tail(), '\n', '\n', '\n')

# # exporting to xlsx
# stock_path = os.path.join("C:\\Users\\subse\\Downloads", 'sharpe.xlsx')
# df.to_excel(stock_path, index=True)  # index=False remove a coluna de índices do DataFrame
# print(f'Exported data - {stock_path}')

df['mma21_trend'] = df['mma21'] > df['mma50']
df['mma50_trend'] = df['mma50'] > df['mma80']
df['mma80_trend'] = (df['mma80'] < df['mma50']) & (df['mma80'] < df['mma21'])
# Sendo,
#       True = Tendência de Alta
#       False = Tendência de Baixas

if df['mma21_trend'].iloc[-1] == True and df['mma50_trend'].iloc[-1] == True and df['mma80_trend'].iloc[-1] == True:
    print('Tendência forte de alta')

elif df['mma21_trend'].iloc[-1] == True and df['mma50_trend'].iloc[-1] == True and df['mma80_trend'].iloc[-1] == False:
    print('Tendência moderada de alta')

elif df['mma21_trend'].iloc[-1] == True and df['mma50_trend'].iloc[-1] == False and df['mma80_trend'].iloc[-1] == False:
    print('Mercado sem tendência')

elif df['mma21_trend'].iloc[-1] == True and df['mma50_trend'].iloc[-1] == False and df['mma80_trend'].iloc[-1] == True:
    print('Tendência fraca de alta')

elif df['mma21_trend'].iloc[-1] == False and df['mma50_trend'].iloc[-1] == False and df['mma80_trend'].iloc[-1] == False:
    print('Tendência forte de baixa')

elif df['mma21_trend'].iloc[-1] == False and df['mma50_trend'].iloc[-1] == False and df['mma80_trend'].iloc[-1] == True:
    print('Tendência moderada de baixa')

elif df['mma21_trend'].iloc[-1] == False and df['mma50_trend'].iloc[-1] == True and df['mma80_trend'].iloc[-1] == True:
    print('Mercado sem tendência')

elif df['mma21_trend'].iloc[-1] == False and df['mma50_trend'].iloc[-1] == True and df['mma80_trend'].iloc[-1] == False:
    print('Tendência fraca de baixa')
