from pydantic import Field
from typing import Optional, Dict, Any
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

class DiscordConfig(BaseConnectionConfig):
    """Configuration for Discord connection"""
    name: str = "discord"
    bot_token: str
    guild_id: Optional[str] = None
    channel_id: Optional[str] = None
    message_limit: int = Field(default=100, gt=0)
    message_interval: int = Field(default=60, gt=0)
