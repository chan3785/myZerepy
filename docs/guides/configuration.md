# Configuration Guide

## Overview
This guide explains how to configure the ZerePy framework and its plugins. The configuration system supports multiple providers and validation schemas.

## Configuration Sources

### Environment Variables
```bash
# Core settings
ZEREPY_DEBUG=true
ZEREPY_LOG_LEVEL=debug

# Connection settings
ZEREPY_CONNECTION_TIMEOUT=30
ZEREPY_MAX_RETRIES=3

# Plugin settings
ZEREPY_PLUGINS_DIR=~/.zerepy/plugins
```

### Configuration Files
```json
{
    "debug": true,
    "log_level": "debug",
    "connections": {
        "timeout": 30,
        "max_retries": 3
    },
    "plugins": {
        "directory": "~/.zerepy/plugins"
    }
}
```

## Configuration Structure

### Core Configuration
```python
{
    "debug": bool,
    "log_level": str,
    "config_dir": str,
    "plugins_dir": str
}
```

### Connection Configuration
```python
{
    "name": str,
    "type": str,
    "credentials": {
        "api_key": str,
        "api_secret": str,
        "access_token": str
    },
    "options": {
        "timeout": int,
        "retries": int
    }
}
```

### Plugin Configuration
```python
{
    "name": str,
    "version": str,
    "type": str,
    "config": {
        "enabled": bool,
        "options": dict
    }
}
```

## Configuration Validation

### Schema Validation
```python
from src.config.validation import SchemaValidator

schema = {
    "name": {"required": True, "type": str},
    "version": {"required": True, "type": str},
    "options": {
        "type": dict,
        "schema": {
            "timeout": {"type": int},
            "retries": {"type": int}
        }
    }
}

validator = SchemaValidator(schema)
errors = validator.validate(config)
```

### Custom Validation
```python
from src.config.validation import ConfigValidator

class MyConfigValidator(ConfigValidator):
    def validate(self, config):
        errors = []
        if "required_field" not in config:
            errors.append("Missing required field")
        return errors
```

## Using Configuration

### Loading Configuration
```python
from src.config.settings import settings

# Get setting with default
debug = settings.get("debug", False)

# Get required setting
api_key = settings.get("api_key")
if api_key is None:
    raise ValueError("API key is required")
```

### Setting Configuration
```python
from src.config.settings import settings

# Set setting
settings.set("timeout", 30)

# Delete setting
settings.delete("old_setting")
```

### Configuration Providers
```python
from src.config.providers import EnvConfigProvider, FileConfigProvider
from src.config.composite import CompositeConfigProvider

providers = CompositeConfigProvider([
    EnvConfigProvider(".env"),
    FileConfigProvider("config.json")
])

value = providers.get("setting_name")
```

## Best Practices

### Configuration Management
1. Use environment variables for sensitive data
2. Use configuration files for defaults
3. Validate all configuration
4. Document all options

### Security
1. Never commit sensitive data
2. Use environment variables for secrets
3. Validate credential format
4. Rotate secrets regularly

### Validation
1. Define clear schemas
2. Validate early
3. Provide clear errors
4. Handle missing values

### Organization
1. Group related settings
2. Use clear naming
3. Document defaults
4. Version configurations

## Common Issues

### Missing Configuration
```python
def get_required(key: str) -> str:
    value = settings.get(key)
    if value is None:
        raise ValueError(f"Required setting missing: {key}")
    return value
```

### Type Conversion
```python
def get_int(key: str, default: int = 0) -> int:
    value = settings.get(key, default)
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
```

### Validation Errors
```python
def validate_config():
    errors = validator.validate(config)
    if errors:
        for error in errors:
            logger.error(f"Config error: {error}")
        raise ValueError("Invalid configuration")
```

## Examples

### Basic Setup
```python
# Load configuration
from src.config.settings import settings

# Core settings
debug = settings.get("debug", False)
log_level = settings.get("log_level", "info")

# Configure logging
logging.basicConfig(level=log_level.upper())
```

### Connection Setup
```python
# Connection configuration
connection_config = {
    "name": "my_connection",
    "type": "api",
    "credentials": {
        "api_key": settings.get("API_KEY"),
        "api_secret": settings.get("API_SECRET")
    },
    "options": {
        "timeout": settings.get("TIMEOUT", 30),
        "retries": settings.get("RETRIES", 3)
    }
}

# Validate configuration
validator = ConnectionConfigValidator()
errors = validator.validate(connection_config)
if not errors:
    connection = create_connection(connection_config)
```

### Plugin Setup
```python
# Plugin configuration
plugin_config = {
    "name": "my_plugin",
    "version": "1.0.0",
    "type": "connection",
    "config": {
        "enabled": settings.get("PLUGIN_ENABLED", True),
        "options": {
            "feature_flag": settings.get("FEATURE_FLAG", False)
        }
    }
}

# Validate and load plugin
validator = PluginConfigValidator()
errors = validator.validate(plugin_config)
if not errors:
    plugin = load_plugin(plugin_config)
```

## Migration

### Version 1.x to 2.x
```python
# Old configuration
old_config = {
    "setting": "value"
}

# New configuration
new_config = {
    "settings": {
        "key": "value"
    }
}

# Migration function
def migrate_config(config):
    if "setting" in config:
        return {
            "settings": {
                "key": config["setting"]
            }
        }
    return config
```

### Legacy Support
```python
def get_setting(key: str, default: Any = None) -> Any:
    # Try new location first
    value = settings.get(f"settings.{key}")
    if value is not None:
        return value
        
    # Fall back to legacy location
    return settings.get(key, default)
```
