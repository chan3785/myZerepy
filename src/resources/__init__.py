"""Resource management for ZerePy."""
from .manager import ResourceManager, resource_manager
from .lifecycle import ResourceLifecycle, ResourceState
from .cleanup import with_cleanup, cleanup_on_error

__all__ = [
    'ResourceManager',
    'resource_manager',
    'ResourceLifecycle',
    'ResourceState',
    'with_cleanup',
    'cleanup_on_error',
]
