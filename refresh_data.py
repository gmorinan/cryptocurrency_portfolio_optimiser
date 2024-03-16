import subprocess
import json
import pandas as pd 
import os


# Path to your shell script
script_path = 'scripts/coingecko_top_250.sh'

# Execute the shell script
result = subprocess.run([script_path], capture_output=True, text=True, shell=True)

# Check if the script executed successfully
if result.returncode == 0:
    print("Script executed successfully!")
    # Optionally print the output
    print("Output:", result.stdout)
else:
    print("Script execution failed!")
    # Optionally print the error
    print("Error:", result.stderr)

with open('data/coingecko_top_250_raw.json', 'r', encoding='utf-8') as f:
    top_250_by_mcap = json.load(f)
with open('data/coingecko_top_250_ids.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join([c['id'] for c in top_250_by_mcap]))


# Path to your shell script
script_path = 'scripts/coingecko_detailed.sh'

# Execute the shell script
result = subprocess.run([script_path], capture_output=True, text=True, shell=True)

# Check if the script executed successfully
if result.returncode == 0:
    print("Script executed successfully!")
    # Optionally print the output
    print("Output:", result.stdout)
else:
    print("Script execution failed!")
    # Optionally print the error
    print("Error:", result.stderr)


# prices 
from datetime import datetime

def convert_unix_ts_to_date(unix_ts):
    dt_object = datetime.fromtimestamp(unix_ts / 1e3)
    return dt_object.strftime('%Y-%m-%d')

def process_prices_json(filename):
    prices = df.from_dict(json.load(open(f'data/prices/{filename}', 'r')))
    prices.index = prices['prices'].map(lambda x: x[0])
    prices.index = prices.index.map(convert_unix_ts_to_date)
    prices.index.name = 'date'
    for col in prices.columns:
        prices[col] = prices[col].map(lambda x: x[1])
    prices['coin'] =  filename.split('.')[0]
    prices = prices[~prices.index.duplicated(keep='first')]
    return prices

prices = pd.concat([
    process_prices_json(file)
    for file in os.listdir('data/prices')
])

current_mcaps = prices.loc['2024-03-16'].set_index('coin')['market_caps']


# process categories
df = pd.DataFrame.from_records(
    [
        json.loads(open(f'data/categories_processed/{file}', 'r').replace('\n','').read())
        for file in os.listdir('data/categories_processed')
    ]
)[['id','symbol','name','asset_platform_id','market_cap_rank','categories']]
df = df.join(current_mcaps, on='id').sort_values('market_caps', ascending=False)

# save full table
df.to_csv('data/asset_summary.csv', index=False)
# save categories
df[['id','categories']].explode('categories').groupby('categories')['id'].apply(list).to_csv('data/asset_categories.csv')

# get groupings
all_cat = df.explode('categories').groupby('categories')['market_caps'
    ].agg(['count','sum']).sort_values('sum', ascending=False)
all_cat = all_cat[all_cat['count']>=3]

# manually set groupings based on analysis
category_grouping_filters = {
    'portfolio': ['Portfolio', 'Binance'],
    'ecosystem': ['Ecosystem'],
    'exclude': ['FTX Holdings', 
                'Alleged SEC Securities', 
                'Decentralized Exchange (DEX)',
                'Exchange-based Tokens',
                'USD Stablecoin',
                'Dog-Themed Coins'
                ],
    'groupings_1': [
                'Layer 1 (L1)',
                'Layer 2 (L2)',
                'Cryptocurrency',
                'Smart Contract Platform',
                'Stablecoins',
                'Centralized Exchange (CEX)',
                'Decentralized Finance (DeFi)',
                'NFT',
                'Meme'
    ],
    'groupings_2':[
                'Proof of Work (PoW)',
                'Proof of Stake (PoS)',
                'Infrastructure',
                'Governance',
                'Protocol',
                'Metaverse',
                'Gaming (GameFi)',
                'Liquid Staking Tokens',
                'DePIN',
                'Artificial Intelligence (AI)',
                'Storage',
                'Yield Farming',
                'Zero Knowledge (ZK)',
                'Rollup',
    ]
}
def substring_filter(x, substrings):
    return any(substring in x for substring in substrings)

category_groupings = {cat: all_cat[all_cat.index.map(lambda x: substring_filter(x, filters))].index.to_list()
 for cat,filters in category_grouping_filters.items()
 }

with open('data/category_groupings.json', 'w', encoding='utf-8') as f:
    json.dump(category_groupings, f, ensure_ascii=False, indent=4)