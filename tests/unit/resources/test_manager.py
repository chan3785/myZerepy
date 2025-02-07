"""Tests for resource manager."""
import pytest
from src.resources.manager import ResourceManager
from src.resources.lifecycle import ResourceLifecycle

class MockResource:
    """Mock resource for testing."""
    def __init__(self):
        self.initialized = False
        self.cleaned_up = False
        
    def initialize(self):
        self.initialized = True
        
    def cleanup(self):
        self.cleaned_up = True

def test_resource_manager_init():
    """Test resource manager initialization."""
    manager = ResourceManager()
    assert manager._resources == {}

def test_resource_manager_register():
    """Test registering resources."""
    manager = ResourceManager()
    resource = MockResource()
    manager.register('test', 'mock', resource)
    assert 'test' in manager._resources
    assert 'mock' in manager._resources['test']
    assert isinstance(manager._resources['test']['mock'], ResourceLifecycle)

def test_resource_manager_get():
    """Test getting resources."""
    manager = ResourceManager()
    resource = MockResource()
    manager.register('test', 'mock', resource)
    retrieved = manager.get('test', 'mock')
    assert retrieved is resource

def test_resource_manager_cleanup():
    """Test cleaning up resources."""
    manager = ResourceManager()
    resource = MockResource()
    manager.register('test', 'mock', resource)
    manager.cleanup()
    assert resource.cleaned_up

def test_resource_manager_cleanup_category():
    """Test cleaning up resources by category."""
    manager = ResourceManager()
    resource1 = MockResource()
    resource2 = MockResource()
    manager.register('test1', 'mock1', resource1)
    manager.register('test2', 'mock2', resource2)
    manager.cleanup('test1')
    assert resource1.cleaned_up
    assert not resource2.cleaned_up
