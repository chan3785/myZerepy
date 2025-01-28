from typing import Any


def deep_pretty_print(
    obj: Any,
    res_str: str = "",
    indent: int = 2,
    blacklisted_fields: list[str] | None = None,
    partial_match: bool | None = None,
) -> str:
    # example format for {"ExampleAgent": {"name": "example", "age": 20}}
    # ExampleAgent:
    #      - name: example
    #      - age: 20
    if blacklisted_fields is None:
        blacklisted_fields = []
    if partial_match is None:
        partial_match = False
    if isinstance(obj, dict) and len(obj) > 0:
        for key, value in obj.items():
            if partial_match:
                if any(field in key for field in blacklisted_fields):
                    continue
            else:
                if key in blacklisted_fields:
                    continue
            res_str += f"\n{' ' * indent}- {key}:"
            res_str = deep_pretty_print(
                value, res_str, indent + indent, blacklisted_fields, partial_match
            )
    elif isinstance(obj, list):
        for value in obj:
            res_str += f"\n{' ' * indent}- {value}"
            res_str = deep_pretty_print(
                value, res_str, indent + indent, blacklisted_fields, partial_match
            )
    else:
        res_str += "  " + f"{obj}"
    return res_str


def deep_remove_fields(
    obj: dict[str, Any], fields: list[str], partial_match: bool | None = None
) -> dict[str, Any]:
    for key, value in obj.items():
        if partial_match:
            if any(field in key for field in fields):
                obj.pop(key)
        else:
            if key in fields:
                obj.pop(key)
        if isinstance(value, dict):
            if len(value) == 0:
                continue
            return deep_remove_fields(value, fields, partial_match)
    return obj
