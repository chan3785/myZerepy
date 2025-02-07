"""Plugin discovery mechanisms for ZerePy."""
import os
import sys
import importlib
import logging
from typing import Dict, Type, List
from pathlib import Path

from .base import PluginBase
from .exceptions import PluginLoadError

logger = logging.getLogger(__name__)

def discover_plugins(plugin_dir: str) -> Dict[str, Type[PluginBase]]:
    """
    Discover plugins in the given directory.
    
    Args:
        plugin_dir: Directory to search for plugins
        
    Returns:
        Dictionary mapping plugin names to plugin classes
        
    Raises:
        PluginLoadError: If plugin loading fails
    """
    plugins: Dict[str, Type[PluginBase]] = {}
    plugin_path = Path(plugin_dir)
    
    if not plugin_path.exists():
        logger.warning(f"Plugin directory {plugin_dir} does not exist")
        return plugins
        
    # Add plugin directory to Python path
    sys.path.insert(0, str(plugin_path.parent))
    
    try:
        # Find all Python files in plugin directory
        for file_path in plugin_path.glob("*.py"):
            if file_path.name.startswith("_"):
                continue
                
            module_name = file_path.stem
            try:
                # Import module
                module = importlib.import_module(f"{plugin_path.name}.{module_name}")
                
                # Find plugin classes
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        issubclass(attr, PluginBase) and 
                        attr != PluginBase):
                        plugins[attr.name] = attr
                        
            except Exception as e:
                logger.error(f"Failed to load plugin {module_name}: {e}")
                raise PluginLoadError(f"Failed to load plugin {module_name}: {e}")
                
    finally:
        # Remove plugin directory from Python path
        sys.path.pop(0)
        
    return plugins
