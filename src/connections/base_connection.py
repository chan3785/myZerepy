import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Callable
from dataclasses import dataclass
from langgraph.prebuilt import ToolExecutor

@dataclass
class ActionParameter:
    name: str
    required: bool
    type: type
    description: str

@dataclass
class Action:
    name: str
    parameters: List[ActionParameter]
    description: str
    
    def validate_params(self, params: Dict[str, Any]) -> List[str]:
        errors = []
        for param in self.parameters:
            if param.required and param.name not in params:
                errors.append(f"Missing required parameter: {param.name}")
            elif param.name in params:
                try:
                    params[param.name] = param.type(params[param.name])
                except ValueError:
                    errors.append(f"Invalid type for {param.name}. Expected {param.type.__name__}")
        return errors

class BaseConnection(ABC):
    def __init__(self, config):
        try:
            # Dictionary to store action name -> handler method mapping
            self.actions: Dict[str, Callable] = {}
            # Dictionary to store some essential configuration
            self.config = self.validate_config(config) 
            # Register actions during initialization
            self.register_actions()
        #Create tool executor for registered actions 
            tools = [self._create_tool(action) for action in self.actions.values()]
            self.tool_executor = ToolExecutor(tools)
        except Exception as e:
            logging.error("Could not initialize the connection")
            raise e
    
    def _create_tool(self, action: Action) -> Callable:
            """Convert an Action to a LangGraph tool format"""
            
            def tool_wrapper(tool_input: dict):
                print(f"Tool invoked: {action.name} with arguments: {tool_input}")
                
                '''
                # Validate required parameters
                missing_params = [param.name for param in action.parameters if param.required and param.name not in tool_input]
                if missing_params:
                    raise ValueError(f"Missing required parameters for {action.name}: {', '.join(missing_params)}")'''
                
                missing_params = [param.name for param in action.parameters if param.required and param.name not in tool_input]
                all_required_params = [param.name for param in action.parameters if param.required]
                
                if missing_params:
                    print(f"⚠️ Missing required parameters for {action.name}: {missing_params}")
                    return {
                        "status": "missing_params",
                        "message": f"Missing required parameters for {action.name}: {', '.join(missing_params)}",
                        "missing_params": missing_params,
                        "required_params": all_required_params  # NEW: Return all required parameters
                    }

                method_name = action.name.replace('-', '_')
                method = getattr(self, method_name)
                return method(**tool_input) 

            tool_wrapper.__name__ = action.name
            tool_wrapper.__doc__ = action.description
            
            tool_wrapper.__annotations__ = {
                param.name: param.type 
                for param in action.parameters
            }

            return tool_wrapper

    @property
    @abstractmethod
    def is_llm_provider(self):
        pass

    @abstractmethod
    def validate_config(self, config) -> Dict[str, Any]:
        """
        Validate config from JSON

        Args:
            config: dictionary containing all the config values for that connection
        
        Returns:
            Dict[str, Any]: Returns the config if valid
        
        Raises:
            Error if the configuration is not valid
        """

    @abstractmethod
    def configure(self, **kwargs) -> bool:
        """
        Configure the connection with necessary credentials.
        
        Args:
            **kwargs: Configuration parameters
            
        Returns:
            bool: True if configuration was successful, False otherwise
        """
        pass

    @abstractmethod
    def is_configured(self, verbose = False) -> bool:
        """
        Check if the connection is properly configured and ready for use.
        
        Returns:
            bool: True if the connection is configured, False otherwise
        """
        pass

    @abstractmethod
    def register_actions(self) -> None:
        """
        Register all available actions for this connection.
        Should populate self.actions with action_name -> handler mappings.
        """
        pass

    def perform_action(self, action_name: str, **kwargs) -> Any:
        """
        Perform a registered action with the given parameters. 
        
        Args:
            action_name: Name of the action to perform
            **kwargs: Parameters for the action
            
        Returns:
            Any: Result of the action
            
        Raises:
            KeyError: If the action is not registered
            ValueError: If the action parameters are invalid
        """
        if action_name not in self.actions:
            raise KeyError(f"Unknown action: {action_name}")
            
        handler = self.actions[action_name]
        return handler(**kwargs)
