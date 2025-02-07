"""Event bus implementation for ZerePy."""
from typing import Any, Callable, Dict, List, Optional
import asyncio
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class Event:
    """Event data container."""
    name: str
    data: Dict[str, Any]
    source: str

class EventBus:
    """Event bus for message passing and coordination."""
    
    def __init__(self):
        """Initialize event bus."""
        self._subscribers: Dict[str, List[Callable]] = {}
        self._loop = asyncio.get_event_loop()
        
    async def publish(self, event: Event) -> None:
        """
        Publish an event to all subscribers.
        
        Args:
            event: Event to publish
        """
        if event.name not in self._subscribers:
            return
            
        for handler in self._subscribers[event.name]:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    await self._loop.run_in_executor(None, handler, event)
            except Exception as e:
                logger.error(f"Error in event handler for {event.name}: {e}")
                
    def subscribe(self, event_name: str, handler: Callable) -> None:
        """
        Subscribe to an event.
        
        Args:
            event_name: Name of event to subscribe to
            handler: Event handler function
        """
        if event_name not in self._subscribers:
            self._subscribers[event_name] = []
        self._subscribers[event_name].append(handler)
        
    def unsubscribe(self, event_name: str, handler: Callable) -> None:
        """
        Unsubscribe from an event.
        
        Args:
            event_name: Name of event to unsubscribe from
            handler: Event handler function to remove
        """
        if event_name in self._subscribers:
            self._subscribers[event_name] = [
                h for h in self._subscribers[event_name] if h != handler
            ]
            
    def clear_subscribers(self, event_name: Optional[str] = None) -> None:
        """
        Clear all subscribers for an event or all events.
        
        Args:
            event_name: Optional event name to clear subscribers for
        """
        if event_name:
            self._subscribers[event_name] = []
        else:
            self._subscribers.clear()

# Global event bus instance
event_bus = EventBus()
