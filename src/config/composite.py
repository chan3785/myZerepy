"""Composite configuration provider for ZerePy."""
from typing import Any, Dict, List, Optional
from .providers import ConfigProvider

class CompositeConfigProvider(ConfigProvider):
    """Provider that combines multiple providers with priority."""
    
    def __init__(self, providers: List[ConfigProvider]):
        """
        Initialize provider.
        
        Args:
            providers: List of providers in priority order (first has highest priority)
        """
        self._providers = providers
        
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value from first provider that has it.
        
        Args:
            key: Configuration key
            default: Default value if not found
            
        Returns:
            Configuration value or default
        """
        for provider in self._providers:
            value = provider.get(key)
            if value is not None:
                return value
        return default
        
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value in all providers.
        
        Args:
            key: Configuration key
            value: Configuration value
        """
        for provider in self._providers:
            provider.set(key, value)
