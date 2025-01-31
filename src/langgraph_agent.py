import os
from dotenv import load_dotenv
from connection_manager import ConnectionManager
from langgraph import ChatOpenAI, ToolExecutor, create_react_agent, AIMessage
from pathlib import Path
import json

class LangGraphAgent:
    def __init__(self,agent_name: str):
        agent_path = Path("agents") / f"{agent_name}.json"
        agent_dict = json.load(open(agent_path, "r"))

        if "config" not in agent_dict:
            raise KeyError(f"Missing required fields: config")
        
        self.connection_manager = ConnectionManager(agent_dict["config"])
        self.langgraphAgent = self._setup_langgraph_agent()

    def _collect_tools_from_connections(self):
        tools = []  
        for connection_name in self.connection_manager.get_connections():
            connection = self.connection_manager.get_connection(connection_name)
            if hasattr(connection, "tool_executor") and connection.tool_executor:
                tools.extend(connection.tool_executor.tools)
            else:
                print(f"Connection {connection_name} has no tools.")
        return tools

    def _setup_langgraph_agent(self):
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")    #default to use openai for now 
        if not api_key:
            raise ValueError("OpenAI API key not found in environment variables")

        model = ChatOpenAI(model="gpt-4", temperature=0.7, openai_api_key=api_key)
        tools = self._collect_tools_from_connections()
        tool_executor = ToolExecutor(tools)
        app = create_react_agent(model, tool_executor.tools)
        return app

    def invoke(self, user_input: str):
        state = {"messages": [{"role": "user", "content": user_input}]}
        final_state = self.langgraphAgent.invoke(state)
        response = next(
            msg.content for msg in reversed(final_state["messages"])
            if msg.content and isinstance(msg, AIMessage)
        )
        return response
    
    