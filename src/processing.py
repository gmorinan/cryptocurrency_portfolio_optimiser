import json
import pandas as pd
import ast
import numpy as np
from typing import Tuple

market_cap_categories = {
    'XL Market Cap': 5e10,
    'Large Market Cap': 1e10,
    'Medium Market Cap': 5e9,
    'Small Market Cap': 1e9
}


def define_marketcap_category(market_cap: float) -> str:
    """
    Define the market cap category of a cryptocurrency based on its market cap.
    """
    for key, value in market_cap_categories.items():
        if market_cap > value:
            return key
    return 'XS Market Cap'

def process_price_data(path: str ='data/prices.csv', window_size: int = 7, max_null_price: int = 50
                       ) -> Tuple[pd.Series, pd.DataFrame, pd.DataFrame, list]:
    """
    Process the price data and return the expected return and covariance matrix.

    Parameters
    ----------
    path : str
        The path to the price data.
    window_size : int
        The window size for computing the expected return and covariance matrix.
    max_null_price : int
        The maximum number of null values allowed for a cryptocurrency (if below this
        we drop the asset)

    Returns
    -------
    mu_expected_return : pd.Series
        The expected return of each cryptocurrency.
    sigma_covariance : pd.DataFrame
        The covariance matrix of the cryptocurrencies.
    df_prices : pd.DataFrame
        The price data.
    to_drop : list
        The cryptocurrencies that have been dropped.    
    """

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
        mcap_option: list,
        metadata_path: str = 'data/coin_metadata.csv',
        category_groupings_path: str = 'data/category_groupings.json',
):
    """
    Process the coin metadata and return the expected return and covariance matrix.

    Parameters
    ----------
    to_drop : list
        The cryptocurrencies that need to be dropped.
    mcap_option : list
        The market cap categories to include.
    metadata_path : str
        The path to the coin metadata.
    category_groupings_path : str
        The path to the category groupings.

    Returns
    -------
    df_meta : pd.DataFrame
        The asset metadata.
    dct_category_groupings : dict
        which categories fall into which groupings
    dct_coin_category : dict
        Which assets fall into which categories
    lst_assets : list
        The list of assets.
    lst_categories : list
        The list of categories
    """
    
    # open the category groupings and get a full list of them
    with open(category_groupings_path, 'r', encoding='utf-8') as f:
        dct_category_groupings = json.load(f)
    lst_categories = sorted(set(np.concatenate([list(v) for v in dct_category_groupings.values()])))

    # read the asset metadata, drop any that need dropping
    df_meta = pd.read_csv(metadata_path)
    df_meta = df_meta[~df_meta['id'].isin(to_drop)]

    # processing categories and add market cap category
    df_meta['categories'] = df_meta['categories'].apply(ast.literal_eval)
    df_meta['market_cap_category'] = df_meta['market_caps'].map(define_marketcap_category)

    # additionall drop to only marketcaps the user is interested in
    df_meta = df_meta[df_meta['market_cap_category'].isin(mcap_option)]

    # make category table to create a dict of assets to categories
    df_categories = df_meta[['id','categories']].explode('categories')
    dct_coin_category = pd.concat([
        df_categories[df_categories['categories'].isin(lst_categories)].groupby('categories')['id'].apply(list),
        df_meta.groupby('market_cap_category')['id'].apply(list)
    ])

    # limit based on reduced set
    dct_category_groupings = {
        k:[v for v in vals if v in dct_coin_category.index] for k,vals in dct_category_groupings.items()}

    lst_assets = sorted(df_meta['id'])
    lst_categories = sorted(dct_coin_category.keys())

    return df_meta.set_index('id'), dct_category_groupings, dct_coin_category, lst_assets, lst_categories