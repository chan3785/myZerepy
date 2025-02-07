"""Global settings management for ZerePy."""
from typing import Any, Dict, Optional
from pathlib import Path
import os
import json

class Settings:
    """Global settings manager."""
    
    def __init__(self):
        """Initialize settings manager."""
        self._settings: Dict[str, Any] = {}
        self._config_dir = Path.home() / '.zerepy'
        self._config_file = self._config_dir / 'config.json'
        self._load_settings()
        
    def _load_settings(self) -> None:
        """Load settings from config file."""
        if not self._config_dir.exists():
            self._config_dir.mkdir(parents=True)
            
        if self._config_file.exists():
            try:
                with open(self._config_file, 'r') as f:
                    self._settings = json.load(f)
            except Exception as e:
                self._settings = {}
                
    def _save_settings(self) -> None:
        """Save settings to config file."""
        try:
            with open(self._config_file, 'w') as f:
                json.dump(self._settings, f, indent=4)
        except Exception as e:
            pass  # Fail silently on save errors
            
    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value."""
        return self._settings.get(key, default)
        
    def set(self, key: str, value: Any) -> None:
        """Set a setting value."""
        self._settings[key] = value
        self._save_settings()
        
    def delete(self, key: str) -> None:
        """Delete a setting."""
        if key in self._settings:
            del self._settings[key]
            self._save_settings()
            
    @property
    def all(self) -> Dict[str, Any]:
        """Get all settings."""
        return self._settings.copy()

# Global settings instance
settings = Settings()
