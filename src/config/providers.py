"""Configuration providers for ZerePy."""
from typing import Any, Dict, Optional
from abc import ABC, abstractmethod
import os
from pathlib import Path
import json
from dotenv import load_dotenv

class ConfigProvider(ABC):
    """Base class for configuration providers."""
    
    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        pass
        
    @abstractmethod
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value."""
        pass

class EnvConfigProvider(ConfigProvider):
    """Environment variable configuration provider."""
    
    def __init__(self, env_file: str = '.env'):
        """Initialize provider."""
        self.env_file = env_file
        load_dotenv(env_file)
        
    def get(self, key: str, default: Any = None) -> Any:
        """Get environment variable."""
        return os.getenv(key, default)
        
    def set(self, key: str, value: Any) -> None:
        """Set environment variable."""
        os.environ[key] = str(value)
        # Note: We don't persist to .env file by default
        # Use set_key from python-dotenv if persistence is needed

class FileConfigProvider(ConfigProvider):
    """File-based configuration provider."""
    
    def __init__(self, config_file: str):
        """Initialize provider."""
        self.config_file = Path(config_file)
        self._config: Dict[str, Any] = {}
        self._load_config()
        
    def _load_config(self) -> None:
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self._config = json.load(f)
            except Exception:
                self._config = {}
                
    def _save_config(self) -> None:
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self._config, f, indent=4)
        except Exception:
            pass  # Fail silently on save errors
            
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self._config.get(key, default)
        
    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        self._config[key] = value
        self._save_config()
