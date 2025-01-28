from typing import Any


def deep_pretty_print(
    obj: dict[str, Any],
    res_str: str = "",
    indent: int = 2,
    blacklisted_fields: list[str] | None = None,
    partial_match: bool | None = None,
) -> str:
    for key, value in obj.items():
        if blacklisted_fields is not None:
            if partial_match:
                if any(field in key for field in blacklisted_fields):
                    continue
            if key in blacklisted_fields:
                continue
        if isinstance(value, dict):
            if len(value) == 0:
                continue
            res_str += f"{' '*indent}{key}:\n"
            return deep_pretty_print(
                value,
                res_str=res_str,
                indent=indent + indent,
                blacklisted_fields=blacklisted_fields,
                partial_match=partial_match,
            )
        else:
            res_str += f"{' '*indent} - {key}: {value}\n"
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
