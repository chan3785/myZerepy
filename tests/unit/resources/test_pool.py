"""Tests for resource pooling."""
import pytest
import asyncio
from typing import Optional
from src.resources.pool import ResourcePool, PoolConfig, PoolStats
from src.resources.lifecycle import ResourceState

class MockResource:
    """Mock resource for testing."""
    def __init__(self):
        self.initialized = False
        self.cleaned_up = False
        
    async def initialize(self):
        self.initialized = True
        
    async def cleanup(self):
        self.cleaned_up = True

@pytest.mark.asyncio
async def test_pool_initialization():
    """Test pool initialization."""
    config = PoolConfig(min_size=2, max_size=5)
    pool = ResourcePool(MockResource, config)
    
    await pool.start()
    stats = pool.stats
    
    assert stats.total == 2  # min_size resources created
    assert stats.active == 0  # no resources in use
    assert stats.idle == 2   # all resources idle
    
    await pool.stop()

@pytest.mark.asyncio
async def test_pool_acquire_release():
    """Test acquiring and releasing resources."""
    pool = ResourcePool(MockResource)
    await pool.start()
    
    # Acquire resource
    resource_id = await pool.acquire()
    stats = pool.stats
    
    assert stats.active == 1
    assert stats.idle == 0
    
    # Release resource
    await pool.release(resource_id)
    stats = pool.stats
    
    assert stats.active == 0
    assert stats.idle == 1
    
    await pool.stop()

@pytest.mark.asyncio
async def test_pool_max_size():
    """Test pool maximum size."""
    config = PoolConfig(min_size=1, max_size=2)
    pool = ResourcePool(MockResource, config)
    await pool.start()
    
    # Acquire max resources
    id1 = await pool.acquire()
    id2 = await pool.acquire()
    
    # Try to acquire one more
    with pytest.raises(RuntimeError, match="Resource pool exhausted"):
        await pool.acquire()
        
    await pool.stop()

@pytest.mark.asyncio
async def test_pool_cleanup():
    """Test pool cleanup."""
    config = PoolConfig(
        min_size=1,
        max_size=3,
        max_idle=1,
        cleanup_interval=1
    )
    pool = ResourcePool(MockResource, config)
    await pool.start()
    
    # Create extra idle resources
    id1 = await pool.acquire()
    id2 = await pool.acquire()
    await pool.release(id1)
    await pool.release(id2)
    
    # Wait for cleanup
    await asyncio.sleep(2)
    stats = pool.stats
    
    assert stats.total == 1  # Only min_size remains
    assert stats.idle == 1
    
    await pool.stop()

@pytest.mark.asyncio
async def test_pool_error_handling():
    """Test pool error handling."""
    class ErrorResource:
        async def initialize(self):
            raise RuntimeError("Initialization error")
            
    pool = ResourcePool(ErrorResource)
    await pool.start()
    
    with pytest.raises(RuntimeError, match="Initialization error"):
        await pool.acquire()
        
    stats = pool.stats
    assert stats.errors == 1
    
    await pool.stop()
