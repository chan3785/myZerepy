import os
import logging
from typing import Dict, Any, List, Tuple, Optional
from requests_oauthlib import OAuth1Session
from dotenv import set_key, load_dotenv
from src.connections.base_connection import BaseConnection, Action, ActionParameter
from src.helpers import print_h_bar

logger = logging.getLogger("connections.twitter_connection")

class TwitterConnectionError(Exception):
    """Base exception for Twitter connection errors"""
    pass

class TwitterConfigurationError(TwitterConnectionError):
    """Raised when there are configuration/credential issues"""
    pass

class TwitterAPIError(TwitterConnectionError):
    """Raised when Twitter API requests fail"""
    pass

class TwitterConnection(BaseConnection):
    def __init__(self, config: Dict[str, Any]):
        # Initialize caches
        self._oauth_session = None
        self._credentials_cache = None
        self._user_info_cache = None
        # Load credentials immediately to ensure state is correct
        try:
            self._credentials_cache = self._load_credentials()
            self._create_oauth_session()
        except Exception:
            pass
        super().__init__(config)

    @property
    def is_llm_provider(self) -> bool:
        return False

    def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Twitter configuration from JSON"""
        required_fields = ["timeline_read_count", "tweet_interval"]
        missing_fields = [field for field in required_fields if field not in config]
        
        if missing_fields:
            raise ValueError(f"Missing required configuration fields: {', '.join(missing_fields)}")
            
        if not isinstance(config["timeline_read_count"], int) or config["timeline_read_count"] <= 0:
            raise ValueError("timeline_read_count must be a positive integer")

        if not isinstance(config["tweet_interval"], int) or config["tweet_interval"] <= 0:
            raise ValueError("tweet_interval must be a positive integer")
            
        return config

    def register_actions(self) -> None:
        """Register available Twitter actions"""
        self.actions = {
            "get-latest-tweets": Action(
                name="get-latest-tweets",
                parameters=[
                    ActionParameter("username", True, str, "Twitter username to get tweets from"),
                    ActionParameter("count", False, int, "Number of tweets to retrieve")
                ],
                description="Get the latest tweets from a user"
            ),
            "post-tweet": Action(
                name="post-tweet",
                parameters=[
                    ActionParameter("message", True, str, "Text content of the tweet")
                ],
                description="Post a new tweet"
            ),
            "read-timeline": Action(
                name="read-timeline",
                parameters=[
                    ActionParameter("count", False, int, "Number of tweets to read from timeline")
                ],
                description="Read tweets from user's timeline"
            ),
            "like-tweet": Action(
                name="like-tweet",
                parameters=[
                    ActionParameter("tweet_id", True, str, "ID of the tweet to like")
                ],
                description="Like a specific tweet"
            ),
            "reply-to-tweet": Action(
                name="reply-to-tweet",
                parameters=[
                    ActionParameter("tweet_id", True, str, "ID of the tweet to reply to"),
                    ActionParameter("message", True, str, "Reply message content")
                ],
                description="Reply to an existing tweet"
            ),
            "get-tweet-replies": Action(
                name="get-tweet-replies",
                parameters=[
                    ActionParameter("tweet_id", True, str, "ID of the tweet to query for replies")
                ],
                description="Fetch tweet replies"
            )
        }

    def _get_credentials(self) -> Dict[str, str]:
        """Get Twitter credentials from environment with caching"""
        if self._credentials_cache is not None:
            return self._credentials_cache

        load_dotenv()
        required_vars = {
            'TWITTER_CONSUMER_KEY': 'consumer key',
            'TWITTER_CONSUMER_SECRET': 'consumer secret',
            'TWITTER_ACCESS_TOKEN': 'access token',
            'TWITTER_ACCESS_TOKEN_SECRET': 'access token secret',
            'TWITTER_USER_ID': 'user ID'
        }

        credentials = {}
        missing = []

        for env_var, description in required_vars.items():
            value = os.getenv(env_var)
            if not value:
                missing.append(description)
            credentials[env_var] = value

        if missing:
            error_msg = f"Missing Twitter credentials: {', '.join(missing)}"
            raise TwitterConfigurationError(error_msg)

        self._credentials_cache = credentials
        return credentials

    def _get_oauth(self) -> OAuth1Session:
        """Get or create OAuth session using stored credentials"""
        if self._oauth_session is None:
            try:
                credentials = self._get_credentials()
                self._oauth_session = OAuth1Session(
                    credentials['TWITTER_CONSUMER_KEY'],
                    client_secret=credentials['TWITTER_CONSUMER_SECRET'],
                    resource_owner_key=credentials['TWITTER_ACCESS_TOKEN'],
                    resource_owner_secret=credentials['TWITTER_ACCESS_TOKEN_SECRET']
                )
            except Exception as e:
                logger.error(f"Failed to create OAuth session: {str(e)}")
                raise

        return self._oauth_session

    def _make_request(self, method: str, endpoint: str, **kwargs) -> dict:
        """Make a request to the Twitter API with error handling"""
        try:
            oauth = self._get_oauth()
            full_url = f"https://api.twitter.com/2/{endpoint.lstrip('/')}"
            
            response = getattr(oauth, method.lower())(full_url, **kwargs)

            if response.status_code not in [200, 201]:
                logger.error(f"Request failed: {response.status_code} - {response.text}")
                raise TwitterAPIError(f"Request failed with status {response.status_code}: {response.text}")

            return response.json()

        except Exception as e:
            raise TwitterAPIError(f"API request failed: {str(e)}")

    def configure(self) -> bool:
        """Sets up Twitter API authentication"""
        logger.info("\n🐦 TWITTER AUTHENTICATION SETUP")

        if self.is_configured():
            logger.info("\nTwitter API is already configured.")
            response = input("Do you want to reconfigure? (y/n): ")
            if response.lower() != 'y':
                return True

        setup_instructions = [
            "\n📝 To get your Twitter API credentials:",
            "1. Go to https://developer.twitter.com/en/portal/dashboard",
            "2. Create a new project and app if you haven't already",
            "3. In your app settings, enable OAuth 1.0a with read and write permissions",
            "4. Get your API Key (consumer key) and API Key Secret (consumer secret)"
        ]
        logger.info("\n".join(setup_instructions))
        print_h_bar()

        try:
            # Get account details
            logger.info("\nPlease enter your Twitter API credentials:")
            credentials = {
                'consumer_key': input("Enter your API Key (consumer key): "),
                'consumer_secret': input("Enter your API Key Secret (consumer secret): ")
            }

            logger.info("\nStarting OAuth authentication process...")

            # Initialize OAuth flow
            request_token_url = "https://api.twitter.com/oauth/request_token?oauth_callback=oob&x_auth_access_type=write"
            oauth = OAuth1Session(
                credentials['consumer_key'],
                client_secret=credentials['consumer_secret']
            )

            try:
                fetch_response = oauth.fetch_request_token(request_token_url)
            except ValueError as e:
                logger.error("Failed to fetch request token")
                raise TwitterConfigurationError("Invalid consumer key or secret") from e

            # Get authorization
            base_authorization_url = "https://api.twitter.com/oauth/authorize"
            authorization_url = oauth.authorization_url(base_authorization_url)
            logger.info("\n1. Please visit this URL to authorize the application:")
            logger.info(authorization_url)
            logger.info("\n2. After authorizing, Twitter will give you a PIN code.")
            
            verifier = input("\n3. Please enter the PIN code here: ")

            # Get access token
            access_token_url = "https://api.twitter.com/oauth/access_token"
            oauth = OAuth1Session(
                credentials['consumer_key'],
                client_secret=credentials['consumer_secret'],
                resource_owner_key=fetch_response.get('oauth_token'),
                resource_owner_secret=fetch_response.get('oauth_token_secret'),
                verifier=verifier
            )

            oauth_tokens = oauth.fetch_access_token(access_token_url)

            # Create temp session to get user info
            temp_oauth = OAuth1Session(
                credentials['consumer_key'],
                client_secret=credentials['consumer_secret'],
                resource_owner_key=oauth_tokens.get('oauth_token'),
                resource_owner_secret=oauth_tokens.get('oauth_token_secret')
            )

            # Get user info using the temp session
            self._oauth_session = temp_oauth
            response = self._make_request(
                'get',
                'users/me',
                params={'user.fields': 'id,username'}
            )
            user_data = response.get('data', {})
            user_id = user_data.get('id')
            username = user_data.get('username')

            if not user_id or not username:
                raise TwitterConfigurationError("Failed to get user information")

            # Save to .env
            if not os.path.exists('.env'):
                with open('.env', 'w') as f:
                    f.write('')

            env_vars = {
                'TWITTER_USER_ID': user_id,
                'TWITTER_USERNAME': username,
                'TWITTER_CONSUMER_KEY': credentials['consumer_key'],
                'TWITTER_CONSUMER_SECRET': credentials['consumer_secret'],
                'TWITTER_ACCESS_TOKEN': oauth_tokens.get('oauth_token'),
                'TWITTER_ACCESS_TOKEN_SECRET': oauth_tokens.get('oauth_token_secret')
            }

            for key, value in env_vars.items():
                set_key('.env', key, value)

            # Clear any cached data
            self._credentials_cache = None
            self._oauth_session = None
            self._user_info_cache = None

            logger.info("\n✅ Twitter authentication successfully set up!")
            logger.info("Your API keys and user information have been stored in the .env file.")
            return True

        except Exception as e:
            error_msg = f"Setup failed: {str(e)}"
            logger.error(error_msg)
            raise TwitterConfigurationError(error_msg)

    def is_configured(self, verbose: bool = False) -> bool:
        """Check if Twitter credentials are configured"""
        try:
            # Just check if credentials exist, don't make API call
            self._get_credentials()
            return True
        except Exception as e:
            if verbose:
                logger.error(f"Configuration check failed: {e}")
            return False

    def _validate_tweet_text(self, text: str, context: str = "Tweet") -> None:
        """Validate tweet text meets Twitter requirements"""
        if not text:
            raise ValueError(f"{context} text cannot be empty")
        if len(text) > 280:
            raise ValueError(f"{context} exceeds 280 character limit")

    def read_timeline(self, count: int = None) -> list:
        """Read tweets from user's timeline"""
        if count is None:
            count = self.config["timeline_read_count"]

        credentials = self._get_credentials()
        params = {
            "tweet.fields": "created_at,author_id,attachments",
            "expansions": "author_id",
            "user.fields": "name,username",
            "max_results": count
        }

        response = self._make_request(
            'get',
            f"users/{credentials['TWITTER_USER_ID']}/timelines/reverse_chronological",
            params=params
        )

        tweets = response.get("data", [])
        user_info = response.get("includes", {}).get("users", [])
        
        # Create user lookup for efficient joining
        user_dict = {
            user['id']: {
                'name': user['name'],
                'username': user['username']
            }
            for user in user_info
        }

        # Attach user info to tweets
        for tweet in tweets:
            author_id = tweet['author_id']
            author_info = user_dict.get(author_id, {
                'name': "Unknown",
                'username': "Unknown"
            })
            tweet.update({
                'author_name': author_info['name'],
                'author_username': author_info['username']
            })

        return tweets

    def post_tweet(self, message: str) -> dict:
        """Post a new tweet"""
        self._validate_tweet_text(message)
        return self._make_request('post', 'tweets', json={'text': message})

    def reply_to_tweet(self, tweet_id: str, message: str) -> dict:
        """Reply to an existing tweet"""
        self._validate_tweet_text(message, "Reply")
        return self._make_request(
            'post',
            'tweets',
            json={
                'text': message,
                'reply': {
                    'in_reply_to_tweet_id': tweet_id
                }
            }
        )

    def like_tweet(self, tweet_id: str) -> dict:
        """Like a tweet"""
        credentials = self._get_credentials()
        return self._make_request(
            'post',
            f"users/{credentials['TWITTER_USER_ID']}/likes",
            json={'tweet_id': tweet_id}
        )
    
    def get_tweet_replies(self, tweet_id: str, count: int = 10) -> List[dict]:
        """Fetch replies to a specific tweet"""
        params = {
            "query": f"conversation_id:{tweet_id} is:reply",
            "tweet.fields": "author_id,created_at,text",
            "max_results": min(count, 100)
        }
        
        response = self._make_request('get', 'tweets/search/recent', params=params)
        return response.get("data", [])

    def get_latest_tweets(self, username: str, count: int = 10) -> list:
        """Get latest tweets for a user"""
        params = {
            "tweet.fields": "created_at,text",
            "max_results": min(count, 100),
            "query": f"from:{username} -is:retweet -is:reply"
        }

        response = self._make_request('get', 'tweets/search/recent', params=params)
        return response.get("data", [])

    def perform_action(self, action_name: str, kwargs) -> Any:
        """Execute a Twitter action with validation"""
        if action_name not in self.actions:
            raise KeyError(f"Unknown action: {action_name}")

        action = self.actions[action_name]
        errors = action.validate_params(kwargs)
        if errors:
            raise ValueError(f"Invalid parameters: {', '.join(errors)}")

        # Add config parameters if not provided
        if action_name == "read-timeline" and "count" not in kwargs:
            kwargs["count"] = self.config["timeline_read_count"]

        # Call the appropriate method based on action name
        method_name = action_name.replace('-', '_')
        method = getattr(self, method_name)
        return method(**kwargs)