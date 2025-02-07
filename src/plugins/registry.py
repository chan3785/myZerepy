"""Plugin registry for ZerePy."""
from typing import Dict, Type, Any
from .base import PluginBase
from .exceptions import PluginNotFoundError

class PluginRegistry:
    """Registry for managing plugins."""
    
    def __init__(self):
        """Initialize the plugin registry."""
        self._plugins: Dict[str, Dict[str, Type[PluginBase]]] = {}
        self._categories = {'connection', 'action'}
        
    def register(self, category: str, name: str, plugin_cls: Type[PluginBase]) -> None:
        """
        Register a plugin.
        
        Args:
            category: Plugin category ('connection' or 'action')
            name: Plugin name
            plugin_cls: Plugin class
            
        Raises:
            ValueError: If category is invalid
        """
        if category not in self._categories:
            raise ValueError(f"Invalid category: {category}")
        if category not in self._plugins:
            self._plugins[category] = {}
        self._plugins[category][name] = plugin_cls
        
    def get_plugin(self, category: str, name: str) -> Type[PluginBase]:
        """
        Get a plugin by category and name.
        
        Args:
            category: Plugin category
            name: Plugin name
            
        Returns:
            Plugin class
            
        Raises:
            PluginNotFoundError: If plugin is not found
        """
        if category not in self._plugins or name not in self._plugins[category]:
            raise PluginNotFoundError(f"Plugin not found: {category}/{name}")
        return self._plugins[category][name]
        
    def list_plugins(self, category: str = None) -> Dict[str, Dict[str, Type[PluginBase]]]:
        """
        List all registered plugins.
        
        Args:
            category: Optional category filter
            
        Returns:
            Dictionary of registered plugins
        """
        if category:
            if category not in self._plugins:
                return {}
            return {category: self._plugins[category]}
        return self._plugins.copy()
