#!/bin/bash

# Fetch the API key from environment variables
APIKEY="${COINGECKO_API_KEY}"
if [ -z "$APIKEY" ]; then
  echo "COINGECKO_API_KEY environment variable is not set."
  exit 1
fi

# Token list
#TOKENS=("bitcoin" "ethereum" "tether" "binancecoin" "solana" "staked-ether" "ripple" "usd-coin" "cardano" "dogecoin" "avalanche-2" "shiba-inu" "polkadot" "the-open-network" "chainlink" "tron" "matic-network" "wrapped-bitcoin" "uniswap" "bitcoin-cash" "near" "litecoin" "aptos" "internet-computer" "leo-token" "filecoin" "cosmos" "ethereum-classic" "dai" "render-token" "immutable-x" "hedera-hashgraph" "injective-protocol" "bittensor" "okb" "blockstack" "stellar" "crypto-com-chain" "the-graph" "optimism" "pepe" "vechain" "kaspa" "theta-token" "first-digital-usd" "sei-network" "mantle" "thorchain" "arbitrum" "fetch-ai" "maker" "celestia" "fantom" "monero" "lido-dao" "dogwifcoin" "gala" "algorand" "floki" "arweave" "rocket-pool-eth" "flow" "sui" "beam-2" "mantle-staked-ether" "jupiter-exchange-solana" "quant-network" "bonk" "aave" "elrond-erd-2" "bitcoin-cash-sv" "pyth-network" "conflux-token" "axie-infinity" "starknet" "dydx-chain" "the-sandbox" "mina-protocol" "bittorrent" "wrapped-eeth" "ordinals" "kucoin-shares" "singularitynet" "ether-fi-staked-eth" "havven" "worldcoin-wld" "ribbon-finance" "apecoin" "helium" "flare-networks" "akash-network" "decentraland" "tokenize-xchange" "chiliz" "msol" "tezos" "ronin" "bitget-token" "eos" "whitebit" "axelar" "pancakeswap-token" "ecash" "sats-ordinals" "true-usd" "dydx" "neo" "iota" "0x" "oasis-network" "frax-ether" "kava" "ethena-usde" "corgiai" "klay-token" "gnosis" "illuvium" "wemix-token" "blur" "cheelee" "osmosis" "book-of-meme" "woo-network" "gatechain-token" "dymension" "terra-luna" "jasmycoin" "bitcoin-gold" "astar" "curve-dao-token" "lido-staked-sol" "sweth" "nervos-network" "manta-network" "echelon-prime" "aioz-network" "nexo" "enjincoin" "amp-token" "staked-frax-ether" "ondo-finance" "usdd" "iotex" "ethereum-name-service" "livepeer" "coinbase-wrapped-staked-eth" "celo" "holotoken" "1inch" "kelp-dao-restaked-eth" "ocean-protocol" "space-id" "memecoin-2" "terra-luna-2" "frax-share" "zilliqa" "raydium" "rocket-pool" "xdce-crowd-sale" "frax" "radix" "stepn" "trust-wallet-token" "metis-token" "pixels" "superfarm" "dexe" "arkham" "loopring" "apenft" "siacoin" "coredaoorg" "altlayer" "compound-governance-token" "theta-fuel" "casper-network" "golem" "fasttoken" "helium-mobile" "zetachain" "tether-gold" "skale" "ankr" "moonbeam" "qtum" "gmx" "origintrail" "basic-attention-token" "compound-wrapped-btc" "nosana" "nem" "kadena" "kusama" "zcash" "project-galaxy" "stader-ethx" "gas" "dash" "biconomy" "decred" "mask-network" "paal-ai" "aelf" "benqi-liquid-staked-avax" "zelcash" "jito-governance-token" "kujira" "vanar-chain" "ethereum-pow-iou" "chia" "waves" "dao-maker" "harmony" "portal-2" "compound-ether" "deso" "telcoin" "ravencoin" "aleph-zero" "pax-gold" "neutron-3" "oec-token" "baby-doge-coin" "mx-token" "audius" "stride" "aragon" "sushi" "xai-blockchain" "convex-finance" "api3" "coq-inu" "rollbit-coin" "safepal" "boba-network" "l7dex" "just" "0x0-ai-ai-smart-contract" "threshold-network-token" "mog-coin" "uma" "mantra-dao" "blox" "reserve-rights-token" "delysium" "ssv-network" "band-protocol" "seedify-fund" "icon" "ontology")

# File containing the list of tokens
TOKENS_FILE="data/coingecko_top_250_ids.txt"

# Check if the tokens file exists
if [ ! -f "$TOKENS_FILE" ]; then
  echo "Tokens file $TOKENS_FILE does not exist."
  exit 1
fi

  echo "start"


while IFS= read -r line || [[ -n "$line" ]]; do
    TOKENS+=("$line")
done < "$TOKENS_FILE"

# To verify, you can print all tokens
printf "%s\n" "${TOKENS[@]}"

  echo "start"

  echo "$TOKENS"

# The file to store the results
OUTPUT_DIR_PRICES="data/prices"
OUTPUT_DIR_METADATA="data/metadata"

# Check if the directory exists, if not, create it
if [ ! -d "$OUTPUT_DIR_PRICES" ]; then
  mkdir -p "$OUTPUT_DIR_PRICES"
fi

# Check if the directory exists, if not, create it
if [ ! -d "$OUTPUT_DIR_METADATA" ]; then
  mkdir -p "$OUTPUT_DIR_METADATA"
fi

  echo "start"


# Loop through all tokens
for TOKEN in "${TOKENS[@]}"; do

  # Make the API call, capture the output
  RESPONSE_PRICE=$(curl --silent --request GET --url "https://pro-api.coingecko.com/api/v3/coins/$TOKEN/market_chart?vs_currency=usd&days=180&interval=daily&precision=12&x_cg_pro_api_key=$APIKEY")

  # Append the full response to the file
  echo "$RESPONSE_PRICE" > "$OUTPUT_DIR_PRICES/$TOKEN.json"
  
  # Print the token name and the first 25 characters of the response
  echo "Processed: $TOKEN - Response preview: ${RESPONSE_PRICE:0:50} - Saved to: $OUTPUT_DIR_PRICES/$TOKEN.json"

  # Time between each request
  sleep 1

  # Make the API call, capture the output
  RESPONSE_METADATA=$(curl --silent --request GET --url "https://pro-api.coingecko.com/api/v3/coins/$TOKEN?localization=false&tickers=false&market_data=false&community_data=false&developer_data=false&sparkline=false&x_cg_pro_api_key=$APIKEY")
  
  # Append the full response to the file
  echo "$RESPONSE_METADATA" > "$OUTPUT_DIR_METADATA/$TOKEN.json"
  
  # Print the token name and the first 25 characters of the response
  echo "Processed: $TOKEN - Response preview: ${PROCESSED_RESPONSE:0:50} - Saved to: $OUTPUT_DIR_METADATA/$TOKEN.json"

  # Time between each request
  sleep 1

done