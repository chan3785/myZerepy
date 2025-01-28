from datetime import datetime
from typing import Annotated, Any, Optional, Tuple, TypeAliasType
from ...base_config import BaseConfig, BaseSettings
from pydantic import (
    PositiveFloat,
    TypeAdapter,
    ValidationInfo,
    ValidatorFunctionWrapHandler,
    WrapValidator,
)


def string_time_validator(
    value: str,
    handler: ValidatorFunctionWrapHandler,
    _info: ValidationInfo,
) -> datetime:
    format_string = "%H:%M:%S"
    if not isinstance(value, str):
        raise InvalidTimeIntervalError(f"Time {value} is not a string")
    try:
        validated_value = datetime.strptime(value, format_string)
    except ValueError:
        raise InvalidTimeIntervalError(
            f"Time {value} does not follow the format of {format_string}"
        )
    return validated_value


def time_interval_validator(
    value: dict[str, float],
    handler: ValidatorFunctionWrapHandler,
    _info: ValidationInfo,
) -> dict[Tuple[datetime, datetime], PositiveFloat]:
    format_string = "%H:%M:%S"
    validated_dict = {}
    for k, v in value.items():
        validated_value = TypeAdapter(PositiveFloat).validate_python(v)
        interval_split = k.split("-")
        if len(interval_split) != 2:
            raise InvalidTimeIntervalError(
                f'Time interval "{k}" does not follow the format of {format_string}-{format_string}'
            )
        start_time = datetime.strptime(interval_split[0], format_string)
        end_time = datetime.strptime(interval_split[1], format_string)
        validated_dict[(start_time, end_time)] = validated_value
    # check if there are overlapping time intervals
    time_intervals = list(validated_dict.keys())
    for i, interval in enumerate(time_intervals):
        for other_interval in time_intervals[i + 1 :]:
            if interval[0] < other_interval[1] and other_interval[0] < interval[1]:
                interval_string = f"{interval[0].strftime(format_string)}-{interval[1].strftime(format_string)}"
                other_interval_string = f"{other_interval[0].strftime(format_string)}-{other_interval[1].strftime(format_string)}"
                raise InvalidTimeIntervalError(
                    f"Time intervals {str(interval_string)} and {other_interval_string} overlap"
                )
    return validated_dict


TimeBasedMultiplier = TypeAliasType(
    "TimeBasedMultiplier",
    Annotated[
        dict[Tuple[datetime, datetime], PositiveFloat],
        WrapValidator(time_interval_validator),
    ],
)

StringTime = TypeAliasType(
    "StringTime", Annotated[datetime, WrapValidator(string_time_validator)]
)


class InvalidTimeIntervalError(Exception):
    pass


class Task(BaseConfig):
    weight: PositiveFloat
    min_interval: StringTime
    max_interval: StringTime
    time_based_multipliers: Optional[TimeBasedMultiplier] = None
    last_performed: Optional[datetime] = None

    def get_weight(self) -> PositiveFloat:
        if self.time_based_multipliers is not None:
            current_time = datetime.now().time()
            for interval, weight in self.time_based_multipliers.items():
                if interval[0].time() <= current_time <= interval[1].time():
                    return weight * self.weight
        return self.weight

    def should_perform_task(self) -> None:
        if self.last_performed is None:
            # set last_performed to current time plus min_interval
            self.last_performed = datetime.now()
