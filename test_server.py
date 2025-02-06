from src.client import ZerePyClient
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("server_test")

def test_server_mode():
    """Test ZerePy server functionality"""
    try:
        # Initialize client
        client = ZerePyClient("http://localhost:8000")
        
        # Check server status
        status = client.get_status()
        logger.info(f"Server Status: {status}")
        
        # Load minimal agent
        response = client.load_agent("mijo")
        logger.info(f"Load Agent Response: {response}")
        
        # List connections
        connections = client.list_connections()
        logger.info(f"Available Connections: {connections}")
        
        # Test Sonic connection
        logger.info("\nTesting Sonic connection...")
        
        # Get native token balance
        balance_result = client.perform_action(
            connection="sonic",
            action="get-balance",
            params=[]
        )
        logger.info(f"Native Token Balance: {balance_result}")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")

if __name__ == "__main__":
    test_server_mode()