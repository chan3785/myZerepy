import logging
import threading
import time
from typing import List

from src.agent import ZerePyAgent
from src.message_bus import MessageBus

logger = logging.getLogger("swarm_manager")

class SwarmManager:
    """
    Manages a swarm (cluster) of agents, each running in its own thread.
    Agents can communicate via a shared MessageBus instance.
    """

    def __init__(self, agent_names: List[str]):
        # Shared message bus for all agents
        self.message_bus = MessageBus()
        self.agents: List[ZerePyAgent] = []
        self.threads: List[threading.Thread] = []
        self.running = False

        # Create each agent, providing the shared message bus
        for name in agent_names:
            try:
                agent = ZerePyAgent(agent_name=name, message_bus=self.message_bus)
                self.agents.append(agent)
            except Exception as e:
                logger.error(f"Failed to load agent '{name}': {e}")

    def start_all(self):
        """
        Start each agent's loop concurrently in its own thread.
        """
        logger.info("Starting swarm of agents...")
        self.running = True
        for agent in self.agents:
            thread = threading.Thread(target=self._run_agent_loop, args=(agent,))
            thread.daemon = True
            thread.start()
            self.threads.append(thread)

    def _run_agent_loop(self, agent: ZerePyAgent):
        """
        Each agent runs in a loop, handling messages and performing tasks.
        """
        try:
            agent.loop()
        except Exception as e:
            logger.error(f"Agent {agent.name} encountered error: {e}")

    def stop_all(self):
        """
        Attempt to stop all agents gracefully.
        """
        logger.info("Stopping swarm of agents...")
        self.running = False
        
        # Stop all agents
        for agent in self.agents:
            agent.stop()

        # Wait for all agent threads to complete with timeout
        for thread in self.threads:
            thread.join(timeout=5)  # Add timeout to prevent hanging
        
        # Clear resources
        self.threads.clear()
        self.agents.clear()
        self.message_bus = None
        logger.info("All agent threads stopped successfully")