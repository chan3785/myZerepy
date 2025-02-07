"""Resource lifecycle management for ZerePy."""
from typing import Any, Optional
import logging
from dataclasses import dataclass
from ..events.bus import event_bus, Event

logger = logging.getLogger(__name__)

@dataclass
class ResourceState:
    """Resource state information."""
    initialized: bool = False
    active: bool = False
    error: Optional[str] = None

class ResourceLifecycle:
    """Lifecycle management for resources."""
    
    def __init__(self, resource: Any):
        """Initialize resource lifecycle."""
        self.resource = resource
        self.state = ResourceState()
        
    def initialize(self) -> None:
        """Initialize the resource."""
        if hasattr(self.resource, 'initialize'):
            try:
                self.resource.initialize()
                self.state.initialized = True
                self.state.active = True
                self.state.error = None
                
                # Publish initialization event
                event_bus.publish(Event(
                    name="resource.initialized",
                    data={"resource": str(self.resource)},
                    source="resource_lifecycle"
                ))
            except Exception as e:
                self.state.error = str(e)
                logger.error(f"Failed to initialize resource: {e}")
                raise
                
    def cleanup(self) -> None:
        """Clean up the resource."""
        if hasattr(self.resource, 'cleanup'):
            try:
                self.resource.cleanup()
                self.state.active = False
                
                # Publish cleanup event
                event_bus.publish(Event(
                    name="resource.cleaned_up",
                    data={"resource": str(self.resource)},
                    source="resource_lifecycle"
                ))
            except Exception as e:
                self.state.error = str(e)
                logger.error(f"Failed to clean up resource: {e}")
                raise
