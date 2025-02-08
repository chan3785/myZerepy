from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

class BaseConnectionConfig(BaseModel):
    """Base configuration model for all connections"""
    name: str
    enabled: bool = True
    
class LLMConnectionConfig(BaseConnectionConfig):
    """Configuration for LLM-based connections"""
    model: str
    api_key: Optional[str] = None
    
class BlockchainConnectionConfig(BaseConnectionConfig):
    """Configuration for blockchain connections"""
    rpc: str
    network: Optional[str] = "mainnet"
    
    class Config:
        # Allow extra fields for blockchain-specific configurations
        extra = "allow"
