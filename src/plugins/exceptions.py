"""Exceptions for the ZerePy plugin system."""

class PluginError(Exception):
    """Base class for plugin-related exceptions."""
    pass

class PluginNotFoundError(PluginError):
    """Raised when a plugin cannot be found."""
    pass

class PluginLoadError(PluginError):
    """Raised when a plugin fails to load."""
    pass

class PluginConfigError(PluginError):
    """Raised when plugin configuration is invalid."""
    pass

class PluginExecutionError(PluginError):
    """Raised when plugin execution fails."""
    pass

class PluginCleanupError(PluginError):
    """Raised when plugin cleanup fails."""
    pass
