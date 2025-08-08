import pandas as pd
import statsmodels.api as sm

# variables
KURTOSIS_WINDOW = "180D"
FAMA_FRENCH_FACTORS = '/Users/aleksandarglamocic/python_wu/petnica-compfin-2025-projekat/F-F_Research_Data_Factors.csv'

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
    # Load Fama-French factors
    factors = pd.read_csv(FAMA_FRENCH_FACTORS, skiprows=3)
    factors = factors.rename(columns={factors.columns[0]: 'Date'})
    factors = factors[factors['Date'].str.len() == 6]  # remove footer rows
    factors['Date'] = pd.to_datetime(factors['Date'], format='%Y%m')
    factors['month_year'] = factors['Date'].dt.to_period('M')

    # Keep only necessary columns and ensure consistent naming
    factors = factors[['month_year', 'Mkt-RF', 'SMB', 'HML', 'RF']]
    factors = factors.rename(columns={'Mkt-RF': 'MKT_RF'})  # rename to valid Python variable name

    # Make sure 'data' also has month_year as Period
    data['month_year'] = data['date'].dt.to_period('M')

    # Merge Fama-French factors with stock data
    result = pd.merge(data, factors, on='month_year', how='left')

    # Compute excess return
    result['excess_return'] = result['ret'] - result['RF']

    # Prepare regression variables
    result = result.dropna(subset=['excess_return', 'MKT_RF', 'SMB', 'HML', 'kurtosis'])
    X = result[['MKT_RF', 'SMB', 'HML', 'kurtosis']]
    X = sm.add_constant(X)
    y = result['excess_return']

    # Run regression
    model = sm.OLS(y, X).fit()
    print(model.summary())



def rate_portfolio(portfolio: pd.DataFrame):
    # ovaj portfolio za mjesec n+1
    fama_french(portfolio)

# calculate kurtosis
df = calculate_kurtosis(load_csv('/Users/aleksandarglamocic/python_wu/petnica-compfin-2025-projekat/crsp.csv'))
df = df.dropna(subset=['kurtosis'])

# Extract unique months
df['month_year'] = df['date'].dt.to_period('M')
months = df['month_year'].unique()

# Iterate over unique months
for month in months:
    month_data = df[df['month_year'] == month]
    # process_quantiles(month_data, rate_portfolio)



