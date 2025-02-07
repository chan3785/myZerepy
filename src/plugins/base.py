"""Base classes for the ZerePy plugin system."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

class PluginBase(ABC):
    """Base class for all plugins."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of the plugin."""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Return the version of the plugin."""
        pass

    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the plugin with configuration."""
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """Clean up plugin resources."""
        pass

class ConnectionPlugin(PluginBase):
    """Base class for connection plugins."""
    
    @abstractmethod
    def is_configured(self) -> bool:
        """Check if the connection is properly configured."""
        pass

    @abstractmethod
    def configure(self) -> bool:
        """Configure the connection."""
        pass

    @abstractmethod
    def perform_action(self, action_name: str, params: Dict[str, Any]) -> Any:
        """Execute an action with the given parameters."""
        pass

class ActionPlugin(PluginBase):
    """Base class for action plugins."""
    
    @abstractmethod
    def validate_params(self, params: Dict[str, Any]) -> List[str]:
        """Validate action parameters."""
        pass

    @abstractmethod
    def execute(self, params: Dict[str, Any]) -> Any:
        """Execute the action with the given parameters."""
        pass
