from typing import Any
import logging

logger = logging.getLogger(__name__)


def deep_set(data: dict[str, Any], keys: list[str], value: Any) -> dict[str, Any]:
    if keys[0] not in data:
        # if its not in the data, add it
        data[keys[0]] = {}
    if len(keys) == 1:
        data[keys[0]] = value
        return data
    return deep_set(data[keys[0]], keys[1:], value=value)


def deep_get(data: dict[str, Any], keys: list[str]) -> Any:
    if keys[0] not in data:
        raise KeyError(f"Key {keys[0]} not found in data")
    if len(keys) == 1:
        return data[keys[0]]
    return deep_get(data[keys[0]], keys[1:])
