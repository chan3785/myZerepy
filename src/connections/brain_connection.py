import logging
import json
from typing import Dict, Any, Optional
from src.connections.base_connection import BaseConnection, Action, ActionParameter
from src.schemas.brain_schemas import BrainResponse, SYSTEM_PROMPT

logger = logging.getLogger("connections.brain_connection")

class BrainConnectionError(Exception):
    """Base exception for Brain connection errors"""
    pass

class BrainConnection(BaseConnection):
    def __init__(self, config: Dict[str, Any]):
        self.llm_provider = None
        self.goat_connection = None
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
            # Get LLM provider
            llm_name = self.config["llm_provider"]
            llm_connections = [
                conn for name, conn in self.connection_manager.connections.items()
                if conn.is_llm_provider and name == llm_name
            ]
            if not llm_connections:
                raise BrainConnectionError(f"LLM provider {llm_name} not found")
            self.llm_provider = llm_connections[0]
            
            # Get GOAT connection
            if "goat" not in self.connection_manager.connections:
                raise BrainConnectionError("GOAT connection not found")
            self.goat_connection = self.connection_manager.connections["goat"]
            
            return True
        except Exception as e:
            logger.error(f"Brain configuration failed: {e}")
            return False

    def is_configured(self, verbose: bool = False) -> bool:
        is_ready = self.llm_provider is not None and self.goat_connection is not None
        if verbose and not is_ready:
            logger.error("Brain connection not fully configured")
        return is_ready

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

            # Execute action if needed
            if response.action == "swap" and response.swap_details:
                execution = self._execute_swap(response.swap_details)
                result.update(execution)
            elif response.action == "send" and response.send_details:
                execution = self._execute_send(response.send_details)
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