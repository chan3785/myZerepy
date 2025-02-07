"""Tests for plugin discovery."""
import pytest
from pathlib import Path
from src.plugins.discovery import discover_plugins
from src.plugins.exceptions import PluginLoadError
from src.plugins.base import PluginBase

def test_discover_plugins_empty_dir(plugin_dir: Path):
    """Test discovering plugins in empty directory."""
    plugins = discover_plugins(str(plugin_dir))
    assert plugins == {}

def test_discover_plugins_with_plugin(plugin_dir: Path):
    """Test discovering plugins with valid plugin."""
    # Create mock plugin file
    plugin_file = plugin_dir / "mock_plugin.py"
    plugin_file.write_text("""
from src.plugins.base import PluginBase

class MockPlugin(PluginBase):
    @property
    def name(self):
        return "mock"
        
    @property
    def version(self):
        return "1.0.0"
        
    def initialize(self, config):
        pass
        
    def cleanup(self):
        pass
""")
    
    plugins = discover_plugins(str(plugin_dir))
    assert "mock" in plugins
    assert issubclass(plugins["mock"], PluginBase)

def test_discover_plugins_invalid_plugin(plugin_dir: Path):
    """Test discovering plugins with invalid plugin."""
    # Create invalid plugin file
    plugin_file = plugin_dir / "invalid_plugin.py"
    plugin_file.write_text("invalid python code")
    
    with pytest.raises(PluginLoadError):
        discover_plugins(str(plugin_dir))

def test_discover_plugins_nonexistent_dir():
    """Test discovering plugins in non-existent directory."""
    plugins = discover_plugins("/nonexistent")
    assert plugins == {}
