# main app
# >>> streamlit run app.py

import pandas as pd
import numpy as np
import streamlit as st
import streamlit.components.v1 as components
from src.optimiser import solver, valid_input_weights
from src.processing import process_price_data, process_coin_metadata

### Functions and option dicts ####

mode_option_dict = {
    "Keep it simple plz": 'data/category_groupings_simple.json'
}
mcap_dict = {
    "Large market caps only": ["XL Market Cap", "Large Market Cap"],
    "Medium or large caps is fine by me": ["XL Market Cap", "Large Market Cap", "Medium Market Cap"],
    "Will consider small (within reason)": ["XL Market Cap", "Large Market Cap", "Medium Market Cap", "Small Market Cap"],
}
risk_level_values = {
    'High': 0.05,
    'Medium': 0.005,
    'Low': 0.0005
}


def fetch_data(mode, mcap, investor_type):
    category_groupings_path = mode_option_dict.get(mode, 'data/category_groupings.json')
    mcap_options = mcap_dict.get(mcap, ["XL Market Cap", "Large Market Cap", "Medium Market Cap", "Small Market Cap", "XS Market Cap"])

    mu_expected_return, sigma_covariance, df_prices, to_drop = process_price_data()
    
    (df_meta, dct_category_groupings, dct_coin_category, lst_assets, lst_categories
    ) = process_coin_metadata(to_drop=to_drop,
                              mcap_option=mcap_options,
                            category_groupings_path=category_groupings_path)
    
    weights_categories = {
            grouping: {cat: [0.0, 1.0] for cat in categories}
         for grouping, categories in dct_category_groupings.items()
    }
    if investor_type == "Trad-fi":
        for key, vals in {"Stablecoins": [0.2, 1.0], 
                        "Centralized Exchange (CEX)": [0.2, 1.0],
                        "Decentralized Finance (DeFi)": [0.0, 0.0],
                        "NFT": [0.0, 0.0],
                        "Meme": [0.0, 0.0]}.items():
            if key in weights_categories['Category']:
                weights_categories['Category'][key] = vals

    if investor_type == "ETH-maxi":
        for key, vals in {"Layer 2 (L2)": [0.3, 1.0], 
                        "Centralized Exchange (CEX)": [0.0, 0.0],
                        "NFT": [0.0, 1.0],
                        "Meme": [0.0, 1.0]}.items():
            if key in weights_categories['Category']:
                weights_categories['Category'][key] = vals
            weights_categories['Ecosystem']['Ethereum Ecosystem'] = [0.8, 1.0]

    if investor_type == "Woof!":
        for key, vals in {"Stablecoins": [0.0, 0.0], 
                        "Centralized Exchange (CEX)": [0.0, 0.0],
                        "NFT": [0.2, 1.0],
                        "Meme": [0.5, 1.0]}.items():
            if key in weights_categories['Category']:
                weights_categories['Category'][key] = vals

    return {
        "mu_expected_return": mu_expected_return,
        "sigma_covariance": sigma_covariance,
        "df_prices": df_prices,
        "df_meta": df_meta,
        "dct_category_groupings": dct_category_groupings,
        "dct_coin_category": dct_coin_category,
        "lst_assets": lst_assets,
        "lst_categories": lst_categories,
        "name_dict": df_meta['name'].to_dict(),
        "weights_assets": {asset: [0.0, 1.0] for asset in lst_assets},
        "weights_categories": {
            grouping: {cat: [0.0, 1.0] for cat in categories}
            for grouping, categories in dct_category_groupings.items()
        },
        "weights_categories":weights_categories
    }


def solve_function():
    allocation = solver(
        lst_assets=st.session_state.fetched_data["lst_assets"],
        mu_expected_return=st.session_state.fetched_data["mu_expected_return"],
        sigma_covariance=st.session_state.fetched_data["sigma_covariance"],
        dct_coin_category=st.session_state.fetched_data["dct_coin_category"],
        dct_category_groupings=st.session_state.fetched_data["dct_category_groupings"],
        weights_assets=st.session_state.fetched_data["weights_assets"],
        weights_categories=st.session_state.fetched_data["weights_categories"],
        name_dict=st.session_state.fetched_data['name_dict'],
        n_max_assets=st.session_state.max_assets,
        portfolio_risk_level=risk_level_values[st.session_state.risk_level]
    )

    st.write("Solve function executed.")
    st.write("Your portfolio:", allocation.to_frame()) 
    return allocation


### INITIAL SETUP ###

st.set_page_config(page_title='Crypto Portfolio Optimiser', page_icon="🌙")

