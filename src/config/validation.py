"""Configuration validation for ZerePy."""
from typing import Any, Dict, List, Optional, Type
from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass
class ValidationError:
    """Validation error details."""
    field: str
    message: str

class ConfigValidator(ABC):
    """Base class for configuration validators."""
    
    @abstractmethod
    def validate(self, config: Dict[str, Any]) -> List[ValidationError]:
        """
        Validate configuration.
        
        Args:
            config: Configuration to validate
            
        Returns:
            List of validation errors
        """
        pass

class ConnectionConfigValidator(ConfigValidator):
    """Validator for connection configurations."""
    
    def validate(self, config: Dict[str, Any]) -> List[ValidationError]:
        errors = []
        
        # Validate required fields
        if 'name' not in config:
            errors.append(ValidationError('name', 'Name is required'))
            
        if 'type' not in config:
            errors.append(ValidationError('type', 'Type is required'))
            
        # Validate credentials if present
        if 'credentials' in config and not isinstance(config['credentials'], dict):
            errors.append(ValidationError('credentials', 'Credentials must be a dictionary'))
            
        return errors

class AgentConfigValidator(ConfigValidator):
    """Validator for agent configurations."""
    
    def validate(self, config: Dict[str, Any]) -> List[ValidationError]:
        errors = []
        
        # Validate required fields
        required_fields = ['name', 'bio', 'traits', 'examples', 'loop_delay', 'config', 'tasks']
        for field in required_fields:
            if field not in config:
                errors.append(ValidationError(field, f'{field} is required'))
                
        # Validate tasks if present
        if 'tasks' in config:
            if not isinstance(config['tasks'], list):
                errors.append(ValidationError('tasks', 'Tasks must be a list'))
            else:
                for i, task in enumerate(config['tasks']):
                    if not isinstance(task, dict):
                        errors.append(ValidationError(f'tasks[{i}]', 'Task must be a dictionary'))
                    elif 'name' not in task:
                        errors.append(ValidationError(f'tasks[{i}]', 'Task name is required'))
                        
        return errors
