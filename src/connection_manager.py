"""Connection management for ZerePy."""
import logging
import os
from typing import Any, List, Optional, Type, Dict
from pathlib import Path
from src.plugins.registry import PluginRegistry
from src.plugins.discovery import discover_plugins
from src.plugins.base import ConnectionPlugin
from src.resources.manager import resource_manager
from src.events.bus import event_bus, Event

logger = logging.getLogger("connection_manager")

class ConnectionManager:
    def __init__(self, agent_config):
        """Initialize connection manager."""
        self.connections: Dict[str, ConnectionPlugin] = {}
        self._plugin_registry = PluginRegistry()
        self._load_plugins()
        self._setup_connections(agent_config)
        
    def _load_plugins(self) -> None:
        """Load connection plugins."""
        # Load built-in plugins
        plugin_dir = Path(__file__).parent / "connections"
        plugins = discover_plugins(str(plugin_dir))
        
        # Load user plugins if they exist
        user_plugin_dir = Path.home() / ".zerepy" / "plugins" / "connections"
        if user_plugin_dir.exists():
            user_plugins = discover_plugins(str(user_plugin_dir))
            plugins.update(user_plugins)
            
        # Register plugins
        for name, plugin_cls in plugins.items():
            self._plugin_registry.register("connection", name, plugin_cls)
            
    def _setup_connections(self, agent_config) -> None:
        """Initialize connections with proper error handling."""
        for config in agent_config:
            try:
                self._register_connection(config)
            except Exception as e:
                logger.error(f"Failed to initialize connection {config.get('name')}: {e}")
                self._cleanup_connection(config.get('name'))
                
    def _get_connection_class(self, name: str) -> Optional[Type[ConnectionPlugin]]:
        """Get connection class from registry."""
        try:
            return self._plugin_registry.get_plugin("connection", name)
        except Exception as e:
            logger.error(f"Failed to get connection class {name}: {e}")
            return None
            
    def _register_connection(self, config: Dict[str, Any]) -> None:
        """
        Create and register a new connection with configuration.
        
        Args:
            config: Configuration dictionary for the connection
        """
        try:
            name = config["name"]
            connection_class = self._get_connection_class(name)
            if not connection_class:
                logger.error(f"Connection type {name} not found")
                return
                
            # Create and initialize connection
            connection = connection_class(config)
            connection.initialize(config)
            
            # Register with resource manager
            resource_manager.register("connection", name, connection)
            self.connections[name] = connection
            
            # Publish connection registered event
            event_bus.publish(Event(
                name="connection.registered",
                data={"name": name},
                source="connection_manager"
            ))
            
        except Exception as e:
            logger.error(f"Failed to initialize connection {config.get('name')}: {e}")
            self._cleanup_connection(config.get('name'))
            
    def _cleanup_connection(self, name: str) -> None:
        """Clean up a connection's resources."""
        if name in self.connections:
            try:
                resource_manager.cleanup("connection", name)
                del self.connections[name]
            except Exception as e:
                logger.error(f"Error cleaning up connection {name}: {e}")
                
    def _check_connection(self, connection_name: str) -> bool:
        """Check if a connection is configured and working."""
        try:
            connection = self.connections[connection_name]
            return connection.is_configured(verbose=True)
        except KeyError:
            logger.error("Unknown connection. Try 'list-connections' to see available connections.")
            return False
        except Exception as e:
            logger.error(f"Error checking connection: {e}")
            return False

    async def configure_connection(self, connection_name: str) -> bool:
        """Configure a specific connection."""
        try:
            connection = self.connections[connection_name]
            success = connection.configure()

            if success:
                await event_bus.publish(Event(
                    name="connection.configured",
                    data={"name": connection_name},
                    source="connection_manager"
                ))
                logger.info(f"Successfully configured connection: {connection_name}")
            else:
                logger.error(f"Failed to configure connection: {connection_name}")
            return success

        except KeyError:
            logger.error("Unknown connection. Try 'list-connections' to see available connections.")
            return False
        except Exception as e:
            logger.error(f"Error configuring connection: {e}")
            return False

    def list_connections(self) -> None:
        """List all available connections and their status."""
        logger.info("\nAvailable Connections:")
        for name, connection in self.connections.items():
            status = "✅ Configured" if connection.is_configured() else "❌ Not Configured"
            logger.info(f"- {name}: {status}")

    def list_actions(self, connection_name: str) -> None:
        """List all available actions for a specific connection."""
        try:
            connection = self.connections[connection_name]
            if not connection.is_configured():
                logger.info(f"{connection_name} is not configured. Configure it first.")
                return

            logger.info(f"\nAvailable actions for {connection_name}:")
            for action_name, action in connection.actions.items():
                logger.info(f"- {action_name}: {action.description}")
                logger.info("  Parameters:")
                for param in action.parameters:
                    req = "required" if param.required else "optional"
                    logger.info(f"    - {param.name} ({req}): {param.description}")

        except KeyError:
            logger.error("Unknown connection. Try 'list-connections' to see available connections.")
        except Exception as e:
            logger.error(f"Error listing actions: {e}")

    async def perform_action(
        self, connection_name: str, action_name: str, params: List[Any]
    ) -> Optional[Any]:
        """
        Perform an action on a specific connection with given parameters.
        
        Args:
            connection_name: Name of the connection to use
            action_name: Name of the action to perform
            params: List of parameters for the action
            
        Returns:
            Result of the action or None if it fails
        """
        try:
            connection = self.connections[connection_name]

            if not connection.is_configured():
                logger.error(f"Connection '{connection_name}' is not configured")
                return None

            if action_name not in connection.actions:
                logger.error(
                    f"Unknown action '{action_name}' for connection '{connection_name}'"
                )
                return None

            action = connection.actions[action_name]

            # Convert list of params to kwargs dictionary
            kwargs = {}
            param_index = 0

            # Add provided parameters
            for param in action.parameters:
                if param_index < len(params):
                    kwargs[param.name] = params[param_index]
                    param_index += 1

            # Validate required parameters
            missing_required = [
                param.name
                for param in action.parameters
                if param.required and param.name not in kwargs
            ]

            if missing_required:
                logger.error(
                    f"Missing required parameters: {', '.join(missing_required)}"
                )
                return None

            # Publish action start event
            await event_bus.publish(Event(
                name=f"{connection_name}.{action_name}.start",
                data={"params": kwargs},
                source="connection_manager"
            ))

            try:
                result = connection.perform_action(action_name, kwargs)
                
                # Publish success event
                await event_bus.publish(Event(
                    name=f"{connection_name}.{action_name}.success",
                    data={"result": result},
                    source="connection_manager"
                ))
                
                return result
                
            except Exception as e:
                # Publish failure event
                await event_bus.publish(Event(
                    name=f"{connection_name}.{action_name}.failure",
                    data={"error": str(e)},
                    source="connection_manager"
                ))
                raise

        except Exception as e:
            logger.error(
                f"Error performing action {action_name} for {connection_name}: {e}"
            )
            return None

    def get_model_providers(self) -> List[str]:
        """Get a list of all LLM provider connections."""
        return [
            name
            for name, conn in self.connections.items()
            if conn.is_configured() and getattr(conn, "is_llm_provider", lambda: False)
        ]

    def __del__(self):
        """Ensure cleanup on deletion."""
        for name in list(self.connections.keys()):
            self._cleanup_connection(name)
