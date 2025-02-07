"""Pytest configuration and fixtures."""
import pytest
from pathlib import Path
import tempfile
import shutil
from typing import Generator

@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)

@pytest.fixture
def plugin_dir(temp_dir: Path) -> Path:
    """Create a temporary plugin directory."""
    plugin_dir = temp_dir / "plugins"
    plugin_dir.mkdir()
    return plugin_dir

@pytest.fixture
def config_dir(temp_dir: Path) -> Path:
    """Create a temporary config directory."""
    config_dir = temp_dir / "config"
    config_dir.mkdir()
    return config_dir

@pytest.fixture
def cleanup_resources():
    """Clean up resources after tests."""
    yield
    from src.resources.manager import resource_manager
    resource_manager.cleanup()

@pytest.fixture
def event_bus():
    """Get event bus instance and clean up after tests."""
    from src.events.bus import event_bus
    yield event_bus
    event_bus.clear_subscribers()
