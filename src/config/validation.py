"""Configuration validation for ZerePy."""
from typing import Any, Dict, List, Optional, Type, Union
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

class SchemaValidator(ConfigValidator):
    """Schema-based configuration validator."""
    
    def __init__(self, schema: Dict[str, Dict[str, Any]]):
        """
        Initialize validator.
        
        Args:
            schema: Validation schema
        """
        self.schema = schema
        
    def validate(self, config: Dict[str, Any]) -> List[ValidationError]:
        """Validate configuration against schema."""
        errors = []
        
        for field, rules in self.schema.items():
            # Check required fields
            if rules.get('required', False) and field not in config:
                errors.append(ValidationError(field, f'{field} is required'))
                continue
                
            if field not in config:
                continue
                
            value = config[field]
            
            # Check type
            expected_type = rules.get('type')
            if expected_type and not isinstance(value, expected_type):
                errors.append(ValidationError(
                    field, 
                    f'{field} must be of type {expected_type.__name__}'
                ))
                
            # Check enum values
            enum_values = rules.get('enum')
            if enum_values and value not in enum_values:
                errors.append(ValidationError(
                    field,
                    f'{field} must be one of {enum_values}'
                ))
                
            # Check nested objects
            nested_schema = rules.get('schema')
            if nested_schema and isinstance(value, dict):
                nested_validator = SchemaValidator(nested_schema)
                errors.extend(nested_validator.validate(value))
                
            # Check array items
            items_schema = rules.get('items')
            if items_schema and isinstance(value, list):
                item_validator = SchemaValidator(items_schema)
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        errors.extend(item_validator.validate(item))
                    
        return errors

class ConnectionConfigValidator(ConfigValidator):
    """Validator for connection configurations."""
    
    def __init__(self):
        """Initialize validator with schema."""
        self._schema = SchemaValidator({
            'name': {'required': True, 'type': str},
            'type': {'required': True, 'type': str},
            'credentials': {
                'type': dict,
                'schema': {
                    'api_key': {'type': str},
                    'api_secret': {'type': str},
                    'access_token': {'type': str}
                }
            },
            'options': {'type': dict}
        })
        
    def validate(self, config: Dict[str, Any]) -> List[ValidationError]:
        return self._schema.validate(config)

class PluginConfigValidator(ConfigValidator):
    """Validator for plugin configurations."""
    
    def __init__(self):
        """Initialize validator with schema."""
        self._schema = SchemaValidator({
            'name': {'required': True, 'type': str},
            'version': {'required': True, 'type': str},
            'type': {'required': True, 'type': str, 'enum': ['connection', 'action']},
            'config': {
                'type': dict,
                'schema': {
                    'enabled': {'type': bool},
                    'options': {'type': dict}
                }
            }
        })
        
    def validate(self, config: Dict[str, Any]) -> List[ValidationError]:
        return self._schema.validate(config)

class AgentConfigValidator(ConfigValidator):
    """Validator for agent configurations."""
    
    def __init__(self):
        """Initialize validator with schema."""
        self._schema = SchemaValidator({
            'name': {'required': True, 'type': str},
            'bio': {'required': True, 'type': str},
            'traits': {'required': True, 'type': list},
            'examples': {'required': True, 'type': list},
            'loop_delay': {'required': True, 'type': (int, float)},
            'config': {'required': True, 'type': dict},
            'tasks': {
                'required': True,
                'type': list,
                'items': {
                    'name': {'required': True, 'type': str},
                    'description': {'type': str},
                    'enabled': {'type': bool}
                }
            }
        })
        
    def validate(self, config: Dict[str, Any]) -> List[ValidationError]:
        return self._schema.validate(config)
