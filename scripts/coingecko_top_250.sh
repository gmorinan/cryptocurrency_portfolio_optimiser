#!/bin/bash

# Fetch the API key from environment variables
APIKEY="${COINGECKO_API_KEY}"
if [ -z "$APIKEY" ]; then
  echo "COINGECKO_API_KEY environment variable is not set."
  exit 1
fi

URL="https://pro-api.coingecko.com/api/v3/coins/markets?vs_currency=USD&order=market_cap_desc&per_page=250&page=1&locale=en&precision=12&x_cg_pro_api_key=$APIKEY"

curl --silent --request GET --url "$URL" > data/coingecko_top_250_raw.json

# Inform the user
echo "Response saved to coingecko_top_250_raw.json"
