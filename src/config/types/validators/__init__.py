from pydantic import ValidationInfo, ValidatorFunctionWrapHandler


def api_key_validator(
    value: str, handler: ValidatorFunctionWrapHandler, _info: ValidationInfo
) -> str:
    if len(value) < 10:
        raise ValueError("Key too short")
    return value
