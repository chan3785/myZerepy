import logging
import json
from typing import Dict, Any, Optional
from src.connections.base_connection import BaseConnection, Action, ActionParameter
from src.schemas.brain_schemas import BrainResponse, SYSTEM_PROMPT
from src.connections.openai_connection import OpenAIConnection
from src.connections.ethereum_connection import EthereumConnection
from src.connections.solana_connection import SolanaConnection
from src.connections.sonic_connection import SonicConnection
from src.connections.anthropic_connection import AnthropicConnection

logger = logging.getLogger("connections.brain_connection")

class BrainConnectionError(Exception):
    """Base exception for Brain connection errors"""
    pass

class BrainConnection(BaseConnection):
    def __init__(self, config: Dict[str, Any]):
        self.llm_provider = None
        super().__init__(config)

    @property
    def is_llm_provider(self) -> bool:
        return False

    def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        required_fields = ["llm_provider", "llm_model"]
        missing = [f for f in required_fields if f not in config]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")
        return config

    def register_actions(self) -> None:
        self.actions = {
            "process-command": Action(
                name="process-command",
                parameters=[
                    ActionParameter("command", True, str, "Natural language command to process"),
                    ActionParameter("context", False, dict, "Additional context for processing")
                ],
                description="Process natural language into blockchain action"
            )
        }

    def configure(self) -> bool:
        try:
            # Validate LLM provider and model
            self.validate_config(self.config)

            # Instantiate the LLM provider based on the config
            provider_class = self._get_provider_class(self.config["llm_provider"])
            self.llm_provider = provider_class(self.config)

            # Perform a simple action to check if the connection works
            response = self._ping_llm_provider()
            if not response:
                raise BrainConnectionError("Failed to connect to LLM provider")

            logger.info("Brain connection configured successfully! 🎉")
            return True
        except Exception as e:
            logger.error(f"Brain configuration failed: {e}")
            return False

    def _get_provider_class(self, provider_name: str):
        # Map provider names to their respective classes
        provider_map = {
            "openai": OpenAIConnection,
            "anthropic": AnthropicConnection,
            "eternalai": EternalAIConnection,
            # Add other providers as needed
        }
        return provider_map.get(provider_name)

    def is_configured(self, verbose: bool = False) -> bool:
        is_ready = self.llm_provider is not None and self.llm_model is not None
        if verbose:
            if is_ready:
                logger.info("Brain connection is fully configured")
            else:
                logger.error("Brain connection not fully configured")
        return is_ready

    def _ping_llm_provider(self) -> bool:
        try:
            # Simulate a simple action to verify the connection
            response = self.llm_provider.perform_action(
                "check-model",
                kwargs={"model": self.llm_model}
            )
            return response is not None
        except Exception as e:
            logger.error(f"Ping to LLM provider failed: {e}")
            return False

    def _parse_intent(self, command: str, context: Optional[Dict] = None) -> BrainResponse:
        try:
            response = self.llm_provider.perform_action(
                "generate-text",
                kwargs={
                    "prompt": command,
                    "system_prompt": SYSTEM_PROMPT,
                    "model": self.config["llm_model"]
                }
            )
            
            # Parse and validate response using Pydantic
            parsed = json.loads(response)
            return BrainResponse(**parsed)

        except Exception as e:
            logger.error(f"Failed to parse intent: {e}")
            return BrainResponse(
                note=f"Sorry, I couldn't understand that request: {str(e)}",
                action="none"
            )

    def _execute_swap(self, details) -> Dict[str, Any]:
        return self.goat_connection.perform_action(
            "swap",
            kwargs={
                "token_in": details.input_mint,
                "token_out": details.output_mint,
                "amount": details.amount,
                "slippage": details.slippage_bps / 10000  # Convert bps to decimal
            }
        )

    def get_available_actions(self) -> Dict[str, Dict[str, Any]]:
        """Get all available actions from GOAT plugins with their parameters"""
        if not self.goat_connection:
            raise BrainConnectionError("GOAT connection not configured")
            
        actions = {}
        for action_name, tool in self.goat_connection._action_registry.items():
            actions[action_name] = {
                "description": tool.description,
                "parameters": tool.parameters.model_fields
            }
        return actions

    def _execute_send(self, details) -> Dict[str, Any]:
        return self.goat_connection.perform_action(
            "transfer",
            kwargs={
                "to_address": details.recipient,
                "amount": details.amount,
                "token_address": details.token_mint,
                "network": details.network
            }
        )

    def process_command(self, command: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        try:
            # Parse intent using LLM
            response = self._parse_intent(command, context)
            
            result = {
                "success": True,
                "message": response.note,
                "action": response.action
            }

            # Select the connection based on the LLM's response
            connection = self.connection_manager.connections.get(response.connection)
            if not connection:
                raise BrainConnectionError(f"Connection {response.connection} not found")

            # Execute action if needed
            if response.action == "swap" and response.swap_details:
                execution = connection.perform_action("swap", response.swap_details.dict())
                result.update(execution)
            elif response.action == "send" and response.send_details:
                execution = connection.perform_action("send", response.send_details.dict())
                result.update(execution)

            return result

        except Exception as e:
            logger.error(f"Command processing failed: {e}")
            return {
                "success": False,
                "message": f"Error processing command: {str(e)}",
                "action": "none"
            }

    def perform_action(self, action_name: str, kwargs: Dict[str, Any]) -> Any:
        if action_name not in self.actions:
            raise KeyError(f"Unknown action: {action_name}")

        if not self.is_configured(verbose=True):
            raise BrainConnectionError("Brain connection not configured")

        action = self.actions[action_name]
        errors = action.validate_params(kwargs)
        if errors:
            raise ValueError(f"Invalid parameters: {', '.join(errors)}")

        method = getattr(self, action_name.replace("-", "_"))
        return method(**kwargs)