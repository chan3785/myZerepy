from pydantic import Field, BaseModel
from typing import Optional, Dict, Any, List
from .config import BaseConnectionConfig, LLMConnectionConfig, BlockchainConnectionConfig

class OpenAIConfig(LLMConnectionConfig):
    """Configuration for OpenAI connection"""
    name: str = "openai"
    model: str = "gpt-3.5-turbo"
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None, gt=0)

class AnthropicConfig(LLMConnectionConfig):
    """Configuration for Anthropic connection"""
    name: str = "anthropic"
    model: str = "claude-3-5-sonnet-20241022"
    max_tokens: Optional[int] = Field(default=None, gt=0)

class SolanaConfig(BlockchainConnectionConfig):
    """Configuration for Solana connection"""
    name: str = "solana"
    commitment: str = "confirmed"
    timeout: int = Field(default=30, ge=1)
    
class EthereumConfig(BlockchainConnectionConfig):
    """Configuration for Ethereum connection"""
    name: str = "ethereum"
    chain_id: Optional[int] = None
    gas_limit: Optional[int] = Field(default=None, gt=0)
    
class FarcasterConfig(BaseConnectionConfig):
    """Configuration for Farcaster connection"""
    name: str = "farcaster"
    recovery_phrase: Optional[str] = None
    endpoint: Optional[str] = None
    
class TwitterConfig(BaseConnectionConfig):
    """Configuration for Twitter/X connection"""
    name: str = "twitter"
    api_key: str
    api_secret: str
    access_token: Optional[str] = None
    access_token_secret: Optional[str] = None
    timeline_read_count: int = Field(default=10, gt=0)

class TogetherConfig(LLMConnectionConfig):
    """Configuration for Together AI connection"""
    name: str = "together"
    model: str = "mistralai/Mixtral-8x7B-Instruct-v0.1"
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None, gt=0)

class OllamaConfig(LLMConnectionConfig):
    """Configuration for Ollama connection"""
    name: str = "ollama"
    model: str = "mistral"
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None, gt=0)
    host: str = "http://localhost:11434"

class GroqConfig(LLMConnectionConfig):
    """Configuration for Groq connection"""
    name: str = "groq"
    model: str = "mixtral-8x7b-32768"
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None, gt=0)
    top_p: float = Field(default=1.0, ge=0.0, le=1.0)

class EternalAIConfig(LLMConnectionConfig):
    """Configuration for EternalAI connection"""
    name: str = "eternalai"
    model: str = "eternal-v1"
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None, gt=0)
    top_p: float = Field(default=1.0, ge=0.0, le=1.0)
    chain_id: str = "45762"  # Default chain ID
    agent_id: Optional[int] = None
    contract_address: Optional[str] = None
    rpc_url: Optional[str] = None

class HyperbolicConfig(LLMConnectionConfig):
    """Configuration for Hyperbolic connection"""
    name: str = "hyperbolic"
    model: str = "hyperbolic-v1"
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None, gt=0)
    top_p: float = Field(default=1.0, ge=0.0, le=1.0)
    presence_penalty: float = Field(default=0.0, ge=-2.0, le=2.0)
    frequency_penalty: float = Field(default=0.0, ge=-2.0, le=2.0)

class PluginConfig(BaseModel):
    """Configuration for a Goat plugin"""
    name: str
    args: Dict[str, Any]

class GoatConfig(BaseConnectionConfig):
    """Configuration for Goat connection"""
    name: str = "goat"
    plugins: List[PluginConfig]

class EchoChamberConfig(BaseConnectionConfig):
    """Configuration for EchoChamber connection"""
    name: str = "echochamber"
    api_url: str
    api_key: str
    room: str
    sender_username: str
    sender_model: str
    history_read_count: int = Field(default=100, gt=0)
    post_history_track: int = Field(default=50, gt=0)

class SonicConfig(BlockchainConnectionConfig):
    """Configuration for Sonic connection"""
    name: str = "sonic"
    network: str = "mainnet"
    rpc_url: Optional[str] = None  # Optional since it can be derived from network
    explorer_url: Optional[str] = None  # Optional since it can be derived from network
    aggregator_api: str = "https://aggregator-api.kyberswap.com/sonic/api/v1"
    max_queue_size: int = Field(default=100, gt=0)
    gas_limit: Optional[int] = Field(default=None, gt=0)

class AlloraConfig(BlockchainConnectionConfig):
    """Configuration for Allora Network connection"""
    name: str = "allora"
    chain_slug: str = "testnet"  # Default to testnet as per connection class
    api_url: Optional[str] = None
    inference_timeout: int = Field(default=30, gt=0)  # Timeout in seconds for inference requests

class XAIConfig(LLMConnectionConfig):
    """Configuration for XAI (x.ai) connection"""
    name: str = "xai"
    model: str = "grok-1"  # Default model
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None, gt=0)
    top_p: float = Field(default=1.0, ge=0.0, le=1.0)
    presence_penalty: float = Field(default=0.0, ge=-2.0, le=2.0)
    frequency_penalty: float = Field(default=0.0, ge=-2.0, le=2.0)
    base_url: str = "https://api.x.ai/v1"  # XAI's API endpoint

class DiscordConfig(BaseConnectionConfig):
    """Configuration for Discord connection"""
    name: str = "discord"
    bot_token: str
    guild_id: Optional[str] = None
    channel_id: Optional[str] = None
    message_limit: int = Field(default=100, gt=0)
    message_interval: int = Field(default=60, gt=0)
