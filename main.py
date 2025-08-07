import pandas as pd

# variables
kurtosis_window = "180D"

# preprocessing
src = pd.read_csv('crsp.csv')
src = src[['permno', 'ticker', 'comnam', 'date', 'prc', 'ret']]
src['date'] = pd.to_datetime(src['date'], format='%Y%m%d')
src = src.sort_values(by=['permno', 'date'])

# group by stock
grouped = src.groupby('permno')

# calculate kurtosis
kurtosis = {}
for permno, group in grouped:
    group = group.set_index('date')
    kurtosis[permno] = group['ret'].rolling(window=kurtosis_window).kurt()