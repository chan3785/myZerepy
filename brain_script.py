import logging
from src.agent import ZerePyAgent
from dotenv import load_dotenv

# Set up logging with formatting
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

def main():
    # Load environment variables
    load_dotenv()
    
    # Initialize agent
    agent_name = "example"
    logger.info(f"\n🤖 Initializing agent: {agent_name}")
    agent = ZerePyAgent(agent_name)

    # Test command
    prompt = "hi please help me send 2 S tokens to this wallet 0xFF6CBf6830C47F683aC3227baD83c0BE5397A08F on sonic mainnet. thanks!"
    logger.info(f"\n📝 Processing command: {prompt}")
    
    try:
        result = agent.perform_action(
            connection="brain", 
            action="process-command",
            params={"command": prompt}
        )
        
        if result:
            logger.info(f"\n✅ Command result: {result}")
        else:
            logger.error("\n❌ Command returned no result")
            
    except Exception as e:
        logger.error(f"\n❌ Error executing command: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()