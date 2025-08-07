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
    frame['kurtosis'] = None 

    for _, group in frame.groupby('permno'):
        k = group.set_index('date')['ret'].rolling(window=kurtosis_window).kurt()
        frame.loc[group.index, 'kurtosis'] = k.values

    return frame

def sample_month(month: pd.DataFrame):
    sorted_df = month.sort_values(by='kurtosis')

    # Divide into 10 quantiles 
    quantiles = pd.qcut(sorted_df['kurtosis'], q=10, labels=False)

    return quantiles

# calculate kurtosis
df = calculate_kurtosis(load_csv('crsp.csv'))
df = df.dropna(subset=['kurtosis'])

# Extract unique months
df['month_year'] = df['date'].dt.to_period('M')
unique_months = df['month_year'].unique()

# Iterate over unique months
for month in unique_months:
    month_data = df[df['month_year'] == month]
    quantiles = sample_month(month_data)

    # Iterate over each quantile
    for quantile in range(10):
        quantile_data = month_data[quantiles == quantile]
        print(f"Month: {month}, Quantile: {quantile}")
        print(quantile_data)  # Replace with your desired operation

