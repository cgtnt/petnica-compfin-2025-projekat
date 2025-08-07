import pandas as pd

# variables
kurtosis_window = "180D"

def load_csv(path):
    src = pd.read_csv(path)

    # preprocessing
    src = src[['permno', 'ticker', 'comnam', 'date', 'prc', 'ret']]
    src['date'] = pd.to_datetime(src['date'], format='%Y%m%d')
    src = src.sort_values(by=['permno', 'date'])

    return src

def calculate_kurtosis(frame: pd.DataFrame):
    # group by stock
    grouped = frame.groupby('permno')

    # calculate curtiosis
    frame['kurtosis'] = None 

    for _, group in frame.groupby('permno'):
        k = group.set_index('date')['ret'].rolling(window=kurtosis_window).kurt()
        frame.loc[group.index, 'kurtosis'] = k.values

    return frame

# calculate kurtosis
df = calculate_kurtosis(load_csv('crsp.csv'))