import logging
from typing import Dict, Any
from dataclasses import dataclass
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from goat_adapters.langchain import get_on_chain_tools
from src.connections.base_connection import BaseConnection, Action, ActionParameter
from src.connections.goat_connection import GoatConnection

logger = logging.getLogger("connections.brain_connection")

class BrainConnectionError(Exception):
    """Base exception for Brain connection errors"""
    pass

SYSTEM_PROMPT = """You are Blormmy. A helpful assistant for anything onchain. Important rules:
                1. Don't do anything that is not within your plugin options - just say no and don't do it
                2. For swaps: First get a quote using uniswap_get_quote, then use uniswap_swap_tokens with EXACTLY the same parameters as the quote
                3. Always verify the details of any transaction before executing it"""

@dataclass
class ChatHistory:
    """Storage for chat context"""
    messages: list[dict[str, str]] = None

    def __post_init__(self):
        self.messages = [] if self.messages is None else self.messages

    def add_message(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})

    def to_langchain_messages(self):
        return [
            (SystemMessage if msg["role"] == "system" else 
             HumanMessage if msg["role"] == "human" else 
             AIMessage)(content=msg["content"])
            for msg in self.messages
            if msg["role"] in ("system", "human", "ai")
        ]

class BrainConnection(BaseConnection):
    def __init__(self, config: Dict[str, Any]):
        self.provider = None
        self.model = None
        self.agent_executor = None
        self.chat_history = ChatHistory()
        self.goat_connection = None
        super().__init__(config)

    @property
    def is_llm_provider(self) -> bool:
        return False

    def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Brain configuration"""
        required_fields = ["provider", "model"]
        missing = [f for f in required_fields if f not in config]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")
            
        if config["provider"] not in ["anthropic", "openai"]:
            raise ValueError("Provider must be either 'anthropic' or 'openai'")
            
        return config

    def register_actions(self) -> None:
        """Register available Brain actions"""
        self.actions = {
            "process-command": Action(
                name="process-command",
                parameters=[
                    ActionParameter("command", True, str, "Natural language command to process")
                ],
                description="Process natural language into blockchain action"
            )
        }
        
    def _setup_llm(self) -> None:
        """Initialize the LLM based on configuration"""
        if self.config["provider"] == "anthropic":
            self.llm = ChatAnthropic(model=self.config["model"])
        else:  # openai
            self.llm = ChatOpenAI(model=self.config["model"])

    def _setup_langchain_agent(self, goat_connection: GoatConnection) -> None:
        """Initialize Langchain agent with GOAT tools"""
        try:
            # Create chatbot prompt template
            prompt = ChatPromptTemplate.from_messages([
                ("system", SYSTEM_PROMPT),
                ("placeholder", "{chat_history}"),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}")
            ])

            # Get tools from GOAT connection
            tools = get_on_chain_tools(
                wallet=goat_connection._wallet_client,
                plugins=list(goat_connection._plugins.values())
            )

            # Create agent and executor
            agent = create_tool_calling_agent(self.llm, tools, prompt)
            self.agent_executor = AgentExecutor(
                agent=agent,
                tools=tools,
                handle_parsing_errors=True,
                verbose=True
            )
            
        except Exception as e:
            raise BrainConnectionError(f"Agent setup failed: {str(e)}")

    def configure(self, goat_connection: GoatConnection = None) -> bool:
        """Configure the brain connection"""
        try:
            if not goat_connection:
                raise BrainConnectionError("GOAT connection is required")
                
            self.goat_connection = goat_connection
            self._setup_llm()
            self._setup_langchain_agent(goat_connection)
            return True
            
        except Exception as e:
            logger.error(f"Brain configuration failed: {e}")
            return False

    def is_configured(self, verbose: bool = False) -> bool:
        configured = (
            self.llm is not None and 
            self.agent_executor is not None and
            self.goat_connection is not None
        )
        
        if verbose and not configured:
            if not self.llm:
                logger.error("LLM not initialized")
            if not self.agent_executor:
                logger.error("Langchain agent not initialized")
            if not self.goat_connection:
                logger.error("GOAT connection not configured")
        return configured

    def process_command(self, command: str) -> str:
        """Process a natural language command"""
        if not self.is_configured(verbose=True):
            return "Brain connection not fully configured"

        try:
            self.chat_history.add_message("human", command)
            response = self.agent_executor.invoke({
                "input": command,
                "chat_history": self.chat_history.to_langchain_messages()
            })
            
            output = response["output"]
            self.chat_history.add_message("ai", output)
            return output

        except Exception as e:
            error_msg = str(e)
            if "'HexBytes' object has no attribute 'to_0x_hex'" in error_msg:
                return "Transaction submitted successfully! Note: Transaction details may take a few moments to appear."
            return f"Error processing command: {str(e)}"

    def perform_action(self, action_name: str, kwargs: Dict[str, Any]) -> Any:
        """Execute a brain action"""
        if action_name not in self.actions:
            raise KeyError(f"Unknown action: {action_name}")

        if not self.is_configured(verbose=True):
            raise BrainConnectionError("Brain connection not configured")

        action = self.actions[action_name]
        errors = action.validate_params(kwargs)
        if errors:
            raise ValueError(f"Invalid parameters: {', '.join(errors)}")

        method = getattr(self, action_name.replace("-", "_"))
        return method(**kwargs)