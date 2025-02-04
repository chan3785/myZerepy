from src.connections.brain_connection import BrainConnection
from dotenv import load_dotenv
import json
import logging

load_dotenv()

def load_agent_config(agent_name: str = "example") -> dict:
    """Load agent configuration from JSON file"""
    try:
        with open(f"agents/{agent_name}.json", "r") as f:
            config = json.load(f)
            
        # Extract brain configuration
        brain_config = next((c for c in config["config"] if c["name"] == "brain"), None)
        
        if not brain_config:
            raise ValueError("Missing required brain configuration")
            
        return brain_config
        
    except Exception as e:
        raise Exception(f"Failed to load agent config: {e}")

def test_brain(agent_name: str = "example"):
    """Test brain functionality with configuration from agent file"""
    try:
        # Load brain configuration
        brain_config = load_agent_config(agent_name)
        
        # Initialize and configure Brain connection
        brain_connection = BrainConnection(brain_config)
        if not brain_connection.configure():
            print("Failed to configure Brain connection")
            return

        # Test commands
        test_commands = [
            # "what's my wallet address",
            # "get me info about bitcoin",
            # "check my eth balance",
            # "what actions can you do",
            # "please send .001 native token to 0xFF6CBf6830C47F683aC3227baD83c0BE5397A08F",
            "help me swap 3 of 0x833589fcd6edb6e08f4c7c32d4f71b54bda02913 for 0x2Da56AcB9Ea78330f947bD57C54119Debda7AF71"
            # "get me the token price of pepe using the uniswap plugin"
        ]

        for cmd in test_commands:
            print(f"\nTesting: {cmd}")
            result = brain_connection.process_command(cmd)
            print(f"Result: {result}")

    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    test_brain()