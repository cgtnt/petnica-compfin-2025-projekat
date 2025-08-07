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

src['kurtosis'] = None 

for permno, group in src.groupby('permno'):
    k = group.set_index('date')['ret'].rolling(window=kurtosis_window).kurt()
    src.loc[group.index, 'kurtosis'] = k.values
