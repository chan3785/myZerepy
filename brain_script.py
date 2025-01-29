from src.connections.brain_connection import BrainConnection
from dotenv import load_dotenv
import logging
load_dotenv()

# logging.basicConfig(level=logging.DEBUG)

def test_brain():
    config = {
        "llm_provider": "openai",
        "model": "gpt-4o",
        "plugins": [
            {
                "name": "coingecko",
                "args": {"api_key": "CG-12BeZ64iSajBLPPz8mfX4uao"}
            },
            {
                "name": "erc20",
                "args": {
                    "tokens": ["goat_plugins.erc20.token.PEPE", "goat_plugins.erc20.token.USDC"]
                }
            }
        ]
    }

    brain = BrainConnection(config)
    if not brain.configure():
        print("Failed to configure brain")
        return

    # Test commands
    commands = [
        "get me my wallet address",
        # "give me info about bitcoin",
        "give me my pepe balance on base",
        # "get me info about litecoin",
        "send .0001 of native token to 0xFF6CBf6830C47F683aC3227baD83c0BE5397A08F"
    ]

    for cmd in commands:
        print(f"\nTesting: {cmd}")
        result = brain.process_command(cmd)
        print(f"Result: {result}")

if __name__ == "__main__":
    test_brain()