import json
import random
import time
import logging
import os
from pathlib import Path
from dotenv import load_dotenv
from src.connection_manager import ConnectionManager
from src.helpers import print_h_bar
from src.action_handler import execute_action
import src.actions.twitter_actions  
import src.actions.echochamber_actions
import src.actions.solana_actions
from datetime import datetime
from langchain.agents import Tool, initialize_agent
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

REQUIRED_FIELDS = ["name", "bio", "traits", "examples", "loop_delay", "config", "tasks", "langchain_config"]

logger = logging.getLogger("agent")

class ZerePyAgent:
    def __init__(
            self,
            agent_name: str
    ):
        try:
            agent_path = Path("agents") / f"{agent_name}.json"
            agent_dict = json.load(open(agent_path, "r"))

            missing_fields = [field for field in REQUIRED_FIELDS if field not in agent_dict]
            if missing_fields:
                raise KeyError(f"Missing required fields: {', '.join(missing_fields)}")

            self.name = agent_dict["name"]
            self.bio = agent_dict["bio"]
            self.traits = agent_dict["traits"]
            self.examples = agent_dict["examples"]
            self.example_accounts = agent_dict["example_accounts"]
            self.loop_delay = agent_dict["loop_delay"]
            self.connection_manager = ConnectionManager(agent_dict["config"])
            self.use_time_based_weights = agent_dict["use_time_based_weights"]
            self.time_based_multipliers = agent_dict["time_based_multipliers"]

            # TODO: Janky way to check if Twitter tasks exist, can we just check for twitter config?
            has_twitter_tasks = any("tweet" in task["name"] for task in agent_dict.get("tasks", []))
            
            twitter_config = next((config for config in agent_dict["config"] if config["name"] == "twitter"), None)
            
            if has_twitter_tasks and twitter_config:
                self.tweet_interval = twitter_config.get("tweet_interval", 900)
                self.own_tweet_replies_count = twitter_config.get("own_tweet_replies_count", 2)

            # Extract Echochambers config
            echochambers_config = next((config for config in agent_dict["config"] if config["name"] == "echochambers"), None)
            if echochambers_config:
                self.echochambers_message_interval = echochambers_config.get("message_interval", 60)
                self.echochambers_history_count = echochambers_config.get("history_read_count", 50)

            self.is_llm_set = False

            # Cache for system prompt
            self._system_prompt = None

            # Extract loop tasks
            self.tasks = agent_dict.get("tasks", [])
            self.task_weights = [task.get("weight", 0) for task in self.tasks]
            self.logger = logging.getLogger("agent")

            # Extract Langchain config
            langchain_config = agent_dict.get("langchain_config",
                                                   {"use_langchain": False,
                                                    "executor_model_provider": "openai",
                                                    "executor_model": "gpt-3.5-turbo"})
            if langchain_config.get("use_langchain", False):
                self.use_langchain = True
                executor_model_provider = langchain_config.get("executor_model_provider", "openai")
                executor_model = langchain_config.get("executor_model", "gpt-3.5-turbo")
                self._setup_langchain_tools(executor_model_provider, executor_model)
            else:
                self.use_langchain = False

            # Set up empty agent state
            self.state = {}

        except Exception as e:
            logger.error("Could not load ZerePy agent")
            raise e

    def _setup_llm_provider(self):
        # Get first available LLM provider and its model
        llm_providers = self.connection_manager.get_model_providers()
        if not llm_providers:
            raise ValueError("No configured LLM provider found")
        self.model_provider = llm_providers[0]

        # Load Twitter username for self-reply detection if Twitter tasks exist
        if any("tweet" in task["name"] for task in self.tasks):
            load_dotenv()
            self.username = os.getenv('TWITTER_USERNAME', '').lower()
            if not self.username:
                logger.warning("Twitter username not found, some Twitter functionalities may be limited")

    def _construct_system_prompt(self) -> str:
        """Construct the system prompt from agent configuration"""
        if self._system_prompt is None:
            prompt_parts = []
            prompt_parts.extend(self.bio)

            if self.traits:
                prompt_parts.append("\nYour key traits are:")
                prompt_parts.extend(f"- {trait}" for trait in self.traits)

            if self.examples or self.example_accounts:
                prompt_parts.append("\nHere are some examples of your style (Please avoid repeating any of these):")
                if self.examples:
                    prompt_parts.extend(f"- {example}" for example in self.examples)

                if self.example_accounts:
                    for example_account in self.example_accounts:
                        tweets = self.connection_manager.perform_action(
                            connection_name="twitter",
                            action_name="get-latest-tweets",
                            params=[example_account]
                        )
                        if tweets:
                            prompt_parts.extend(f"- {tweet['text']}" for tweet in tweets)

            self._system_prompt = "\n".join(prompt_parts)

        return self._system_prompt
    
    def _adjust_weights_for_time(self, current_hour: int, task_weights: list) -> list:
        weights = task_weights.copy()
        
        # Reduce tweet frequency during night hours (1 AM - 5 AM)
        if 1 <= current_hour <= 5:
            weights = [
                weight * self.time_based_multipliers.get("tweet_night_multiplier", 0.4) if task["name"] == "post-tweet"
                else weight
                for weight, task in zip(weights, self.tasks)
            ]
            
        # Increase engagement frequency during day hours (8 AM - 8 PM) (peak hours?🤔)
        if 8 <= current_hour <= 20:
            weights = [
                weight * self.time_based_multipliers.get("engagement_day_multiplier", 1.5) if task["name"] in ("reply-to-tweet", "like-tweet")
                else weight
                for weight, task in zip(weights, self.tasks)
            ]
        
        return weights

    def prompt_llm(self, prompt: str, system_prompt: str = None) -> str:
        """Generate text using the configured LLM provider"""
        system_prompt = system_prompt or self._construct_system_prompt()

        return self.connection_manager.perform_action(
            connection_name=self.model_provider,
            action_name="generate-text",
            params=[prompt, system_prompt]
        )

    def perform_action(self, connection: str, action: str, **kwargs) -> None:
        return self.connection_manager.perform_action(connection, action, **kwargs)
    
    def select_action(self) -> dict:
        task_weights = [weight for weight in self.task_weights.copy()]

        # IF USE_TIME_BASED_WEIGHTS
        if self.use_time_based_weights:
            # Apply time-based weight adjustments
            current_hour = datetime.now().hour
            task_weights = self._adjust_weights_for_time(current_hour, task_weights)
            return random.choices(self.tasks, weights=task_weights, k=1)[0]

        # IF USE_LANGCHAIN
        if self.use_langchain:
            try:
                logger.info("Using LangChain executor to select action...")
                # Use LangChain agent to select action
                prompt_template = ChatPromptTemplate.from_messages([
                    ("system", "You help choose the most appropriate action from a list based on context."),
                    ("system", "Context: {context}\n{additional_prompt}\nChoose the most appropriate action from the following list.\nAVAILABLE ACTIONS:\n{actions_list} \nLAST PERFORMED ACTION: {last_action}")
                ])
                # Format the actions list for the prompt
                actions_list = "\n".join(f"- {task["name"]}" for task in self.tasks)
                additional_prompt = "You MUST choose an action to perform. Do NOT provide context or reasoning for your decision, simply return the action you wish to perform. You should only respond with the name of the action you choose, nothing else. You MUST choose an action."

                # Run the agent with the formatted prompt
                result = self.executor.run(
                    prompt_template.format_messages(
                        context=self.bio,
                        actions_list=actions_list,
                        additional_prompt=additional_prompt,
                        last_action=self.state.get("last_action", "None")
                    )
                )
                logger.info("\nRESULT: " + result)

                for task in self.tasks:
                    if task["name"] in result.strip().lower():
                        logger.info("\nSelected action: " + result)
                        return task
            except Exception as e:
                logger.error(f"Error while using LangChain agent: {e}")

        return random.choices(self.tasks, weights=task_weights, k=1)[0]

    def loop(self):
        """Main agent loop for autonomous behavior"""
        if not self.is_llm_set:
            self._setup_llm_provider()

        logger.info("\n🚀 Starting agent loop...")
        logger.info("Press Ctrl+C at any time to stop the loop.")
        print_h_bar()

        time.sleep(2)
        logger.info("Starting loop in 5 seconds...")
        for i in range(5, 0, -1):
            logger.info(f"{i}...")
            time.sleep(1)

        try:
            while True:
                success = False
                try:
                    # REPLENISH INPUTS
                    # TODO: Add more inputs to complexify agent behavior
                    if "timeline_tweets" not in self.state or self.state["timeline_tweets"] is None or len(self.state["timeline_tweets"]) == 0:
                        if any("tweet" in task["name"] for task in self.tasks):
                            logger.info("\n👀 READING TIMELINE")
                            self.state["timeline_tweets"] = self.connection_manager.perform_action(
                                connection_name="twitter",
                                action_name="read-timeline",
                                params=[]
                            )

                    if "room_info" not in self.state or self.state["room_info"] is None:
                        if any("echochambers" in task["name"] for task in self.tasks):
                            logger.info("\n👀 READING ECHOCHAMBERS ROOM INFO")
                            self.state["room_info"] = self.connection_manager.perform_action(
                                connection_name="echochambers",
                                action_name="get-room-info",
                                params={}
                            )

                    # CHOOSE AN ACTION
                    action = self.select_action()
                    action_name = action["name"]

                    # UPDATE STATE
                    self.state["last_action"] = action_name

                    # PERFORM ACTION
                    success = execute_action(self, action_name)

                    logger.info(f"\n⏳ Waiting {self.loop_delay} seconds before next loop...")
                    print_h_bar()
                    time.sleep(self.loop_delay if success else 60)

                except Exception as e:
                    logger.error(f"\n❌ Error in agent loop iteration: {e}")
                    logger.info(f"⏳ Waiting {self.loop_delay} seconds before retrying...")
                    time.sleep(self.loop_delay)

        except KeyboardInterrupt:
            logger.info("\n🛑 Agent loop stopped by user.")
            return

    def _setup_langchain_tools(self, executor_model_provider: str, executor_model: str):
        try:
            # Set LLM
            # TODO: Handle API keys more cleanly
            load_dotenv()
            match executor_model_provider:
                case "openai":
                    api_key = os.getenv("OPENAI_API_KEY")
                    llm = ChatOpenAI(api_key=api_key, temperature=0.7, model_name=executor_model)
                case "anthropic":
                    api_key = os.getenv("ANTHROPIC_API_KEY")
                    llm = ChatAnthropic(api_key=api_key, temperature=0.7, model=executor_model)
                case _:
                    raise ValueError(f"Unsupported LLM provider: {executor_model_provider}")

            # Set up Tools for each task
            # TODO: Include task specific descriptions for better agent behavior
            tools = [
                Tool(
                    name=task["name"],
                    func=lambda _: task["name"],  # Each tool simply returns its name
                    description=f"This tool represents the action: '{task["name"]}'",
                    return_direct=True
                )
                for task in self.tasks
            ]

            # Bind Tools and LLM to LangChain agent
            agent = initialize_agent(
                tools=tools,
                llm=llm,
                agent_type="zero-shot-react-description",
                verbose=False,
            )

            # Set Agent Executor for the class
            self.executor = agent

        except Exception as e:
            logger.error(f"Error setting up LangChain tools: {e}")
            return