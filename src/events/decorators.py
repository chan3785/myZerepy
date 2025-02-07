"""Event decorators for ZerePy."""
from typing import Any, Callable, Dict, Optional
from functools import wraps
from .bus import Event, event_bus

def publish_event(event_name: str, source: str) -> Callable:
    """
    Decorator to publish events before and after function execution.
    
    Args:
        event_name: Base name for the events
        source: Source of the events
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Publish start event
            await event_bus.publish(Event(
                name=f"{event_name}.start",
                data={"args": args, "kwargs": kwargs},
                source=source
            ))
            
            try:
                result = await func(*args, **kwargs)
                
                # Publish success event
                await event_bus.publish(Event(
                    name=f"{event_name}.success",
                    data={"result": result},
                    source=source
                ))
                
                return result
                
            except Exception as e:
                # Publish failure event
                await event_bus.publish(Event(
                    name=f"{event_name}.failure",
                    data={"error": str(e)},
                    source=source
                ))
                raise
                
        return wrapper
    return decorator

def subscribe_to(event_name: str) -> Callable:
    """
    Decorator to subscribe a function to an event.
    
    Args:
        event_name: Name of event to subscribe to
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        event_bus.subscribe(event_name, func)
        return func
    return decorator
