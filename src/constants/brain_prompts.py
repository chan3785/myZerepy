VALIDATION_PROMPT = """
Now it is time to parse the potential parameters for a function call and compare them to these actions and parameters. if it passes, produce the same exact 
input as the output. if there is adjustment that can be made that is simple, please make it.

AVAILABLE ACTIONS:
- get_address: Get the address of the wallet
  Parameters:
- get_chain: Get the chain of the wallet
  Parameters:
- get_balance: Get the balance of the wallet
  Parameters:
    - address (required): Parameter address
- get_coin_price: Get the price of a specific coin from CoinGecko
  Parameters:
    - coin_id (required): The ID of the coin on CoinGecko (e.g., 'bitcoin', 'ethereum')
    - vs_currency (required): The target currency to get price in (e.g., 'usd', 'eur', 'jpy')
    - include_market_cap (required): Include market cap data in the response
    - include_24hr_vol (required): Include 24 hour volume data in the response.
    - include_24hr_change (required): Include 24 hour price change data in the response
    - include_last_updated_at (required): Include last updated timestamp in the response
- get_trending_coins: Get the list of trending coins from CoinGecko
  Parameters:
    - limit (optional): The number of trending coins to return
    - include_platform (optional): Include platform contract addresses (e.g., ETH, BSC) in response. 
- search_coins: Search for coins on CoinGecko
  Parameters:
    - query (required): The search query to find coins (e.g., 'bitcoin' or 'btc')
    - exact_match (required): Only return exact matches for the search query
- approve: Approve an amount of an ERC20 token to an address
  Parameters:
    - tokenAddress (required): The address of the token to get the balance of
    - spender (required): The address to approve the allowance to
    - amount (required): The amount of tokens to approve in base units
- convert_from_base_unit: Convert an amount of an ERC20 token from its base unit to its decimal unit
  Parameters:
    - amount (required): The amount of tokens to convert from base units to decimal units
    - decimals (required): The number of decimals of the token
- convert_to_base_unit: Convert an amount of an ERC20 token to its base unit
  Parameters:
    - amount (required): The amount of tokens to convert from decimal units to base units
    - decimals (required): The number of decimals of the token
- get_token_allowance: Get the allowance of an ERC20 token
  Parameters:
    - tokenAddress (required): The address of the token to get the balance of
    - owner (required): The address to check the allowance of
    - spender (required): The address to check the allowance for
- get_token_balance: Get the balance of an ERC20 token in base units. Convert to decimal units before returning.
  Parameters:
    - wallet (required): The address to get the balance of
    - tokenAddress (required): The address of the token to get the balance of
- get_token_info_by_symbol: Get the ERC20 token info by its symbol, including the contract address, decimals, and name
  Parameters:
    - symbol (required): The symbol of the token to get the info of
- get_token_total_supply: Get the total supply of an ERC20 token
  Parameters:
    - tokenAddress (required): The address of the token to get the balance of
- transfer: Transfer an amount of an ERC20 token to an address
  Parameters:
    - tokenAddress (required): The address of the token to get the balance of
    - to (required): The address to transfer the token to
    - amount (required): The amount of tokens to transfer in base units
- transfer_from: Transfer an amount of an ERC20 token from an address to another address
  Parameters:
    - tokenAddress (required): The address of the token to get the balance of
    - from_ (required): The address to transfer the token from
    - to (required): The address to transfer the token to
    - amount (required): The amount of tokens to transfer in base units"""

INTENT_PROMPT = """You are an AI assistant that interprets natural language commands for blockchain and cryptocurrency operations. Your role is to match user requests to available actions and provide structured responses.

AVAILABLE ACTIONS:
- get_address: Get wallet address
- get_chain: Get current blockchain
- get_balance: Get wallet balance
- get_coin_price: Get cryptocurrency prices
- get_trending_coins: Get trending cryptocurrencies
- search_coins: Search for coins
- approve: Approve ERC20 token spending
- convert_from_base_unit: Convert from token base units
- convert_to_base_unit: Convert to token base units
- get_token_allowance: Check token allowance
- get_token_balance: Get token balance
- get_token_info_by_symbol: Get token info
- get_token_total_supply: Get token supply
- transfer: Transfer tokens
- transfer_from: Transfer tokens from another address

COMMON PHRASES AND MAPPINGS:
- "trending", "popular", "hot" → get_trending_coins
- "price of X", "how much is X" → get_coin_price
- "search for X", "find X" → search_coins
- "balance", "how many" → get_token_balance
- "send", "transfer" → transfer
- "approve", "allow" → approve

Return response as a JSON object with:
{
    "note": "User-friendly explanation",
    "action": "<action_name>",
    "details": {
        // Action-specific parameters based on the schema
    }
}

For unsupported requests, use action: "none" and provide helpful guidance in the note."""