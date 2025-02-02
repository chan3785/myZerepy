from src.connections.brain_connection import BrainConnection
from src.connections.goat_connection import GoatConnection
from dotenv import load_dotenv
import json
import logging
import os

load_dotenv()

def load_agent_config(agent_name: str = "example") -> dict:
    """Load agent configuration from JSON file"""
    try:
        with open(f"agents/{agent_name}.json", "r") as f:
            config = json.load(f)
            
        # Extract relevant configurations
        brain_config = next((c for c in config["config"] if c["name"] == "brain"), None)
        goat_config = next((c for c in config["config"] if c["name"] == "goat"), None)
        
        if not brain_config or not goat_config:
            raise ValueError("Missing required brain or goat configuration")
            
        return {
            "brain": brain_config,
            "goat": goat_config
        }
    except Exception as e:
        raise Exception(f"Failed to load agent config: {e}")

def test_brain(agent_name: str = "example"):
    """Test brain functionality with configuration from agent file"""
    try:
        # Load configurations
        configs = load_agent_config(agent_name)
        
        # Initialize and configure GOAT connection
        goat_connection = GoatConnection(configs["goat"])
        if not goat_connection.configure():
            print("Failed to configure GOAT connection")
            return

        # Initialize and configure Brain connection
        brain_connection = BrainConnection(configs["brain"])
        if not brain_connection.configure(goat_connection):
            print("Failed to configure Brain connection")
            return

        # Test commands
        test_commands = [
            "what's my wallet address",
            "get me info about bitcoin",
            "check my eth balance",
            "help me swap 0.01 eth for usdc"
        ]

        for cmd in test_commands:
            print(f"\nTesting: {cmd}")
            result = brain_connection.process_command(cmd)
            print(f"Result: {result}")

    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    test_brain()