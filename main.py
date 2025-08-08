import pandas as pd
import statsmodels.api as sm

# variables
KURTOSIS_WINDOW = "180D"
FAMA_FRENCH_FACTORS = 'F-F_Research_Data_Factors.csv'

def load_csv(path):
    src = pd.read_csv(path)

    # preprocessing
    src = src[['permno', 'ticker', 'comnam', 'date', 'prc', 'ret']]

    src['ret'] = pd.to_numeric(src['ret'], errors='coerce')
    src = src.dropna(subset=['ret'])

    src['date'] = pd.to_datetime(src['date'], format='%Y%m%d')

    return src

def calculate_kurtosis(frame: pd.DataFrame):
    frame['kurtosis'] = None 

    for _, group in frame.groupby('permno'):
        k = group.set_index('date')['ret'].rolling(window=KURTOSIS_WINDOW).kurt()
        frame.loc[group.index, 'kurtosis'] = k.values

    return frame.dropna(subset=['kurtosis'])

def get_quantiles(data: pd.DataFrame, field):
    sorted_df = data.sort_values(by=field)
    return pd.qcut(sorted_df[field], q=10, labels=False)

def process_quantiles(data: pd.DataFrame, f):
    quantiles = get_quantiles(data, "kurtosis")

    for quantile in range(10):
        quantile_data = data[quantiles == quantile]
        f(quantile_data) 

def fama_french(data: pd.DataFrame):
    # Load Fama-French factors
    factors = pd.read_csv(FAMA_FRENCH_FACTORS)
    factors['Date'] = pd.to_datetime(factors['Date'], format='%Y%m')
    
    data['month_year'] = data['date'].dt.to_period('M')
    factors['month_year'] = factors['Date'].dt.to_period('M')

    print(factors.head())
    print(data.head())

    factors = factors[factors['month_year'].isin(data['month_year'])]

    print(factors.head())

    # Keep only necessary columns and ensure consistent naming
    factors = factors[['month_year', 'MKT_RF', 'SMB', 'HML', 'RF']]

    print(factors.head())
    # Adjust scale of factors
    factors['MKT_RF'] = factors['MKT_RF'] / 100
    factors['SMB'] = factors['SMB'] / 100
    factors['HML'] = factors['HML'] / 100
    factors['RF'] = factors['RF'] / 100

    # Merge Fama-French factors with stock data
    regression_in = pd.merge(data, factors, on='month_year', how='left')

    # Compute excess return
    regression_in['excess_return'] = regression_in['ret'] - regression_in['RF']

    print(regression_in.info())
    print(regression_in.head())

    # Prepare regression variables
    X = regression_in[['MKT_RF', 'SMB', 'HML', 'kurtosis']]
    X = X.apply(pd.to_numeric, errors='raise')
    X = sm.add_constant(X, has_constant='add')

    print(X.head())

    y = pd.to_numeric(regression_in['excess_return'], errors='raise')

    # Run regression
    model = sm.OLS(y, X).fit()
    print(model.summary())


def rate_portfolio(portfolio: pd.DataFrame):
    # ovaj portfolio za mjesec n+1
    fama_french(portfolio)

# calculate kurtosis
df = calculate_kurtosis(load_csv('crsp.csv'))

# Extract unique months
df['month_year'] = df['date'].dt.to_period('M')
df = df[df['month_year'] >= pd.Period('1926-07', freq='M')]
months = df['month_year'].unique()

# Iterate over unique months
for month in months:
    month_data = df[df['month_year'] == month]
    # process_quantiles(month_data, rate_portfolio)

month_data = df[df['month_year'] == months[1]]
quantiles = get_quantiles(month_data, "kurtosis")
print(fama_french(month_data[quantiles == 9]))
