"""Resource manager for ZerePy."""
from typing import Any, Dict, Optional, Type
import logging
from .lifecycle import ResourceLifecycle
from ..events.bus import event_bus, Event

logger = logging.getLogger(__name__)

class ResourceManager:
    """Manager for tracking and cleaning up resources."""
    
    def __init__(self):
        """Initialize resource manager."""
        self._resources: Dict[str, Dict[str, ResourceLifecycle]] = {}
        
    def register(self, category: str, name: str, resource: Any) -> None:
        """
        Register a resource for management.
        
        Args:
            category: Resource category
            name: Resource name
            resource: Resource instance
        """
        if category not in self._resources:
            self._resources[category] = {}
            
        lifecycle = ResourceLifecycle(resource)
        self._resources[category][name] = lifecycle
        
        # Publish resource registration event
        event_bus.publish(Event(
            name="resource.registered",
            data={"category": category, "name": name},
            source="resource_manager"
        ))
        
    def get(self, category: str, name: str) -> Optional[Any]:
        """
        Get a registered resource.
        
        Args:
            category: Resource category
            name: Resource name
            
        Returns:
            Resource instance if found, None otherwise
        """
        return (self._resources.get(category, {})
                .get(name, ResourceLifecycle(None)).resource)
        
    def cleanup(self, category: Optional[str] = None, name: Optional[str] = None) -> None:
        """
        Clean up resources.
        
        Args:
            category: Optional category to clean up
            name: Optional name to clean up
        """
        if category and name:
            # Clean up specific resource
            if category in self._resources and name in self._resources[category]:
                self._resources[category][name].cleanup()
                del self._resources[category][name]
        elif category:
            # Clean up category
            if category in self._resources:
                for resource in self._resources[category].values():
                    resource.cleanup()
                del self._resources[category]
        else:
            # Clean up all resources
            for category_dict in self._resources.values():
                for resource in category_dict.values():
                    resource.cleanup()
            self._resources.clear()
            
        # Publish cleanup event
        event_bus.publish(Event(
            name="resource.cleanup",
            data={"category": category, "name": name},
            source="resource_manager"
        ))
        
    def __del__(self):
        """Ensure cleanup on deletion."""
        self.cleanup()

# Global resource manager instance
resource_manager = ResourceManager()
