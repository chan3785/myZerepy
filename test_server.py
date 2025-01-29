from src.server.client import ZerePyClient
import time
import logging

def test_server():
    client = ZerePyClient("http://localhost:8000")
    
    # Test server status
    logging.info("\nChecking server status...")
    status = client.get_status()
    logging.info(f"Status: {status}")
    
    # List and load agents
    logging.info("\nListing agents...")
    agents = client.list_agents()
    logging.info(f"Available agents: {agents}")
    
    if agents:
        logging.info(f"\nLoading agent {agents[2]}...")
        result = client.load_agent(agents[2])
        logging.info(f"Load result: {result}")
        
        # List connections
        logging.info("\nListing connections...")
        connections = client.list_connections()
        logging.info(f"Connections: {connections}")
        
        # Start agent loop
        logging.info("\nStarting agent loop...")
        start_result = client.start_agent()
        logging.info(f"Start result: {start_result}")
        
        logging.info("\nWaiting 2 seconds...")
        time.sleep(2)
        
        # Stop agent loop
        logging.info("\nStopping agent loop...")
        stop_result = client.stop_agent()
        logging.info(f"Stop result: {stop_result}")
        
        # Try individual action
        logging.info("\nTrying single action...")
        action_result = client.perform_action(
            connection="solana",
            action="get-balance",
            params=[]
        )
        logging.info(f"Action result: {action_result}")

if __name__ == "__main__":
    test_server()