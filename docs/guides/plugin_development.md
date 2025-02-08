# Plugin Development Guide

## Overview
This guide explains how to create and integrate plugins with the ZerePy framework. Plugins provide a way to extend the framework's functionality through standardized interfaces.

## Getting Started

### Plugin Types
1. **Connection Plugins**
   - Network connections
   - API integrations
   - Protocol implementations

2. **Action Plugins**
   - Custom actions
   - Task handlers
   - Data processors

### Basic Structure
```python
from typing import Dict, Any, List
from src.plugins.base import PluginBase

class MyPlugin(PluginBase):
    @property
    def name(self) -> str:
        return "my_plugin"
        
    @property
    def version(self) -> str:
        return "1.0.0"
        
    def initialize(self, config: Dict[str, Any]) -> None:
        # Initialize plugin
        pass
        
    def cleanup(self) -> None:
        # Clean up resources
        pass
```

## Creating Plugins

### Connection Plugin
```python
from src.plugins.base import ConnectionPlugin

class MyConnection(ConnectionPlugin):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.client = None
        
    def initialize(self, config: Dict[str, Any]) -> None:
        # Set up connection
        self.client = MyClient(config)
        
    def cleanup(self) -> None:
        # Clean up connection
        if self.client:
            self.client.close()
            
    def is_configured(self) -> bool:
        return self.client is not None
        
    def perform_action(self, action: str, params: Dict[str, Any]) -> Any:
        # Execute action
        return self.client.execute(action, params)
```

### Action Plugin
```python
from src.plugins.base import ActionPlugin

class MyAction(ActionPlugin):
    def validate_params(self, params: Dict[str, Any]) -> List[str]:
        errors = []
        if 'required_param' not in params:
            errors.append("Missing required parameter")
        return errors
        
    async def execute(self, params: Dict[str, Any]) -> Any:
        # Execute action
        result = process_data(params)
        return result
```

## Configuration

### Plugin Config
```python
{
    "name": "my_plugin",
    "version": "1.0.0",
    "type": "connection",  # or "action"
    "config": {
        "enabled": true,
        "options": {
            "timeout": 30,
            "retries": 3
        }
    }
}
```

### Validation
```python
from src.config.validation import ConfigValidator

class MyPluginValidator(ConfigValidator):
    def validate(self, config: Dict[str, Any]) -> List[str]:
        errors = []
        if 'timeout' not in config['options']:
            errors.append("Timeout is required")
        return errors
```

## Event Integration

### Publishing Events
```python
from src.events.bus import event_bus, Event

async def my_action():
    await event_bus.publish(Event(
        name="my_plugin.action.start",
        data={"param": "value"},
        source="my_plugin"
    ))
```

### Subscribing to Events
```python
from src.events.decorators import subscribe_to

@subscribe_to("system.initialized")
def handle_system_init(event: Event):
    # Handle system initialization
    pass
```

## Resource Management

### Resource Tracking
```python
from src.resources.manager import resource_manager

def initialize():
    # Register resources
    resource_manager.register(
        category="my_plugin",
        name="my_resource",
        resource=MyResource()
    )
```

### Cleanup
```python
def cleanup():
    # Clean up resources
    resource_manager.cleanup(
        category="my_plugin",
        name="my_resource"
    )
```

## Installation

### Directory Structure
```
~/.zerepy/plugins/
├── connections/
│   └── my_connection/
│       ├── __init__.py
│       └── plugin.py
└── actions/
    └── my_action/
        ├── __init__.py
        └── plugin.py
```

### Plugin Package
```python
# __init__.py
from .plugin import MyPlugin

__all__ = ['MyPlugin']
```

## Testing

### Unit Tests
```python
import pytest
from src.plugins.base import PluginBase

def test_plugin_initialization():
    plugin = MyPlugin()
    config = {"option": "value"}
    plugin.initialize(config)
    assert plugin.is_configured()
```

### Integration Tests
```python
@pytest.mark.asyncio
async def test_plugin_action():
    plugin = MyPlugin()
    result = await plugin.execute({"param": "value"})
    assert result is not None
```

## Best Practices

### Error Handling
1. Use proper error types
2. Implement retries
3. Clean up resources
4. Log errors

### Resource Management
1. Track resources
2. Implement cleanup
3. Handle timeouts
4. Monitor usage

### Configuration
1. Validate configs
2. Use proper scopes
3. Handle missing values
4. Document options

### Testing
1. Write unit tests
2. Add integration tests
3. Test error cases
4. Verify cleanup

## Common Issues

### Initialization Failures
```python
def initialize(self, config: Dict[str, Any]) -> None:
    try:
        self.client = setup_client(config)
    except Exception as e:
        logger.error(f"Failed to initialize: {e}")
        raise
```

### Resource Leaks
```python
def cleanup(self) -> None:
    try:
        if self.client:
            self.client.close()
    finally:
        self.client = None
```

### Configuration Issues
```python
def validate_config(self, config: Dict[str, Any]) -> List[str]:
    errors = []
    for required in ['api_key', 'secret']:
        if required not in config:
            errors.append(f"Missing {required}")
    return errors
```

## Debugging

### Logging
```python
import logging

logger = logging.getLogger(__name__)

def my_action():
    logger.debug("Starting action")
    try:
        result = process()
        logger.info("Action completed")
        return result
    except Exception as e:
        logger.error(f"Action failed: {e}")
        raise
```

### Event Monitoring
```python
@subscribe_to("*")
def monitor_events(event: Event):
    logger.debug(f"Event: {event.name} from {event.source}")
```

### Resource Tracking
```python
def check_resources():
    stats = resource_manager.get_stats("my_plugin")
    logger.info(f"Resource stats: {stats}")
```
