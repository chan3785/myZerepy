import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from typing_extensions import TypedDict
from langchain_core.messages import AIMessage, ToolMessage
from langgraph.prebuilt import ToolExecutor, create_react_agent
from pathlib import Path
import json

class LangGraphAgent:
    def __init__(self, agent_name: str, provide_tools: bool, connection_manager=None):
        self.connection_manager = connection_manager
        self.provideTools = provide_tools
        self._load_agent_config(agent_name)
        self._load_environment_variables()
        self.langgraphAgent = self._setup_langgraph_agent()

    def _load_agent_config(self, agent_name: str):
        agent_path = Path("agents") / f"{agent_name}.json"
        agent_dict = json.load(open(agent_path, "r", encoding="utf-8"))

        if "langchain_config" not in agent_dict or not agent_dict["langchain_config"].get("use_langchain", False):
            raise ValueError("You must have a langchain_config configuration in your agent file or must have it enabled to use LangGraphAgent")

        if "config" not in agent_dict:
            raise KeyError("Missing required fields: config")

        self.langchainConfig = agent_dict["langchain_config"]

    def _load_environment_variables(self):
        load_dotenv()
        if (self.langchainConfig["provider"] == "openai"):
            self.api_key = os.getenv("OPENAI_API_KEY")
        else:
            self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("API key not found in environment variables")

    def _setup_langgraph_agent(self):
        if self.provideTools:
            return self._setup_agent_with_tools()
        return self._setup_agent_without_tools()

    def _setup_agent_with_tools(self):
        if (self.langchainConfig["provider"] == "openai"):
            model = ChatOpenAI(model=self.langchainConfig["executor_model"], temperature=0.7, openai_api_key=self.api_key)
        else:
            model = ChatAnthropic(model=self.langchainConfig["executor_model"] ,temperature=0.7,api_key=self.api_key)
        tools = self._collect_tools_from_connections()
        tool_executor = ToolExecutor(tools)
        return create_react_agent(model, tool_executor.tools)

    def _setup_agent_without_tools(self):
        if (self.langchainConfig["provider"] == "openai"):
            return ChatOpenAI(model=self.langchainConfig["driver_model"], api_key=self.api_key)
        return ChatAnthropic(model=self.langchainConfig["driver_model"], api_key=self.api_key)

    def _collect_tools_from_connections(self):
        tools = []
        for connection_name in self.connection_manager.get_connections():
            connection = self.connection_manager.get_connection(connection_name)
            if hasattr(connection, "tool_executor") and connection.tool_executor:
                tools.extend(connection.tool_executor.tools)
            else:
                print(f"Connection {connection_name} has no tools.")
        return tools

    def invoke(self, user_input: str):
        if self.provideTools:
            formatted_input = {"messages": [ {"role": "user","content": user_input}]}
            return self.langgraphAgent.invoke(formatted_input)
        else:
            return self.langgraphAgent.invoke(user_input)

    def invoke_chat(self, messages: list[dict]):
        state = {"messages": messages}
        final_state = self.langgraphAgent.invoke(state)
        response = next(
            msg.content for msg in reversed(final_state["messages"])
            if msg.content and isinstance(msg, AIMessage)
        )
        return response

    def process_response(self, response, state):

        messages = response.get("messages", [])
        last_tool_execution = None
        final_response = None

        try:
            final_response = next(
                msg.content for msg in reversed(messages)
                if msg.content and isinstance(msg, AIMessage)
            )
        except StopIteration:
            final_response = None

        for i, message in enumerate(messages):
            if isinstance(message, AIMessage):
                tool_executions = self._extract_tool_executions(message, messages, i)
                if tool_executions:
                    last_tool_execution = tool_executions

        if last_tool_execution:
            if (final_response): #log final response
                print("Final Response:", final_response)
                last_tool_execution["final_response"] = final_response

            state["action_log"].append(last_tool_execution)

        return state

    def _extract_tool_executions(self, message, messages, index):
        tool_calls = message.additional_kwargs.get("tool_calls", [])
        
        for tool_call in tool_calls:
            tool_name = self._get_tool_name(tool_call)
            tool_parameters = self._parse_tool_parameters(tool_call)
            tool_result, tool_status = self._find_tool_result(messages, index, tool_call)

            if tool_name:  #if we have a valid tool call
                return {
                    "action": "tool_execution",
                    "tool": tool_name,
                    "parameters": tool_parameters,
                    "result": tool_result,
                    "status": tool_status
                }
        return None

    def _get_tool_name(self, tool_call):
        """Extract tool name from tool call."""
        function_info = tool_call.get("function", {})
        return function_info.get("name") or tool_call.get("name")

    def _parse_tool_parameters(self, tool_call):
        args = tool_call.get("function", {}).get("arguments")
        if isinstance(args, str):
            try:
                return json.loads(args)
            except json.JSONDecodeError:
                return {"raw_args": args}
        return tool_call.get("args", {})

    def _find_tool_result(self, messages, start_index, tool_call):
        tool_result = None
        tool_status = "pending"

        # First look for a ToolMessage with matching tool_call_id
        for msg in messages[start_index:]:
            if isinstance(msg, ToolMessage) and msg.tool_call_id == tool_call.get("id"):
                return msg.content, msg.status

        # If no ToolMessage found, look for next AIMessage with content
        for msg in messages[start_index:]:
            if isinstance(msg, AIMessage) and msg.content:
                return msg.content, tool_status

        return tool_result, tool_status


