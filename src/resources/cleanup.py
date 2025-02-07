"""Cleanup utilities for ZerePy."""
from typing import Any, Callable, Optional
import logging
from functools import wraps
from .manager import resource_manager
from ..events.bus import event_bus, Event

logger = logging.getLogger(__name__)

def with_cleanup(category: str, name: str) -> Callable:
    """
    Decorator to ensure resource cleanup.
    
    Args:
        category: Resource category
        name: Resource name
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            finally:
                try:
                    resource_manager.cleanup(category, name)
                except Exception as e:
                    logger.error(f"Error during cleanup: {e}")
        return wrapper
    return decorator

def cleanup_on_error(func: Callable) -> Callable:
    """
    Decorator to clean up resources on error.
    
    Args:
        func: Function to wrap
        
    Returns:
        Wrapped function
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Publish error event
            event_bus.publish(Event(
                name="resource.error",
                data={"error": str(e)},
                source="cleanup_utilities"
            ))
            
            # Clean up all resources on error
            resource_manager.cleanup()
            raise
    return wrapper
