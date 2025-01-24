from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

class ActionType(str, Enum):
    NONE = "none"
    SWAP = "swap"
    SEND = "send"

class SwapDetails(BaseModel):
    input_mint: str = Field(description="Token symbol or mint address")
    output_mint: str = Field(description="Token symbol or mint address")
    amount: float
    slippage_bps: int = Field(
        default=100,
        ge=0,
        le=10000,
        description="Slippage tolerance in basis points (0-10000)"
    )
    user_specified_slippage: bool = False

class SendDetails(BaseModel):
    token_mint: str = Field(description="Token symbol or mint address")
    amount: float
    recipient: str
    network: Optional[str] = Field(
        default="ethereum",
        description="Blockchain network for the transaction"
    )

class BrainResponse(BaseModel):
    note: str = Field(description="User-friendly response message")
    action: ActionType
    connection: str
    swap_details: Optional[SwapDetails] = None
    send_details: Optional[SendDetails] = None

SYSTEM_PROMPT = """You are a professional blockchain intents parser that converts natural language into structured actions.
Your task is to parse user inputs into specific blockchain operations across multiple networks.

Provide responses in this structure:
{
    "note": "user-friendly explanation",
    "action": "swap|send|none",
    "connection": "ethereum|solana|sonic",  # Specify the connection to use
    "swap_details": {
        "input_mint": "token symbol/address",
        "output_mint": "token symbol/address", 
        "amount": number,
        "slippage_bps": number(0-10000),
        "user_specified_slippage": boolean
    },
    "send_details": {
        "token_mint": "token symbol/address",
        "amount": number,
        "recipient": "address",
        "network": "ethereum|solana|etc"
    }
}

Guidelines:
- Default slippage is 1% (100 basis points)
- Network defaults to ethereum if not specified
- Token symbols will be resolved to addresses by our backend
- Return action "none" with helpful advice for unsupported actions
- Choose the connection from: ethereum, solana, sonic
"""