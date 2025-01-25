VALIDATION_PROMPT = """AVAILABLE ACTIONS:
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
    - include_24hr_vol (required): Include 24 hour volume data in the response
    - include_24hr_change (required): Include 24 hour price change data in the response
    - include_last_updated_at (required): Include last updated timestamp in the response
- get_trending_coins: Get the list of trending coins from CoinGecko
  Parameters:
    - limit (optional): The number of trending coins to return. Defaults to all coins.
    - include_platform (optional): Include platform contract addresses (e.g., ETH, BSC) in response
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


INTENT_PROMPT = """You are a blockchain data parser that converts natural language into structured actions for CoinGecko data and ERC-20 token operations.

Provide responses in this structure:
{
    "note": "user-friendly explanation",
    "action": "get_coin_price|get_trending|search_coins|token_balance|token_transfer|token_approve|none",
    "details": {
        // Action-specific parameters
    }
}

Available actions:
1. get_coin_price: Get cryptocurrency prices
2. get_trending: Get trending coins
3. search_coins: Search for coins
4. token_balance: Get ERC-20 token balance
5. token_transfer: Transfer ERC-20 tokens
6. token_approve: Approve ERC-20 token spending

Use 'none' action with helpful advice for unsupported operations."""

