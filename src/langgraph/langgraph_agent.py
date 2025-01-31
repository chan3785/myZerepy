import os
from dotenv import load_dotenv
from src.connection_manager import ConnectionManager
from langchain_openai import ChatOpenAI
from typing_extensions import TypedDict
from langchain_core.messages import AIMessage,ToolMessage
from langgraph.prebuilt import ToolExecutor
from langgraph.prebuilt import create_react_agent
from pathlib import Path
import json

class LangGraphAgent:
    def __init__(self,agent_name: str, provide_tools:bool):

        agent_path = Path("agents") / f"{agent_name}.json"
        agent_dict = json.load(open(agent_path, "r"))

        if "langchain_config" not in agent_dict or agent_dict["langchain_config"]["use_langchain"] == False: #langgraph is not configured
            return None

        if "config" not in agent_dict:
            raise KeyError(f"Missing required fields: config")
        
        self.provideTools = provide_tools
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

        if self.provideTools:
            tool_executor = ToolExecutor(tools)
            app = create_react_agent(model, tool_executor.tools)
        else:
            app = create_react_agent(model)
            
        return app
    
    def invoke_chat(self, messages: list[dict]):
        state = {"messages": messages}
        final_state = self.langgraphAgent.invoke(state)
        response = next(
            msg.content for msg in reversed(final_state["messages"])
            if msg.content and isinstance(msg, AIMessage)
        )
        return response
    
    def _process_response(self, response, state):
        if "execution_log" not in state:
            state["execution_log"] = []

        messages = response.get("messages", [])
        last_tool_execution = None 

        for i, message in enumerate(messages):
            if isinstance(message, AIMessage):
                tool_calls = message.additional_kwargs.get("tool_calls", [])

                for tool_call in tool_calls:
                    tool_name = tool_call.get("function", {}).get("name") or tool_call.get("name")
                    args = tool_call.get("function", {}).get("arguments")
                    if isinstance(args, str):
                        try:
                            import json
                            tool_parameters = json.loads(args)
                        except json.JSONDecodeError:
                            tool_parameters = {"raw_args": args}
                    else:
                        tool_parameters = tool_call.get("args", {})

                    tool_result = None
                    tool_status = "pending"

                    for next_msg in messages[i:]:
                        if (isinstance(next_msg, ToolMessage) and 
                            next_msg.tool_call_id == tool_call.get("id")):
                            tool_result = next_msg.content
                            tool_status = next_msg.status
                            break

                    if tool_result is None:
                        for next_msg in messages[i:]:
                            if isinstance(next_msg, AIMessage) and next_msg.content:
                                tool_result = next_msg.content
                                break

                    last_tool_execution = {
                        "action": "tool_execution",
                        "tool": tool_name,
                        "parameters": tool_parameters,
                        "result": tool_result,
                        "status": tool_status
                    }

        if last_tool_execution:
            print("Tool Call Result : ", last_tool_execution["result"])
            state["execution_log"].append(last_tool_execution)

        return state
    
    def invoke_executor(self, user_input: str, state: dict):
        formatted_input = {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        f"Before executing the following action, consider the previous execution log:\n\n"
                        f"EXECUTION LOG:\n{json.dumps(state.get('execution_log', []), indent=2)}\n\n"
                        f"Now, execute this action based on the prior results: {user_input}"
                    ),
                }
                ],
                "execution_log": state["execution_log"]  
            }
         
        response = self.langgraphAgent.invoke(formatted_input)    
        state = self._process_response(response, state)    
        return state    

    
