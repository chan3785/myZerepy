import logging
import json
from typing import Dict, Any, Optional
from src.connections.base_connection import BaseConnection, Action, ActionParameter
from src.schemas.brain_schemas import BrainResponse, SYSTEM_PROMPT
from src.connections.openai_connection import OpenAIConnection
from src.connections.goat_connection import GoatConnection

logger = logging.getLogger("connections.brain_connection")

class BrainConnectionError(Exception):
    """Base exception for Brain connection errors"""
    pass

class BrainConnection(BaseConnection):
    def __init__(self, config: Dict[str, Any]):
        self.llm_provider = None
        self.model = None
        # Initialize GOAT with debug logging
        logger.info("Initializing GOAT connection...")
        self.goat_connection = GoatConnection(config)
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
            self.validate_config(self.config)
            self.llm_provider = OpenAIConnection(self.config)
            
            if not self._ping_llm_provider():
                raise BrainConnectionError("Failed to connect to LLM provider")

            # Configure GOAT and log available actions
            if not self.goat_connection.is_configured():
                logger.info("Configuring GOAT connection...")
                if not self.goat_connection.configure():
                    raise BrainConnectionError("Failed to configure GOAT connection")
            
            # Log available GOAT actions for debugging
            logger.info("Available GOAT actions:")
            for action_name, action in self.goat_connection.actions.items():
                logger.info(f"  - {action_name}: {action.description}")

            logger.info("Brain connection configured successfully!")
            return True
        except Exception as e:
            logger.error(f"Brain configuration failed: {e}")
            return False

    def is_configured(self, verbose: bool = False) -> bool:
        is_ready = (self.llm_provider is not None and 
                   self.model is not None and 
                   self.goat_connection.is_configured())
        if verbose and not is_ready:
            if not self.llm_provider:
                logger.error("LLM provider not configured")
            if not self.model:
                logger.error("Model not specified")
            if not self.goat_connection.is_configured():
                logger.error("GOAT connection not configured")
        return is_ready

    def _ping_llm_provider(self) -> bool:
        try:
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
            response = self.llm_provider.perform_action(
                "generate-text",
                kwargs={
                    "prompt": command,
                    "system_prompt": SYSTEM_PROMPT,
                    "model": self.config["model"]
                }
            )
            parsed = json.loads(response)
            return BrainResponse(**parsed)
        except Exception as e:
            logger.error(f"Failed to parse intent: {e}")
            return BrainResponse(
                note=f"Sorry, I couldn't understand that request: {str(e)}",
                action="none"
            )

    def _get_goat_action_name(self, brain_action: str) -> Optional[str]:
        """Get corresponding GOAT action name with validation"""
        # Get actual available actions from GOAT
        available_actions = set(self.goat_connection.actions.keys())
        logger.debug(f"Available GOAT actions: {available_actions}")
        logger.debug(f"Looking up brain action: {brain_action}")
        logger.debug(f"Plugin methods found: {[method for method in dir(self.goat_connection) if not method.startswith('_')]}")

        
        # Define mapping based on actual plugin method names
        action_mapping = {
            "get_coin_price": "get_coin_price",     # CoinGeckoService method
            "get_trending": "get_trending_coins",    # CoinGeckoService method
            "search_coins": "search_coins",          # CoinGeckoService method
            "token_balance": "get_token_balance",    # Erc20Service method
            "token_transfer": "transfer",            # Erc20Service method  
            "token_approve": "approve"               # Erc20Service method
        }
        
        goat_action = action_mapping.get(brain_action)
        if goat_action and goat_action in available_actions:
            return goat_action
        
        logger.error(f"No matching GOAT action found for brain action: {brain_action}")
        logger.error(f"Available actions: {available_actions}")
        return None

    def _execute_goat_action(self, action: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """Execute action using GOAT connection"""
        try:
            logger.debug(f"Executing GOAT action: {action} with details: {details}")
            result = self.goat_connection.perform_action(action, **details)
            return {
                "success": True,
                "result": result
            }
        except Exception as e:
            logger.error(f"GOAT action execution failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def process_command(self, command: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        try:
            # Parse intent using LLM
            response = self._parse_intent(command, context)
            logger.debug(f"Parsed intent: {response}")
            
            if response.action == "none":
                return {
                    "success": True,
                    "message": response.note,
                    "action": "none"
                }

            # Get corresponding GOAT action
            goat_action = self._get_goat_action_name(response.action)
            if not goat_action:
                return {
                    "success": False,
                    "message": f"Unsupported action: {response.action}",
                    "action": "none"
                }

            # Convert response details to dictionary if present
            details = response.details.dict() if response.details else {}
            
            # Execute action and return result
            result = self._execute_goat_action(goat_action, details)
            result["message"] = response.note
            result["action"] = response.action
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