from enum import Enum
from typing import Optional, Union
from pydantic import BaseModel, Field

class ActionType(str, Enum):
    NONE = "none"
    GET_COIN_PRICE = "get_coin_price"
    GET_TRENDING = "get_trending"
    SEARCH_COINS = "search_coins"
    TOKEN_BALANCE = "token_balance"
    TOKEN_TRANSFER = "token_transfer"
    TOKEN_APPROVE = "token_approve"

class CoinPriceDetails(BaseModel):
    coin_id: str
    vs_currency: str = "usd"
    include_market_cap: bool = True
    include_24hr_vol: bool = True
    include_24hr_change: bool = True
    include_last_updated_at: bool = True

class TrendingDetails(BaseModel):
    limit: Optional[int] = None
    include_platform: bool = True

class SearchDetails(BaseModel):
    query: str
    exact_match: bool = False

class TokenBalanceDetails(BaseModel):
    wallet: str
    token_address: str

class TokenTransferDetails(BaseModel):
    token_address: str
    to_address: str
    amount: str
    from_address: Optional[str] = None

class TokenApproveDetails(BaseModel):
    token_address: str
    spender: str
    amount: str

class BrainResponse(BaseModel):
    note: str = Field(description="User-friendly response message")
    action: ActionType
    details: Optional[Union[
        CoinPriceDetails,
        TrendingDetails,
        SearchDetails,
        TokenBalanceDetails,
        TokenTransferDetails,
        TokenApproveDetails
    ]] = None