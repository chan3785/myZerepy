"""Tests for settings management."""
import pytest
from pathlib import Path
from src.config.settings import Settings

def test_settings_init(config_dir: Path):
    """Test settings initialization."""
    settings = Settings()
    assert settings._settings == {}
    assert settings._config_dir.exists()

def test_settings_get_set():
    """Test getting and setting settings."""
    settings = Settings()
    settings.set('test_key', 'test_value')
    assert settings.get('test_key') == 'test_value'
    assert settings.get('nonexistent') is None
    assert settings.get('nonexistent', 'default') == 'default'

def test_settings_delete():
    """Test deleting settings."""
    settings = Settings()
    settings.set('test_key', 'test_value')
    settings.delete('test_key')
    assert settings.get('test_key') is None

def test_settings_all():
    """Test getting all settings."""
    settings = Settings()
    test_data = {'key1': 'value1', 'key2': 'value2'}
    for k, v in test_data.items():
        settings.set(k, v)
    assert settings.all == test_data
