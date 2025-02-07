"""Resource manager for ZerePy."""
from typing import Any, Dict, Optional, Type, TypeVar
import logging
import asyncio
from .lifecycle import ResourceLifecycle
from .pool import ResourcePool, PoolConfig, PoolStats
from ..events.bus import event_bus, Event

logger = logging.getLogger(__name__)

T = TypeVar('T')

class ResourceManager:
    """Manager for tracking and cleaning up resources."""
    
    def __init__(self):
        """Initialize resource manager."""
        self._resources: Dict[str, Dict[str, ResourceLifecycle]] = {}
        self._pools: Dict[str, ResourcePool] = {}
        self._stats: Dict[str, PoolStats] = {}
        
    async def start(self) -> None:
        """Start resource management."""
        # Start all pools
        for pool in self._pools.values():
            await pool.start()
            
    async def stop(self) -> None:
        """Stop resource management."""
        # Stop all pools
        for pool in self._pools.values():
            await pool.stop()
            
        # Clean up remaining resources
        await self.cleanup()
        
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
        
    def register_pool(
        self, 
        category: str, 
        resource_type: Type[T], 
        config: Optional[PoolConfig] = None
    ) -> None:
        """
        Register a resource pool.
        
        Args:
            category: Resource category
            resource_type: Type of resource to pool
            config: Pool configuration
        """
        pool = ResourcePool(resource_type, config)
        self._pools[category] = pool
        
        # Publish pool registration event
        event_bus.publish(Event(
            name="resource.pool.registered",
            data={"category": category, "type": resource_type.__name__},
            source="resource_manager"
        ))
        
    async def acquire(self, category: str) -> Optional[str]:
        """
        Acquire a resource from a pool.
        
        Args:
            category: Resource category
            
        Returns:
            Resource ID if successful, None otherwise
        """
        if category not in self._pools:
            logger.error(f"No pool found for category: {category}")
            return None
            
        try:
            resource_id = await self._pools[category].acquire()
            self._stats[category] = self._pools[category].stats
            return resource_id
        except Exception as e:
            logger.error(f"Failed to acquire resource from pool {category}: {e}")
            return None
            
    async def release(self, category: str, resource_id: str) -> None:
        """
        Release a resource back to its pool.
        
        Args:
            category: Resource category
            resource_id: Resource ID to release
        """
        if category not in self._pools:
            return
            
        await self._pools[category].release(resource_id)
        self._stats[category] = self._pools[category].stats
        
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
        
    async def cleanup(self, category: Optional[str] = None, name: Optional[str] = None) -> None:
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
                
            # Clean up pool if exists
            if category in self._pools:
                await self._pools[category].stop()
                del self._pools[category]
                del self._stats[category]
        else:
            # Clean up all resources
            for category_dict in self._resources.values():
                for resource in category_dict.values():
                    resource.cleanup()
            self._resources.clear()
            
            # Clean up all pools
            for pool in self._pools.values():
                await pool.stop()
            self._pools.clear()
            self._stats.clear()
            
        # Publish cleanup event
        event_bus.publish(Event(
            name="resource.cleanup",
            data={"category": category, "name": name},
            source="resource_manager"
        ))
        
    def get_stats(self, category: Optional[str] = None) -> Dict[str, PoolStats]:
        """
        Get resource statistics.
        
        Args:
            category: Optional category to get stats for
            
        Returns:
            Dictionary of pool statistics by category
        """
        if category:
            return {category: self._stats.get(category, PoolStats())}
        return self._stats.copy()
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop()

# Global resource manager instance
resource_manager = ResourceManager()
