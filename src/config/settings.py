"""Global settings management for ZerePy."""
import logging
from typing import Any, Dict, List, Optional, Type
from pathlib import Path
import os
from .providers import ConfigProvider, EnvConfigProvider, FileConfigProvider
from .composite import CompositeConfigProvider
from .validation import (
    ConfigValidator,
    ConnectionConfigValidator,
    PluginConfigValidator,
    AgentConfigValidator,
    ValidationError
)

logger = logging.getLogger("settings")

class Settings:
    """Global settings manager."""
    
    def __init__(self):
        """Initialize settings manager."""
        self._config_dir = Path.home() / '.zerepy'
        self._config_file = self._config_dir / 'config.json'
        self._env_file = self._config_dir / '.env'
        
        # Ensure config directory exists
        if not self._config_dir.exists():
            self._config_dir.mkdir(parents=True)
            
        # Initialize providers
        self._providers = CompositeConfigProvider([
            EnvConfigProvider(str(self._env_file)),
            FileConfigProvider(str(self._config_file))
        ])
        
        # Initialize validators
        self._validators = {
            'connection': ConnectionConfigValidator(),
            'plugin': PluginConfigValidator(),
            'agent': AgentConfigValidator()
        }
        
    def validate(self, config: Dict[str, Any], validator_type: str) -> List[ValidationError]:
        """
        Validate configuration.
        
        Args:
            config: Configuration to validate
            validator_type: Type of validator to use
            
        Returns:
            List of validation errors
        """
        if validator_type not in self._validators:
            logger.error(f"Unknown validator type: {validator_type}")
            return []
            
        return self._validators[validator_type].validate(config)
        
    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value."""
        return self._providers.get(key, default)
        
    def set(self, key: str, value: Any) -> None:
        """Set a setting value."""
        self._providers.set(key, value)
        
    def delete(self, key: str) -> None:
        """Delete a setting."""
        # Note: We only delete from file provider to maintain env vars
        file_provider = self._providers._providers[1]
        if isinstance(file_provider, FileConfigProvider):
            config = file_provider._config
            if key in config:
                del config[key]
                file_provider._save_config()
            
    @property
    def all(self) -> Dict[str, Any]:
        """Get all settings."""
        # Combine settings from all providers
        settings = {}
        for provider in reversed(self._providers._providers):
            if isinstance(provider, FileConfigProvider):
                settings.update(provider._config)
        return settings.copy()

# Global settings instance
settings = Settings()
