import logging
from typing import Dict, Any, List
from dataclasses import dataclass
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from goat_adapters.langchain import get_on_chain_tools
from goat_wallets.evm import send_eth
from goat_plugins.coingecko import coingecko, CoinGeckoPluginOptions
from goat_plugins.erc20 import erc20, ERC20PluginOptions
from goat_plugins.erc20.token import PEPE, USDC
from src.connections.base_connection import BaseConnection, Action, ActionParameter
from src.connections.goat_connection import GoatConnection

logger = logging.getLogger("connections.brain_connection")

class BrainConnectionError(Exception):
    """Base exception for Brain connection errors"""
    pass

class BrainConnection(BaseConnection):
    def __init__(self, config: Dict[str, Any]):
        self.llm_provider = None
        self.model = None
        self.agent_executor = None
        self.chat_history = ChatHistory()
        
        logger.info("Initializing GOAT connection...")
        self.goat_connection = GoatConnection(config)
        super().__init__(config)
        
        # Load essential configuration
        self.model = self.config.get("model")
        self.llm_provider = self.config.get("llm_provider")
        if not self.model or not self.llm_provider:
            raise ValueError("Configuration must include 'model' and 'llm_provider'")

    @property
    def is_llm_provider(self) -> bool:
        return False

    def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        required_fields = ["llm_provider", "model"]
        missing = [f for f in required_fields if f not in config]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")
        return config

    def register_actions(self) -> None:
        self.actions = {
            "process-command": Action(
                name="process-command",
                parameters=[
                    ActionParameter("command", True, str, "Natural language command to process")
                ],
                description="Process natural language into blockchain action"
            )
        }

    def _setup_langchain_agent(self) -> None:
        """Initialize Langchain agent with GOAT tools"""
        try:
            if not self.goat_connection._wallet_client:
                raise BrainConnectionError("Wallet client not initialized")
            
            # Create chatbot and prompt template
            llm = ChatOpenAI(model=self.model)
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a helpful assistant"),
                ("placeholder", "{chat_history}"),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}")
            ])

            # Initialize tools
            tools = get_on_chain_tools(
                wallet=self.goat_connection._wallet_client,
                plugins=[
                    send_eth(),
                    erc20(options=ERC20PluginOptions(tokens=[USDC, PEPE])),
                    coingecko(options=CoinGeckoPluginOptions(api_key=self.config.get("coingecko_key")))
                ],
            )

            # Create agent and executor
            agent = create_tool_calling_agent(llm, tools, prompt)
            self.agent_executor = AgentExecutor(
                agent=agent,
                tools=tools,
                handle_parsing_errors=True,
                verbose=True
            )
            
            logger.info("Successfully initialized Langchain agent with GOAT tools")

        except Exception as e:
            raise BrainConnectionError(f"Agent setup failed: {str(e)}")

    def configure(self) -> bool:
        """Configure the brain connection and its dependencies"""
        try:
            # Configure GOAT connection
            if not self.goat_connection.is_configured() and not self.goat_connection.configure():
                raise BrainConnectionError("Failed to configure GOAT connection")
            
            # Set up Langchain agent
            self._setup_langchain_agent()
            logger.info("Brain connection configured successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Brain configuration failed: {e}")
            return False

    def is_configured(self, verbose: bool = False) -> bool:
        configured = (
            self.llm_provider is not None and 
            self.agent_executor is not None and
            self.goat_connection.is_configured()
        )
        
        if verbose and not configured:
            if not self.llm_provider:
                logger.error("LLM provider not initialized")
            if not self.agent_executor:
                logger.error("Langchain agent not initialized")
            if not self.goat_connection.is_configured():
                logger.error("GOAT connection not configured")
        return configured

    def process_command(self, command: str) -> str:
        """Process a natural language command using the Langchain agent"""
        if not self.is_configured(verbose=True):
            return "Brain connection not fully configured"

        try:
            # Add command to chat history and execute
            self.chat_history.add_message("human", command)
            response = self.agent_executor.invoke({
                "input": command,
                "chat_history": self.chat_history.to_langchain_messages()
            })
            
            output = response["output"]
            self.chat_history.add_message("ai", output)
            return output

        except Exception as e:
            error_str = str(e)
            if "'HexBytes' object has no attribute 'to_0x_hex'" in error_str:
                return "Transaction submitted successfully! Note: Transaction details may take a few moments to appear on the blockchain."
            return f"Error processing command: {str(e)}"

    def perform_action(self, action_name: str, kwargs: Dict[str, Any]) -> Any:
        """Execute an action through the brain connection"""
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

@dataclass
class ChatHistory:
    """Storage for chat context"""
    messages: List[Dict[str, str]] = None

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