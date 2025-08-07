import pandas as pd

# variables
KURTOSIS_WINDOW = "180D"
FAMA_FRENCH_FACTORS = 'F-F_Research_Data_Factors.csv'

def load_csv(path):
    src = pd.read_csv(path)

    # preprocessing
    src = src[['permno', 'ticker', 'comnam', 'date', 'prc', 'ret']]
    src['date'] = pd.to_datetime(src['date'], format='%Y%m%d')
    src = src.sort_values(by=['permno', 'date'])

    return src

def calculate_kurtosis(frame: pd.DataFrame):
    frame['kurtosis'] = None 

    for _, group in frame.groupby('permno'):
        k = group.set_index('date')['ret'].rolling(window=KURTOSIS_WINDOW).kurt()
        frame.loc[group.index, 'kurtosis'] = k.values

    return frame

def get_quantiles(data: pd.DataFrame, field):
    sorted_df = data.sort_values(by=field)
    return pd.qcut(sorted_df[field], q=10, labels=False)

def process_quantiles(data: pd.DataFrame, f):
    quantiles = get_quantiles(data, "kurtosis")

    for quantile in range(10):
        quantile_data = month_data[quantiles == quantile]
        f(quantile_data) 

def fama_french(data: pd.DataFrame):
    df = pd.read_csv(FAMA_FRENCH_FACTORS)




def rate_portfolio(portfolio: pd.DataFrame):
    # ovaj portfolio za mjesec n+1
    fama_french(portfolio)

# calculate kurtosis
df = calculate_kurtosis(load_csv('crsp.csv'))
df = df.dropna(subset=['kurtosis'])

# Extract unique months
df['month_year'] = df['date'].dt.to_period('M')
months = df['month_year'].unique()

# Iterate over unique months
for month in months:
    month_data = df[df['month_year'] == month]
    process_quantiles(month_data, rate_portfolio)

