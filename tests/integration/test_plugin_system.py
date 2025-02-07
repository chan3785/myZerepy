"""Integration tests for plugin system."""
import pytest
from pathlib import Path
from src.plugins.registry import PluginRegistry
from src.plugins.discovery import discover_plugins
from src.plugins.base import PluginBase

def test_plugin_system_integration(plugin_dir: Path):
    """Test complete plugin system workflow."""
    # Create mock plugin
    plugin_file = plugin_dir / "test_plugin.py"
    plugin_file.write_text("""
from src.plugins.base import PluginBase

class TestPlugin(PluginBase):
    @property
    def name(self):
        return "test"
        
    @property
    def version(self):
        return "1.0.0"
        
    def initialize(self, config):
        pass
        
    def cleanup(self):
        pass
""")
    
    # Discover plugins
    plugins = discover_plugins(str(plugin_dir))
    assert "test" in plugins
    
    # Register plugin
    registry = PluginRegistry()
    registry.register('connection', 'test', plugins['test'])
    
    # Get plugin
    plugin_cls = registry.get_plugin('connection', 'test')
    assert plugin_cls.name == "test"
    assert plugin_cls.version == "1.0.0"
