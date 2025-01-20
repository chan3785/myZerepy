import json
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict
import os
from typing import get_args, get_origin

from src.utils.deep_dict import deep_get, deep_set

logger = logging.getLogger(__name__)


class BaseConfigException(Exception):
    """Base class for exceptions in this module."""

    def __init__(self, message: str) -> None:
        logger.debug(message)
        super().__init__(message)


class Config:
    pass


class BaseConfig(ABC):
    cfg: dict[str, Any] = {}

    def __init__(self, data: dict[str, Any]) -> None:
        self.validate_config(data)

    @property
    @abstractmethod
    def is_llm_provider(self) -> bool:
        pass

    @staticmethod
    @abstractmethod
    def required_config_fields() -> Dict[str, type[Any]]:
        """
        Returns a dictionary of required fields in the config

        Returns:
            Dict[str, type]: Dictionary of field names to their required types
        """
        pass

    @staticmethod
    @abstractmethod
    def required_env_vars() -> Dict[str, type[Any]]:
        """
        Returns a dictionary of required environment variables

        Returns:
            Dict[str, type]: Dictionary of environment variable names to their required types
        """
        pass

    @staticmethod
    @abstractmethod
    def required_fields() -> Dict[str, type[Any]]:
        """
        Returns a dictionary combining the required fields and environment variables

        Returns:
            Dict[str, type]: Combined dictionary of required fields
        """
        pass

    def validate_config(self, config: Dict[str, Any]) -> None:
        """
        Validate the config.

        Args:
            config (Dict[str, Any]): The configuration dictionary.

        Raises:
            BaseConfigException: If a required field is missing or has the wrong type.

        Returns:
            None
        """
        # Validate the config fields from the subclass-specific method
        for field, field_type in self.required_config_fields().items():
            if field not in config:
                raise BaseConfigException(f"Missing required field {field}")
            # pretty print config to logger
            field_value = config[field]

            # Handle parameterized types (e.g., List[str], Dict[str, int], etc.)
            origin = get_origin(
                field_type
            )  # This is the base type (like `str`, `int`, etc.)
            args = get_args(
                field_type
            )  # This will be the type parameters (e.g., `str` in List[str])

            if (
                origin is None
            ):  # This means the field_type is not parameterized (e.g., just `str`, `int`)
                expected_type = field_type
            else:
                expected_type = origin

            if not isinstance(field_value, expected_type):
                try:
                    # Try to convert the field value to the expected type
                    self.cfg = deep_set(self.cfg, [field], expected_type(field_value))
                except Exception as e:

                    raise BaseConfigException(
                        f"Field {field} must be of type {field_type}. Got {field_value}"
                    ) from e
            else:
                self.cfg = deep_set(self.cfg, [field], field_value)

        # Validate the environment variables from the subclass-specific method
        for env_var, env_var_type in self.required_env_vars().items():
            if env_var not in os.environ:
                raise BaseConfigException(
                    f"Missing required environment variable {env_var}"
                )

            retrieved_value = os.environ[env_var]

            # Handle parameterized types for environment variables
            origin = get_origin(env_var_type)  # Get the base type
            args = get_args(env_var_type)  # Get the type arguments (if any)

            if (
                origin is None
            ):  # This means the env_var_type is not parameterized (e.g., just `str`, `int`)
                expected_type = env_var_type
            else:
                expected_type = origin

            if not isinstance(retrieved_value, expected_type):
                try:
                    # Try to convert the environment variable value to the expected type
                    self.cfg = deep_set(
                        self.cfg, [env_var], expected_type(retrieved_value)
                    )
                except Exception as e:
                    raise BaseConfigException(
                        f"Environment variable {env_var} must be of type {env_var_type}. Got {retrieved_value}"
                    ) from e
            else:
                self.cfg = deep_set(self.cfg, [env_var], retrieved_value)

    def get(self, key: str) -> Any:
        if key not in self.required_fields():
            raise BaseConfigException(f"Key {key} not found in config")
        return deep_get(self.cfg, [key])

    def config_to_dict(self) -> Dict[str, Any]:
        # pretty print self to logger without calling getattr
        # logger.debug(json.dumps(self.__dict__, indent=4))
        return {k: deep_get(self.cfg, [k]) for k in self.required_fields()}

    def save(self) -> None:
        with open(self.path(), "w") as f:
            json.dump(self.config_to_dict(), f, indent=4)

    @staticmethod
    def path() -> Path:
        agent_dir = os.getenv("AGENT_DIR")
        if agent_dir:
            return Path(agent_dir)
        else:
            return Path("agents")
