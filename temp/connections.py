from typing import Dict, List, Callable

class ToolExecutor:
    def __init__(self, tools: List[Dict]):
        self.tools = {tool["name"]: tool for tool in tools}

    def execute(self, tool_name: str, **kwargs):
        if tool_name not in self.tools:
            raise ValueError(f"Unknown tool: {tool_name}")
        tool = self.tools[tool_name]
        return tool["function"](**kwargs)

# OpenAI Connection
class OpenAIConnection:
    def __init__(self):
        self.actions = {
            "generate_text": {
                "name": "generate_text",
                "description": "Generate text using GPT-3 given a prompt",
                "parameters": {
                    "prompt": {
                        "type": "string",
                        "description": "The text prompt to generate from"
                    }
                },
                "function": self.generate_text
            },
            "generate_image": {
                "name": "generate_image",
                "description": "Generate an image using DALL-E given a prompt",
                "parameters": {
                    "prompt": {
                        "type": "string",
                        "description": "The image description to generate from"
                    }
                },
                "function": self.generate_image
            }
        }
        self.tool_executor = ToolExecutor([self._create_tool(action) for action in self.actions.values()])

    def _create_tool(self, action: Dict) -> Dict:
        return {
            "name": action["name"],
            "description": action["description"],
            "function": action["function"]
        }

    def generate_text(self, prompt: str) -> str:
        return "Generated text from GPT-3 model"

    def generate_image(self, prompt: str) -> str:
        return "Generated image from DALL-E model"

    def get_tool_description(self) -> Dict:
        return {
            "name": "openai",
            "description": "Connection to OpenAI's models for text and image generation.",
            "actions": self.actions
        }

    def get_tool_executor(self) -> ToolExecutor:
        return self.tool_executor

# Twitter Connection
class TwitterConnection:
    def __init__(self):
        self.actions = {
            "post_tweet": {
                "name": "post_tweet",
                "description": "Post a new tweet",
                "parameters": {
                    "text": {
                        "type": "string",
                        "description": "The text content of the tweet"
                    }
                },
                "function": self.post_tweet
            },
            "like_tweet": {
                "name": "like_tweet",
                "description": "Like an existing tweet",
                "parameters": {
                    "tweet_id": {
                        "type": "string",
                        "description": "The ID of the tweet to like"
                    }
                },
                "function": self.like_tweet
            }
        }
        self.tool_executor = ToolExecutor([self._create_tool(action) for action in self.actions.values()])

    def _create_tool(self, action: Dict) -> Dict:
        return {
            "name": action["name"],
            "description": action["description"],
            "function": action["function"]
        }

    def post_tweet(self, text: str) -> None:
        print(f"Posting tweet: {text}")

    def like_tweet(self, tweet_id: str) -> None:
        print(f"Liking tweet: {tweet_id}")

    def get_tool_description(self) -> Dict:
        return {
            "name": "twitter",
            "description": "Connection to Twitter for posting and interacting with tweets",
            "actions": self.actions
        }

    def get_tool_executor(self) -> ToolExecutor:
        return self.tool_executor

# Farcaster Connection
class FarcasterConnection:
    def __init__(self):
        self.actions = {
            "post_cast": {
                "name": "post_cast",
                "description": "Post a new cast",
                "parameters": {
                    "text": {
                        "type": "string",
                        "description": "The text content of the cast"
                    }
                },
                "function": self.post_cast
            }
        }
        self.tool_executor = ToolExecutor([self._create_tool(action) for action in self.actions.values()])

    def _create_tool(self, action: Dict) -> Dict:
        return {
            "name": action["name"],
            "description": action["description"],
            "function": action["function"]
        }

    def post_cast(self, text: str) -> None:
        print(f"Posting cast: {text}")

    def get_tool_description(self) -> Dict:
        return {
            "name": "farcaster",
            "description": "Connection to Farcaster for posting casts",
            "actions": self.actions
        }

    def get_tool_executor(self) -> ToolExecutor:
        return self.tool_executor

# Anthropic Connection
class AnthropicConnection:
    def __init__(self):
        self.actions = {
            "generate_text": {
                "name": "generate_text",
                "description": "Generate text using Claude given a prompt",
                "parameters": {
                    "prompt": {
                        "type": "string",
                        "description": "The text prompt to generate from"
                    }
                },
                "function": self.generate_text
            }
        }
        self.tool_executor = ToolExecutor([self._create_tool(action) for action in self.actions.values()])

    def _create_tool(self, action: Dict) -> Dict:
        return {
            "name": action["name"],
            "description": action["description"],
            "function": action["function"]
        }

    def generate_text(self, prompt: str) -> str:
        return "Generated text from Claude model"

    def get_tool_description(self) -> Dict:
        return {
            "name": "anthropic",
            "description": "Connection to Anthropic's Claude model for text generation",
            "actions": self.actions
        }

    def get_tool_executor(self) -> ToolExecutor:
        return self.tool_executor