from src.cli import ZerePyCLI
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("llm_test")

def test_llm_chat():
    """Test basic LLM chat functionality"""
    try:
        # Initialize CLI and load agent
        cli = ZerePyCLI()
        cli._load_agent_from_file("starter")
        
        if not cli.agent:
            logger.error("Failed to load agent")
            return
            
        # Set up LLM
        if not cli.agent.is_llm_set:
            cli.agent._setup_llm_provider()
            
        # Test some prompts
        test_prompts = [
            "Hello! What kind of agent are you?",
            "What are your interests?",
            "Tell me a joke about programming!"
        ]
        
        for prompt in test_prompts:
            logger.info(f"\nUser: {prompt}")
            response = cli.agent.prompt_llm(prompt)
            logger.info(f"\nAgent: {response}")
            
    except Exception as e:
        logger.error(f"Test failed: {e}")

if __name__ == "__main__":
    test_llm_chat()
