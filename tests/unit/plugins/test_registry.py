"""Tests for plugin registry."""
import pytest
from src.plugins.registry import PluginRegistry
from src.plugins.base import PluginBase
from src.plugins.exceptions import PluginNotFoundError

class MockPlugin(PluginBase):
    """Mock plugin for testing."""
    @property
    def name(self) -> str:
        return "mock"
        
    @property
    def version(self) -> str:
        return "1.0.0"
        
    def initialize(self, config):
        pass
        
    def cleanup(self):
        pass

def test_plugin_registry_init():
    """Test plugin registry initialization."""
    registry = PluginRegistry()
    assert registry._plugins == {}
    assert 'connection' in registry._categories
    assert 'action' in registry._categories

def test_plugin_registry_register():
    """Test plugin registration."""
    registry = PluginRegistry()
    registry.register('connection', 'mock', MockPlugin)
    assert registry._plugins['connection']['mock'] == MockPlugin

def test_plugin_registry_invalid_category():
    """Test registering plugin with invalid category."""
    registry = PluginRegistry()
    with pytest.raises(ValueError):
        registry.register('invalid', 'mock', MockPlugin)

def test_plugin_registry_get_plugin():
    """Test getting registered plugin."""
    registry = PluginRegistry()
    registry.register('connection', 'mock', MockPlugin)
    plugin_cls = registry.get_plugin('connection', 'mock')
    assert plugin_cls == MockPlugin

def test_plugin_registry_get_nonexistent():
    """Test getting non-existent plugin."""
    registry = PluginRegistry()
    with pytest.raises(PluginNotFoundError):
        registry.get_plugin('connection', 'nonexistent')

def test_plugin_registry_list_plugins():
    """Test listing plugins."""
    registry = PluginRegistry()
    registry.register('connection', 'mock', MockPlugin)
    plugins = registry.list_plugins()
    assert 'connection' in plugins
    assert 'mock' in plugins['connection']
    assert plugins['connection']['mock'] == MockPlugin
