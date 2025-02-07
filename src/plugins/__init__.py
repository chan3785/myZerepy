"""ZerePy plugin system."""
from .base import PluginBase, ConnectionPlugin, ActionPlugin
from .exceptions import (
    PluginError,
    PluginNotFoundError,
    PluginLoadError,
    PluginConfigError,
    PluginExecutionError,
    PluginCleanupError,
)
from .discovery import discover_plugins

__all__ = [
    'PluginBase',
    'ConnectionPlugin',
    'ActionPlugin',
    'PluginError',
    'PluginNotFoundError',
    'PluginLoadError',
    'PluginConfigError',
    'PluginExecutionError',
    'PluginCleanupError',
    'discover_plugins',
]