st.markdown(""" <style> 
        #MainMenu {visibility: hidden;} 
        footer {visibility: hidden;} 
        </style> """, unsafe_allow_html=True)

padding = 0
st.markdown(f""" <style>
    .reportview-container .main .block-container{{
        padding-top: {padding}rem;
        padding-right: {padding}rem;
        padding-left: {padding}rem;
        padding-bottom: {padding}rem;
    }} </style> """, unsafe_allow_html=True)

st.markdown('# Crypto Portfolio Optimiser')

# sidebar
st.sidebar.markdown('### Important config')

mode = st.sidebar.radio("Number of options:", ("Keep it simple plz", "Give me MAX options"))

mcap = st.sidebar.radio("Type of assets:", ("Large market caps only", 
                                              "Medium or large caps is fine by me", 
                                              "Will consider small (within reason)",
                                              "I will invest in literally anything"),
                                index=1)

risk_level = st.sidebar.radio(
        "My risk tolerance is:", ("Low", "Medium", "High"), index=1)

n_assets = st.sidebar.radio("Number number of assets in portfolio:", 
                            (3, 5, 7, 10), index=1)

investor_type = st.sidebar.radio("I would describe my investment strategy as:", (
    "Default",
    "ETH-maxi",
    "Trad-fi",
    "Woof!"
))



show_clicked = st.sidebar.button("Show me which assets fall into each category")
# Check if "Solve" was clicked and call the solve_function
if show_clicked:
    st.markdown('#### Assets in each category')
    st.markdown('###### (double click on a cell to show all)')
    st.write(st.session_state.fetched_data["dct_coin_category"])



### Session state handling ###

if ('fetched_data' not in st.session_state 
    or st.session_state.selected_mode != mode 
    or st.session_state.selected_mcap != mcap
    or st.session_state.selected_investor != investor_type
    or st.session_state.max_assets != n_assets
    or st.session_state.risk_level != risk_level
):
    st.session_state.fetched_data = fetch_data(mode, mcap, investor_type)
    st.session_state.selected_mode = mode
    st.session_state.selected_mcap = mcap
    st.session_state.risk_level = risk_level
    st.session_state.selected_investor = investor_type
    st.session_state.max_assets = n_assets


### Create form ####
weights_assets = {asset: [0.0, 1.0] for asset in st.session_state.fetched_data["lst_assets"]}

name_dict = st.session_state.fetched_data['name_dict']
# add allocation forms for each category
for form_name, my_dict in st.session_state.fetched_data["weights_categories"].items():
    with st.expander(f"Weight allocation by {form_name} (click to expand)"):
        with st.form(form_name):
            col1, col2 = st.columns(2)
            col1.markdown("#### Minimum allocation")
            col2.markdown("#### Maximum allocation")
            updated_values = {}
            for key, values in my_dict.items():
    
                with col1:
                    num1a = st.number_input(f"{key} (min)", value=values[0])
                with col2:
                    num2a = st.number_input(f"{key} (max)", value=values[1])
                updated_values[key] = [num1a, num2a]
            
            # Form submission button
            submitted = st.form_submit_button("Submit")
            if submitted:
                if valid_input_weights(updated_values):
                    st.session_state.fetched_data["weights_categories"][form_name] = updated_values
                    st.write("Updated values for", form_name, ":", updated_values)
                else:
                    st.error("Minimum weights must sum to less than or equal to 1 (and ideally less that 0.7 if you want the optimiser to converge)")

# add constraint for each asset 
with st.expander(f"Constrain allocation by asset (click to expand)"):
    with st.form("Cryptocurrency constraints"):
        col1, col2 = st.columns(2)
        col1.markdown("#### Minimum allocation")
        col2.markdown("#### Maximum allocation")
        updated_values = {}
        for key, value in weights_assets.items():
            with col1:
                num1b = st.number_input(f"{name_dict[key]} (min)", value=0.0)
            with col2:
                num2b = st.number_input(f"{name_dict[key]} (max)", value=1.0)
            updated_values[key] = [num1b, num2b]
        
        # Form submission button
        submitted = st.form_submit_button("Submit")
        if submitted:
            if valid_input_weights(updated_values):
                weights_assets = updated_values
                st.write("Updated values for assets:", updated_values)
            else:
                st.error("Minimum weights must sum to less than or equal to 1 (and ideally less that 0.7 if you want the optimiser to converge)")


solve_clicked = st.button("Optimise Portfolio")

# Check if "Solve" was clicked and call the solve_function
if solve_clicked:
    solve_function()
