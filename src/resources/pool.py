"""Resource pooling and monitoring for ZerePy."""
from typing import Any, Dict, List, Optional, Type, TypeVar
import logging
import asyncio
from dataclasses import dataclass
from .lifecycle import ResourceState
from ..events.bus import event_bus, Event

logger = logging.getLogger(__name__)

T = TypeVar('T')

@dataclass
class PoolConfig:
    """Pool configuration."""
    min_size: int = 1
    max_size: int = 10
    max_idle: int = 300  # seconds
    cleanup_interval: int = 60  # seconds

@dataclass
class PoolStats:
    """Pool statistics."""
    total: int = 0
    active: int = 0
    idle: int = 0
    errors: int = 0

class ResourcePool:
    """Pool for managing resource instances."""
    
    def __init__(self, resource_type: Type[T], config: Optional[PoolConfig] = None):
        """
        Initialize pool.
        
        Args:
            resource_type: Type of resource to pool
            config: Pool configuration
        """
        self._resource_type = resource_type
        self._config = config or PoolConfig()
        self._resources: Dict[str, T] = {}
        self._states: Dict[str, ResourceState] = {}
        self._stats = PoolStats()
        self._cleanup_task: Optional[asyncio.Task] = None
        
    async def start(self) -> None:
        """Start pool management."""
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        # Initialize minimum pool size
        for _ in range(self._config.min_size):
            await self.acquire()
            
    async def stop(self) -> None:
        """Stop pool management."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
                
        # Clean up all resources
        for resource_id in list(self._resources.keys()):
            await self.release(resource_id)
            
    async def acquire(self) -> str:
        """
        Acquire a resource from the pool.
        
        Returns:
            Resource ID
        """
        # Check if we can reuse an idle resource
        for resource_id, state in self._states.items():
            if not state.active:
                state.active = True
                self._stats.active += 1
                self._stats.idle -= 1
                return resource_id
                
        # Create new resource if pool not at max
        if len(self._resources) < self._config.max_size:
            resource_id = f"{self._resource_type.__name__}_{len(self._resources)}"
            resource = self._resource_type()
            
            try:
                if hasattr(resource, 'initialize'):
                    await resource.initialize()
                    
                self._resources[resource_id] = resource
                self._states[resource_id] = ResourceState(
                    initialized=True,
                    active=True
                )
                
                self._stats.total += 1
                self._stats.active += 1
                
                # Publish resource created event
                await event_bus.publish(Event(
                    name="resource.created",
                    data={
                        "resource_id": resource_id,
                        "type": self._resource_type.__name__
                    },
                    source="resource_pool"
                ))
                
                return resource_id
                
            except Exception as e:
                logger.error(f"Failed to create resource: {e}")
                self._stats.errors += 1
                raise
                
        raise RuntimeError("Resource pool exhausted")
        
    async def release(self, resource_id: str) -> None:
        """
        Release a resource back to the pool.
        
        Args:
            resource_id: Resource ID to release
        """
        if resource_id not in self._states:
            return
            
        state = self._states[resource_id]
        if state.active:
            state.active = False
            self._stats.active -= 1
            self._stats.idle += 1
            
    async def _cleanup_loop(self) -> None:
        """Cleanup loop for idle resources."""
        while True:
            try:
                # Remove idle resources above min_size
                idle_count = self._stats.idle
                if idle_count > self._config.min_size:
                    to_remove = idle_count - self._config.min_size
                    removed = 0
                    
                    for resource_id, state in list(self._states.items()):
                        if removed >= to_remove:
                            break
                            
                        if not state.active:
                            resource = self._resources[resource_id]
                            if hasattr(resource, 'cleanup'):
                                await resource.cleanup()
                                
                            del self._resources[resource_id]
                            del self._states[resource_id]
                            
                            self._stats.total -= 1
                            self._stats.idle -= 1
                            removed += 1
                            
                            # Publish resource removed event
                            await event_bus.publish(Event(
                                name="resource.removed",
                                data={
                                    "resource_id": resource_id,
                                    "type": self._resource_type.__name__
                                },
                                source="resource_pool"
                            ))
                            
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                self._stats.errors += 1
                
            await asyncio.sleep(self._config.cleanup_interval)
            
    @property
    def stats(self) -> PoolStats:
        """Get pool statistics."""
        return self._stats
