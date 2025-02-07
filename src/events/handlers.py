"""Event handlers for ZerePy."""
from typing import Any, Callable, Dict, Optional
import logging
from functools import wraps
from .bus import Event

logger = logging.getLogger(__name__)

def with_error_boundary(handler: Callable) -> Callable:
    """
    Decorator to add error boundary to event handlers.
    
    Args:
        handler: Event handler function
        
    Returns:
        Wrapped handler function
    """
    @wraps(handler)
    def wrapper(event: Event) -> None:
        try:
            return handler(event)
        except Exception as e:
            logger.error(f"Error in event handler: {e}")
            # Don't propagate errors from event handlers
            
    return wrapper

class EventHandler:
    """Base class for event handlers."""
    
    def __init__(self, event_name: str):
        """Initialize event handler."""
        self.event_name = event_name
        
    def __call__(self, func: Callable) -> Callable:
        """
        Decorator to register event handler.
        
        Args:
            func: Handler function
            
        Returns:
            Wrapped handler function
        """
        from .bus import event_bus
        
        @with_error_boundary
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)
            
        event_bus.subscribe(self.event_name, wrapper)
        return wrapper
