from typing import Any
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from src.config.types import BlockchainNetwork
from src.config.types import ApiKey


class AlloraSettings(BaseSettings):
    api_key: ApiKey = Field(validation_alias="ALLORA_API_KEY")

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)


class AlloraConfig(BaseModel):
    chain: BlockchainNetwork
    allora_settings: AlloraSettings

    def __init__(self, **data: Any) -> None:
        # if the connection is not configured, return none
        try:
            data["allora_settings"] = AlloraSettings()
            super().__init__(**data)

        except Exception as e:
            return
