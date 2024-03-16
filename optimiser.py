
import os
import json
import pandas as pd
import numpy as np
import cvxpy as cp
import ast

def solver(
        lst_assets: list,
        mu_expected_return: pd.Series,
        sigma_covariance: pd.DataFrame,
        dct_coin_category: dict,
        dct_category_groupings: dict,
        min_weights_assets: dict,
        max_weights_assets: dict,
        min_weights_categories: dict,
        max_weights_categories: dict,
        n_max_assets: int = 10
):

    n_assets = len(mu_expected_return)
    weights = cp.Variable(n_assets)

    mu = mu_expected_return.values
    sigma = sigma_covariance.values

    expected_return = mu.T @ weights
    objective = cp.Maximize(expected_return)

    constraints = [cp.sum(weights) == 1, weights >= 0]

    for asset, min_weight in min_weights_assets.items():
        constraints.append(weights[lst_assets.index(asset)] >= min_weight)

    for asset, max_weight in max_weights_assets.items():
        constraints.append(weights[lst_assets.index(asset)] <= max_weight)

    for grouping, categories in dct_category_groupings.items():
        for category in categories:
            category_assets = dct_coin_category[category]
            category_indices = [i for i, asset in enumerate(lst_assets) if asset in category_assets]
            category_weight_sum = cp.sum(weights[category_indices])
            constraints += [
                category_weight_sum >= min_weights_categories[grouping][category],
                category_weight_sum <= max_weights_categories[grouping][category]
            ]

    prob = cp.Problem(objective, constraints)
    prob.solve()

    optimized_weights = weights.value

    return pd.Series(dict(zip(lst_assets, optimized_weights))).sort_values(ascending=False)


def constrain_to_n_assets(allocation: pd.Series, n_max_assets: int = 5):
    allocation_final = allocation.head(n_max_assets).round(3)
    allocation_final = allocation_final[allocation_final > 0]
    return allocation_final * (1/allocation_final.sum())
