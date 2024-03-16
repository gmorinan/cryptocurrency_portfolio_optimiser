
import os
import json
import pandas as pd
import numpy as np
import cvxpy as cp
import ast

def solver(
        lst_assets: list,
        mu_expected_return: pd.Series,
        dct_coin_category: dict,
        dct_category_groupings: dict,
        weights_assets: dict,
        weights_categories: dict,
        n_max_assets: int = 10
) -> pd.Series:
    
    """
    Function to solve the portfolio optimisation problem.

    Parameters
    ----------
    lst_assets : list
        The list of assets.
    mu_expected_return : pd.Series
        The expected return of each asset.
    dct_coin_category : dict
        Which assets fall into which categories.
    dct_category_groupings : dict
        which categories fall into which groupings
    weights_assets : dict
        The minimum / maximum weights of each asset.
    weights_categories : dict
        The minimum / maximum weights of each category.
    n_max_assets : int
        The maximum number of assets to include.

    Returns
    -------
    pd.Series
        The optimised weights.
    """

    # set up primary variable 
    n_assets = len(mu_expected_return)
    weights = cp.Variable(n_assets)

    # set objective function based on maximising returns
    mu = mu_expected_return.values
    expected_return = mu.T @ weights
    objective = cp.Maximize(expected_return)

    # create initial baseline constraints 
    constraints = [cp.sum(weights) == 1, weights >= 0]

    # for each asset add constraint based on user inputs
    for asset, (w_min, w_max) in weights_assets.items():
        constraints.append(weights[lst_assets.index(asset)] >= w_min)
        constraints.append(weights[lst_assets.index(asset)] <= w_max)


    # for each category add constraint based on user inputs
    for grouping, categories in dct_category_groupings.items():
        for category in categories:
            category_assets = dct_coin_category[category]
            category_indices = [i for i, asset in enumerate(lst_assets) if asset in category_assets]
            category_weight_sum = cp.sum(weights[category_indices])
            constraints += [
                category_weight_sum >= weights_categories[grouping][category][0],
                category_weight_sum <= weights_categories[grouping][category][1]
            ]

    # solve the problem
    prob = cp.Problem(objective, constraints)
    prob.solve()

    # return the optimised weights
    optimized_weights = weights.value
    allocation = pd.Series(dict(zip(lst_assets, optimized_weights))).sort_values(ascending=False)
    return constrain_to_n_assets(allocation, n_max_assets=n_max_assets)


def constrain_to_n_assets(allocation: pd.Series, n_max_assets: int = 5):
    """
    Function to constrain the allocation to the top n_max_assets assets.

    Parameters
    ----------
    allocation : pd.Series
        The allocation of assets.
    n_max_assets : int
        The maximum number of assets to include.
    """
    allocation_final = allocation.head(n_max_assets).round(3)
    allocation_final = allocation_final[allocation_final > 0]
    return allocation_final * (1/allocation_final.sum())

def valid_input_weights(input_dict: dict):
    """
    Function to check if the input weights are valid.
    """
    return sum([v[0] for v in input_dict.values()]) <= 1.0
