import json
import pandas as pd
import ast
from config import market_cap_categories

market_cap_categories = {
    'XL Market Cap': 5e10,
    'Large Market Cap': 1e10,
    'Medium Market Cap': 5e9,
    'Small Market Cap': 1e9
}


def define_marketcap_category(market_cap: float):
    for key, value in market_cap_categories.items():
        if market_cap > value:
            return key
    return 'XS Market Cap'

def process_price_data(path: str ='data/prices.csv', window_size: int = 7, max_null_price: int = 50):

    # read and pivot
    df_prices = pd.read_csv(path, parse_dates=['date'])
    pivot_price = df_prices.pivot(index='date', columns='coin', values='prices')

    # drop any with too many null values
    n_null_price = pivot_price.isna().sum()
    min_null_price = max_null_price
    to_drop = n_null_price[n_null_price > min_null_price].index.to_list()
    pivot_price = pivot_price[[c for c in pivot_price.columns if c not in to_drop]]
    
    # compute expected return and covariance
    pct_change = pivot_price.diff(window_size) / pivot_price
    mu_expected_return = pct_change.mean()
    sigma_covariance = pct_change.cov()
    return mu_expected_return, sigma_covariance, df_prices, to_drop

def process_coin_metadata(
        to_drop: list,
        metadata_path = 'data/coin_metadata.csv',
        category_groupings_path = 'data/category_groupings.json',
):
    
    with open(category_groupings_path, 'r', encoding='utf-8') as f:
        dct_category_groupings = json.load(f)
    lst_categories = sorted(set(np.concatenate([list(v) for v in dct_category_groupings.values()])))

    df_meta = pd.read_csv(metadata_path)
    df_meta = df_meta[~df_meta['id'].isin(to_drop)]
    df_meta['categories'] = df_meta['categories'].apply(ast.literal_eval)
    df_meta['market_cap_category'] = df_meta['market_caps'].map(define_marketcap_category)

    df_categories = df_meta[['id','categories']].explode('categories')

    dct_coin_category = pd.concat([
        df_categories[df_categories['categories'].isin(lst_categories)].groupby('categories')['id'].apply(list),
        df_meta.groupby('market_cap_category')['id'].apply(list)
    ])

    lst_assets = sorted(df_meta['id'])
    lst_categories = sorted(dct_coin_category.keys())

    return df_meta.set_index('id'), dct_category_groupings, dct_coin_category, lst_assets, lst_categories