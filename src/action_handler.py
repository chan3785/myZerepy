"""Action handling system for ZerePy."""
import logging
import asyncio
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar
from pathlib import Path
from src.plugins.registry import PluginRegistry
from src.plugins.discovery import discover_plugins
from src.plugins.base import ActionPlugin
from src.events.bus import event_bus, Event

logger = logging.getLogger("action_handler")

T = TypeVar('T')

class ActionHandler:
    """Handler for managing and executing actions."""
    
    def __init__(self):
        """Initialize action handler."""
        self._plugin_registry = PluginRegistry()
        self._actions: Dict[str, ActionPlugin] = {}
        self._load_plugins()
        
    def _load_plugins(self) -> None:
        """Load action plugins."""
        # Load built-in plugins
        plugin_dir = Path(__file__).parent / "actions"
        plugins = discover_plugins(str(plugin_dir))
        
        # Load user plugins if they exist
        user_plugin_dir = Path.home() / ".zerepy" / "plugins" / "actions"
        if user_plugin_dir.exists():
            user_plugins = discover_plugins(str(user_plugin_dir))
            plugins.update(user_plugins)
            
        # Register plugins
        for name, plugin_cls in plugins.items():
            self._plugin_registry.register("action", name, plugin_cls)
            
    def register_action(self, name: str, action: ActionPlugin) -> None:
        """
        Register an action.
        
        Args:
            name: Action name
            action: Action plugin instance
        """
        self._actions[name] = action
        
    async def execute_action(self, name: str, params: Dict[str, Any]) -> Optional[Any]:
        """
        Execute an action with retry logic.
        
        Args:
            name: Action name
            params: Action parameters
            
        Returns:
            Action result or None if failed
        """
        if name not in self._actions:
            logger.error(f"Action {name} not found")
            return None
            
        action = self._actions[name]
        
        # Validate parameters
        errors = action.validate_params(params)
        if errors:
            logger.error(f"Invalid parameters: {', '.join(errors)}")
            return None
            
        # Publish action start event
        await event_bus.publish(Event(
            name=f"action.{name}.start",
            data={"params": params},
            source="action_handler"
        ))
        
        try:
            result = await self._execute_with_retry(action.execute, params)
            
            # Publish success event
            await event_bus.publish(Event(
                name=f"action.{name}.success",
                data={"result": result},
                source="action_handler"
            ))
            
            return result
            
        except Exception as e:
            # Publish failure event
            await event_bus.publish(Event(
                name=f"action.{name}.failure",
                data={"error": str(e)},
                source="action_handler"
            ))
            logger.error(f"Action {name} failed: {e}")
            return None
            
    async def _execute_with_retry(
        self, 
        func: Callable[..., T], 
        params: Dict[str, Any],
        max_retries: int = 3,
        base_delay: float = 1.0
    ) -> T:
        """Execute function with retry logic."""
        last_error = None
        
        for attempt in range(max_retries):
            try:
                return await func(params)
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    logger.warning(
                        f"Action failed (attempt {attempt + 1}/{max_retries}), "
                        f"retrying in {delay:.1f}s: {e}"
                    )
                    await asyncio.sleep(delay)
                    
        if last_error:
            raise last_error
        return None

# Global action handler instance
action_handler = ActionHandler()

# Backward compatibility layer
def register_action(name: str) -> Callable:
    """
    Legacy decorator for registering actions.
    
    Args:
        name: Action name
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        # Create action plugin from function
        class LegacyAction(ActionPlugin):
            @property
            def name(self) -> str:
                return name
                
            @property
            def version(self) -> str:
                return "1.0.0"
                
            def initialize(self, config: Dict[str, Any]) -> None:
                pass
                
            def cleanup(self) -> None:
                pass
                
            def validate_params(self, params: Dict[str, Any]) -> List[str]:
                return []
                
            async def execute(self, params: Dict[str, Any]) -> Any:
                return await func(**params)
                
        # Register action
        action_handler.register_action(name, LegacyAction())
        return func
    return decorator

# Backward compatibility function
async def execute_action(agent: Any, name: str, **kwargs) -> Any:
    """
    Legacy function for executing actions.
    
    Args:
        agent: Agent instance
        name: Action name
        **kwargs: Action parameters
        
    Returns:
        Action result
    """
    return await action_handler.execute_action(name, kwargs)
