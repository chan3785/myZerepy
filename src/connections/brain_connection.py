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
        self.model = None
        # Add network configs for each chain
        self.eth_config = {"name": "ethereum", "rpc": "https://eth.blockrazor.xyz" }
        self.solana_config = {"name": "solana", "rpc": "https://api.mainnet-beta.solana.com"}
        self.sonic_config = {"name": "sonic", "network": "mainnet"}
        
        self.connections = {
            "ethereum": EthereumConnection(self.eth_config),
            "solana": SolanaConnection(self.solana_config), 
            "sonic": SonicConnection(self.sonic_config)
        }
        super().__init__(config)
        self.load_configuration()

    def load_configuration(self):
        """Load configuration from persistent storage."""
        self.model = self.config.get("model")
        self.llm_provider = self.config.get("llm_provider")

        if not self.model or not self.llm_provider:
            raise ValueError("Configuration must include 'model' and 'llm_provider'")

    @property
    def is_llm_provider(self) -> bool:
        return False

    def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        required_fields = ["llm_provider", "model"]
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
            # add others as desired
        }
        return provider_map.get(provider_name)

    def is_configured(self, verbose: bool = False) -> bool:
        is_ready = self.llm_provider is not None and self.model is not None
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
                kwargs={"model": self.model}
            )
            return response is not None
        except Exception as e:
            logger.error(f"Ping to LLM provider failed: {e}")
            return False

    def _parse_intent(self, command: str, context: Optional[Dict] = None) -> BrainResponse:
        try:
            logger.info(f"\nProcessing command: {command}")
            
            response = self.llm_provider.perform_action(
                "generate-text",
                kwargs={
                    "prompt": command,
                    "system_prompt": SYSTEM_PROMPT,
                    "model": self.config["model"]
                }
            )
            
            logger.info(f"\nRaw LLM response: {response}")
            
            # Parse and validate response 
            parsed = json.loads(response)
            brain_response = BrainResponse(**parsed)
            logger.info(f"\nParsed response: {brain_response.json(indent=2)}")
            
            return brain_response

        except Exception as e:
            logger.error(f"\nFailed to parse intent: {str(e)}")
            return BrainResponse(
                note=f"Sorry, I couldn't understand that request: {str(e)}",
                action="none",
                connection="none"
            )


    # def _execute_swap(self, details) -> Dict[str, Any]:
    #     return self.goat_connection.perform_action(
    #         "swap",
    #         kwargs={
    #             "token_in": details.input_mint,
    #             "token_out": details.output_mint,
    #             "amount": details.amount,
    #             "slippage": details.slippage_bps / 10000  # Convert bps to decimal
    #         }
    #     )

    # def get_available_actions(self) -> Dict[str, Dict[str, Any]]:
    #     """Get all available actions from GOAT plugins with their parameters"""
    #     if not self.goat_connection:
    #         raise BrainConnectionError("GOAT connection not configured")
            
    #     actions = {}
    #     for action_name, tool in self.goat_connection._action_registry.items():
    #         actions[action_name] = {
    #             "description": tool.description,
    #             "parameters": tool.parameters.model_fields
    #         }
    #     return actions

    # def _execute_send(self, details) -> Dict[str, Any]:
    #     return self.goat_connection.perform_action(
    #         "transfer",
    #         kwargs={
    #             "to_address": details.recipient,
    #             "amount": details.amount,
    #             "token_address": details.token_mint,
    #             "network": details.network
    #         }
    #     )

    
    def process_command(self, command: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        try:
            logger.info("\nStarting command processing")
            response = self._parse_intent(command, context)
            
            result = {
                "success": True,
                "message": response.note,
                "action": response.action
            }

            # Get the appropriate connection
            connection = self.connections.get(response.connection)
            if not connection:
                error_msg = f"Connection {response.connection} not found"
                logger.error(f"\n{error_msg}")
                raise BrainConnectionError(error_msg)

            logger.info(f"\n🔗 Using connection: {response.connection}")

            # Execute action
            if response.action == "swap" and response.swap_details:
                logger.info(f"\n💱 Executing swap: {response.swap_details.json(indent=2)}")
                result.update(connection.swap(**response.swap_details.dict()))
            elif response.action == "send" and response.send_details:
                logger.info(f"\n📤 Executing transfer: {response.send_details.json(indent=2)}")
                result.update(connection.transfer(**response.send_details.dict()))

            logger.info(f"\nCommand processed successfully: {json.dumps(result, indent=2)}")
            return result
            
        except Exception as e:
            error_msg = f"Command processing failed: {str(e)}"
            logger.error(f"\n{error_msg}")
            return {
                "success": False, 
                "message": error_msg,
                "action": "none"
            }

    def perform_action(self, action_name: str, kwargs: Dict[str, Any]) -> Any:
        if action_name == "process-command":
            try:
                command = kwargs.get("command")
                context = kwargs.get("context")
                if not command:
                    raise ValueError("Command parameter is required")
                    
                logger.info(f"\nExecuting action: {action_name}")
                logger.info(f"\nCommand: {command}")
                logger.info(f"\nContext: {context}")
                
                result = self.process_command(command, context)
                
                logger.info(f"\nAction result: {json.dumps(result, indent=2)}")
                return result
                
            except Exception as e:
                logger.error(f"\nAction failed: {str(e)}", exc_info=True)
                raise

        # Rest of the method remains the same
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