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
from src.message_bus import MessageBus, MessagePayload

logger = logging.getLogger("agent")

REQUIRED_FIELDS = ["name", "bio", "traits", "examples", "loop_delay", "config", "tasks"]

class ZerePyAgent:
    def __init__(
        self,
        agent_name: str,
        message_bus: MessageBus = None
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
            self.loop_delay = agent_dict["loop_delay"]
            self.connection_manager = ConnectionManager(agent_dict["config"])

            # Extract Twitter config if Twitter tasks exist
            has_twitter_tasks = any(
                "tweet" in task["name"] or task["name"].startswith("like-tweet")
                for task in agent_dict.get("tasks", [])
            )
            twitter_config = next((cfg for cfg in agent_dict["config"] if cfg["name"] == "twitter"), None)
            if has_twitter_tasks and twitter_config:
                self.tweet_interval = twitter_config.get("tweet_interval", 900)
                self.own_tweet_replies_count = twitter_config.get("own_tweet_replies_count", 2)

            # Extract Echochambers config
            echochambers_config = next((cfg for cfg in agent_dict["config"] if cfg["name"] == "echochambers"), None)
            if echochambers_config:
                self.echochambers_message_interval = echochambers_config.get("message_interval", 60)
                self.echochambers_history_count = echochambers_config.get("history_read_count", 50)

            self.is_llm_set = False
            self._system_prompt = None
            self.tasks = agent_dict.get("tasks", [])
            self.task_weights = [task.get("weight", 0) for task in self.tasks]
            self.logger = logging.getLogger("agent")
            self.state = {}

            # New references for message bus
            self.message_bus = message_bus
            self.incoming_messages = []

            self.running = True

        except Exception as e:
            logger.error("Could not load ZerePy agent")
            raise e

    def _setup_llm_provider(self):
        llm_providers = self.connection_manager.get_model_providers()
        if not llm_providers:
            raise ValueError("No configured LLM provider found")
        self.model_provider = llm_providers[0]

        if any("tweet" in task["name"] for task in self.tasks):
            load_dotenv()
            self.username = os.getenv('TWITTER_USERNAME', '').lower()
            if not self.username:
                logger.warning("Twitter username not found; some Twitter functionalities may be limited")

    def _construct_system_prompt(self) -> str:
        if self._system_prompt is None:
            prompt_parts = []
            prompt_parts.extend(self.bio)

            if self.traits:
                prompt_parts.append("\nYour key traits are:")
                prompt_parts.extend(f"- {trait}" for trait in self.traits)

            if self.examples:
                prompt_parts.append("\nHere are some examples of your style (avoid repeating):")
                prompt_parts.extend(f"- {example}" for example in self.examples)

            self._system_prompt = "\n".join(prompt_parts)

        return self._system_prompt

    def prompt_llm(self, prompt: str, system_prompt: str = None) -> str:
        system_prompt = system_prompt or self._construct_system_prompt()
        return self.connection_manager.perform_action(
            connection_name=self.model_provider,
            action_name="generate-text",
            params=[prompt, system_prompt]
        )

    def perform_action(self, connection: str, action: str, **kwargs):
        return self.connection_manager.perform_action(connection, action, **kwargs)

    def loop(self):
        if not self.is_llm_set:
            self._setup_llm_provider()

        logger.info(f"\n🚀 Starting agent loop for {self.name}...")
        logger.info("Press Ctrl+C at any time to stop the loop.")
        print_h_bar()
        time.sleep(2)
        logger.info("Starting loop in 5 seconds...")
        for i in range(5, 0, -1):
            logger.info(f"{i}...")
            time.sleep(1)

        try:
            while self.running:
                success = False
                try:
                    # Collect and handle messages from the bus
                    self._collect_messages()
                    self._handle_incoming()

                    # Replenish inputs or do other tasks
                    self._check_inputs_for_tasks()

                    # Choose and perform an action
                    success = self._perform_regular_actions()

                    logger.info(f"\n⏳ Waiting {self.loop_delay} seconds before next loop...")
                    print_h_bar()
                    time.sleep(self.loop_delay if success else 60)

                except Exception as e:
                    logger.error(f"\n❌ Error in agent loop iteration: {e}")
                    logger.info(f"⏳ Waiting {self.loop_delay} seconds before retrying...")
                    time.sleep(self.loop_delay)

        except KeyboardInterrupt:
            self.stop()
            logger.info("\n🛑 Agent loop stopped by user.")

    def _collect_messages(self):
        if self.message_bus:
            all_messages = self.message_bus.fetch_all()
            relevant = [
                m for m in all_messages
                if m.receiver_id is None or m.receiver_id == self.name
            ]
            if relevant:
                self.logger.info(f"Agent {self.name} fetched {len(relevant)} messages from bus.")
            self.incoming_messages.extend(relevant)

    def _handle_incoming(self):
        """
        Handle each inbound message, possibly prompting the LLM to craft a response.
        """
        for msg in self.incoming_messages:
            self.logger.info(f"{self.name} received: {msg}")

            # If the message is truly from the "other" agent:
            if msg.sender_id != self.name:
                # Example: Pass the content to the LLM to generate a response
                system_prompt = f"You are {self.name}. Reply to the following:\n\n{msg.content}"
                generated_response = self.prompt_llm(prompt=msg.content, system_prompt=system_prompt)
                if generated_response:
                    # Send it back to the other agent
                    self.send_message(generated_response, receiver_id=msg.sender_id)

        self.incoming_messages.clear()

    def send_message(self, content: str, receiver_id: str = None):
        if not self.message_bus:
            self.logger.warning("No shared message bus is configured.")
            return
        message = MessagePayload(
            sender_id=self.name,
            receiver_id=receiver_id,
            content=content
        )
        self.message_bus.publish(message)

    def _check_inputs_for_tasks(self):
        if "timeline_tweets" not in self.state or not self.state["timeline_tweets"]:
            if any("tweet" in t["name"] for t in self.tasks):
                self.logger.info("\n👀 READING TIMELINE")
                self.state["timeline_tweets"] = self.connection_manager.perform_action(
                    connection_name="twitter",
                    action_name="read-timeline",
                    params=[]
                )

        if "room_info" not in self.state or not self.state["room_info"]:
            if any("echochambers" in t["name"] for t in self.tasks):
                self.logger.info("\n👀 READING ECHOCHAMBERS ROOM INFO")
                self.state["room_info"] = self.connection_manager.perform_action(
                    connection_name="echochambers",
                    action_name="get-room-info",
                    params={}
                )

    def _perform_regular_actions(self):
        success = False
        try:
            action = random.choices(self.tasks, weights=self.task_weights, k=1)[0]
            action_name = action["name"]
            success = execute_action(self, action_name)
        except Exception as e:
            self.logger.error(f"\n❌ Error in agent loop iteration: {e}")
        return success

    def stop(self):
        """
        Gracefully stops the agent by:
        1. Setting a flag to stop the main loop
        2. Cleaning up any active connections
        3. Clearing message queues
        4. Logging the shutdown process
        """
        self.logger.info(f"\n🛑 Stopping agent: {self.name}")
        
        # Set flag to stop the main loop
        self.running = False
        
        # Clear message queues
        self.incoming_messages.clear()
        
        # Clean up connection manager resources
        if self.connection_manager:
            for connection_name, connection in self.connection_manager.connections.items():
                try:
                    self.logger.info(f"Closing connection: {connection_name}")
                    if hasattr(connection, 'close'):
                        connection.close()
                except Exception as e:
                    self.logger.error(f"Error closing connection {connection_name}: {e}")
        
        # Clear state
        self.state.clear()
        self.is_llm_set = False
        
        self.logger.info(f"✅ Agent {self.name} stopped successfully")