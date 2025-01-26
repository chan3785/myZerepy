from typing import Annotated, Any, Tuple, TypeAliasType
from pydantic import (
    BaseModel,
    Field,
    PositiveInt,
    ValidationInfo,
    ValidatorFunctionWrapHandler,
    WrapValidator,
)
from pydantic_core import ErrorDetails
from requests_oauthlib import OAuth1Session

from pydantic_settings import BaseSettings
import logging
from src.config.types import ApiKey
from pydantic import ValidationError


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
    user_id: str = Field(validation_alias="TWITTER_USER_ID")

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)


class TwitterConfig(BaseModel):
    timeline_read_count: PositiveInt = 10
    own_tweet_replies_count: PositiveInt = 2
    tweet_interval: PositiveInt = 5400
    twitter_settings: TwitterSettings
    _oauth_session: OAuth1Session = None
    logger: logging.Logger

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data: Any) -> None:
        try:
            data["logger"] = logging.getLogger(f"{self.__class__.__name__}")
            data["twitter_settings"] = TwitterSettings()
            super().__init__(**data)
        except Exception as e:
            if isinstance(e, ValidationError):
                errors: list[ErrorDetails] = e.errors()
                for error in errors:
                    print(
                        f'{error.get("msg")}. Invalid Field(s): {".".join(map(str, error.get("loc", [])))}'
                    )
            return

    def _get_oauth(self) -> OAuth1Session:
        """Get or create OAuth session using stored credentials"""
        if self._oauth_session is None:
            self.logger.debug("Creating new OAuth session")
            try:
                self._oauth_session = OAuth1Session(
                    self.twitter_settings.consumer_key,
                    client_secret=self.twitter_settings.consumer_secret,
                    resource_owner_key=self.twitter_settings.access_token,
                    resource_owner_secret=self.twitter_settings.access_token_secret,
                )
                self.logger.debug("OAuth session created successfully")
            except Exception as e:
                self.logger.error(f"Failed to create OAuth session: {str(e)}")
                raise

        return self._oauth_session

    def _make_request(
        self, method: str, endpoint: str, **kwargs: Any
    ) -> dict[str, Any]:
        """
        Make a request to the Twitter API with error handling

        Args:
            method: HTTP method ('get', 'post', etc.)
            endpoint: API endpoint path
            **kwargs: Additional request parameters

        Returns:
            Dict containing the API response
        """
        self.logger.debug(f"Making {method.upper()} request to {endpoint}")
        try:
            oauth = self._get_oauth()
            full_url = f"https://api.twitter.com/2/{endpoint.lstrip('/')}"

            response = getattr(oauth, method.lower())(full_url, **kwargs)

            if response.status_code not in [200, 201]:
                self.logger.error(
                    f"Request failed: {response.status_code} - {response.text}"
                )
                raise TwitterAPIError(
                    f"Request failed with status {response.status_code}: {response.text}"
                )

            self.logger.debug(f"Request successful: {response.status_code}")
            json_response = response.json()
            if not isinstance(json_response, dict):
                raise TwitterAPIError("API response is not a dictionary")
            return json_response

        except Exception as e:
            raise TwitterAPIError(f"API request failed: {str(e)}")

    def _get_authenticated_user_info(self) -> Tuple[str, str]:
        """Get the authenticated user's ID and username using the users/me endpoint"""
        self.logger.debug("Getting authenticated user info")
        try:
            response = self._make_request(
                "get", "users/me", params={"user.fields": "id,username"}
            )
            user_id = response["data"]["id"]
            username = response["data"]["username"]
            self.logger.debug(f"Retrieved user ID: {user_id}, username: {username}")

            return user_id, username
        except Exception as e:
            self.logger.error(f"Failed to get authenticated user info: {str(e)}")
            raise TwitterConfigurationError(
                "Could not retrieve user information"
            ) from e

    def _validate_tweet_text(self, text: str, context: str = "Tweet") -> None:
        """Validate tweet text meets Twitter requirements"""
        if not text:
            error_msg = f"{context} text cannot be empty"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        if len(text) > 280:
            error_msg = f"{context} exceeds 280 character limit"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        self.logger.debug(f"Tweet text validation passed for {context.lower()}")
