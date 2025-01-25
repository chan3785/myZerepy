from typing import Annotated, Any, TypeAliasType
from pydantic import (
    BaseModel,
    Field,
    PositiveInt,
    ValidationInfo,
    ValidatorFunctionWrapHandler,
    WrapValidator,
)
from pydantic_settings import BaseSettings
import logging
from src.config.types import ApiKey

logger = logging.getLogger(__name__)


class TwitterConnectionError(Exception):
    """Base exception for Twitter connection errors"""

    pass


class TwitterConfigurationError(TwitterConnectionError):
    """Raised when there are configuration/credential issues"""

    pass


class TwitterAPIError(TwitterConnectionError):
    """Raised when Twitter API requests fail"""

    pass


class TwitterSettings(BaseSettings):
    consumer_key: ApiKey = Field(validation_alias="TWITTER_CONSUMER_KEY")
    consumer_secret: ApiKey = Field(validation_alias="TWITTER_CONSUMER_SECRET")
    access_token: ApiKey = Field(validation_alias="TWITTER_ACCESS_TOKEN")
    access_token_secret: ApiKey = Field(validation_alias="TWITTER_ACCESS_TOKEN_SECRET")
    user_id: ApiKey = Field(validation_alias="TWITTER_USER_ID")

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)


class TwitterConfig(BaseModel):
    timeline_read_count: PositiveInt = 10
    own_tweet_replies_count: PositiveInt = 2
    tweet_interval: PositiveInt = 5400
    twitter_settings: TwitterSettings

    def __init__(self, **data: Any) -> None:
        # if the connection is not configured, return none
        try:
            data["twitter_settings"] = TwitterSettings()
            super().__init__(**data)
        except Exception as e:
            return
