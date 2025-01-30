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
        "who are you",
        "give me info about bitcoin",
        "give me info about zerebro on solana",
        "what are all the things you can do?",
        "give me my eth balance",
        "what is the eth balance of 0xFF6CBf6830C47F683aC3227baD83c0BE5397A08F",
        "what is the market cap of zerebro",
        "generate a react button",
        "send .0001 of native token to 0xFF6CBf6830C47F683aC3227baD83c0BE5397A08F"
    ]

    # commands = ["give me info about zerebro on solana"]

    for cmd in commands:
        print(f"\nTesting: {cmd}")
        result = brain.process_command(cmd)
        # print(f"Result: {result}")

if __name__ == "__main__":
    test_brain()