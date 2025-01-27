import json
from typing import List, Dict, Any
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from typing_extensions import TypedDict
from connections import TwitterConnection, OpenAIConnection, FarcasterConnection, AnthropicConnection

class AgentState(TypedDict):
    context: dict
    current_task: str | None
    action_plan: list
    current_action: str | None
    execution_log: list

class ZerePyAgent:
    def __init__(self):
        # Load agent configuration
        self.config_dict = json.load(open("example.json"))

        # Load connections with their tool descriptions
        self.connections = self.config_dict.get("connections", [])
        for connection in self.connections:
            if connection["name"] == "twitter":
                connection["object"] = TwitterConnection()
                connection["tool_executor"] = connection["object"].get_tool_executor()
                connection["description"] = connection["object"].get_tool_description()
            elif connection["name"] == "farcaster":
                connection["object"] = FarcasterConnection()
                connection["tool_executor"] = connection["object"].get_tool_executor()
                connection["description"] = connection["object"].get_tool_description()
            elif connection["name"] == "openai":
                connection["object"] = OpenAIConnection()
                connection["tool_executor"] = connection["object"].get_tool_executor()
                connection["description"] = connection["object"].get_tool_description()
            elif connection["name"] == "anthropic":
                connection["object"] = AnthropicConnection()
                connection["tool_executor"] = connection["object"].get_tool_executor()
                connection["description"] = connection["object"].get_tool_description()

        # Construct graph
        self.graph_builder = StateGraph(AgentState)

        # Add nodes
        self.graph_builder.add_node("observation", self.observation_step)
        self.graph_builder.add_node("determination", self.determination_step)
        self.graph_builder.add_node("division", self.division_step)
        self.graph_builder.add_node("execution", self.execution_step)
        self.graph_builder.add_node("evaluation", self.evaluation_step)

        # Add edges
        self.graph_builder.add_edge(START, "observation")
        self.graph_builder.add_edge("observation", "determination")
        self.graph_builder.add_edge("determination", "division")
        self.graph_builder.add_edge("division", "execution")
        self.graph_builder.add_edge("execution", "evaluation")
        self.graph_builder.add_edge("evaluation", END)

        # Load LLMs
        self.llms = self.config_dict.get("llms", [])
        for llm in self.llms:
            if llm["model_provider"] == "anthropic":
                llm["object"] = ChatAnthropic(model=llm["model"], api_key=ANTHROPIC_API_KEY)
            elif llm["model_provider"] == "openai":
                llm["object"] = ChatOpenAI(model=llm["model"], api_key=OPENAI_API_KEY)

            # Store special LLMs as instance variables
            if llm["name"] == "driver":
                self.driver_llm = llm["object"]
            elif llm["name"] == "character":
                self.character_llm = llm["object"]

    def observation_step(self, state: AgentState):
        print("\n=== OBSERVATION STEP ===")
        print(f"Current Context: {state['context']}")
        return {"context": state["context"]}

    def determination_step(self, state: AgentState):
        print("\n=== DETERMINATION STEP ===")
        print(f"Determining task from context: {state['context']}")
        task = "Make a funny tweet"
        print(f"Determined task: {task}")
        return {"current_task": task}

    def division_step(self, state: AgentState):
        print("\n=== DIVISION STEP ===")
        print(f"Creating action plan for task: {state['current_task']}")
        division_prompt = (f"Based on the the given task and available actions, generate an action plan for the agent. Only respond with the list of steps needed (with the corresponding actions mentioned), and put each step on a new line."
                           f"TASK:\n{state['current_task']}"
                           f"\n\nAVAILABLE CONNECTIONS:{'\n\n'.join(str(connection['description']) for connection in self.connections)}")
        action_plan_text = self.driver_llm.invoke(division_prompt).content
        action_plan = action_plan_text.split("\n")
        print(f"Generated action plan: {action_plan}")
        return {"action_plan": action_plan}

    def execution_step(self, state: AgentState) -> AgentState:
        print("\n=== EXECUTION STEP ===")
        print(f"Current action plan: {state['action_plan']}")
        action_plan = state["action_plan"]

        if not action_plan:
            print("No actions to execute")
            return state

        current_action = action_plan.pop(0)
        print(f"Executing action: {current_action}")

        # Use the driver_llm to decide which tool to use based on the current action
        tool_prompt = f"Based on the action '{current_action}', decide which tool to use and provide the necessary parameters."
        tool_response = self.driver_llm.invoke(tool_prompt)

        # Parse the tool response to get the tool name and parameters
        tool_name = tool_response.get("tool_name")
        tool_parameters = tool_response.get("parameters", {})

        # Find the tool executor for the current action
        tool_executor = None
        for connection in self.connections:
            if tool_name in connection["tool_executor"].tools:
                tool_executor = connection["tool_executor"]
                break

        if not tool_executor:
            raise ValueError(f"No tool executor found for action: {tool_name}")

        # Execute the tool with the provided parameters
        result = tool_executor.execute(tool_name, **tool_parameters)

        # Update the execution log
        state["execution_log"].append({
            "action": current_action,
            "tool": tool_name,
            "parameters": tool_parameters,
            "result": result
        })

        print(f"Action execution complete. Remaining actions: {action_plan}")
        return state

    def evaluation_step(self, state: AgentState):
        print("\n=== EVALUATION STEP ===")
        print(f"Evaluating execution log: {state['execution_log']}")
        return state

    def run(self):
        # Initialize the graph
        self.graph = self.graph_builder.compile()

        # Run the graph
        initial_state = {
            "context": {},
            "current_task": None,
            "action_plan": [],
            "current_action": None,
            "execution_log": []
        }

        print(f"Initial state: {initial_state}")
        final_state = self.graph.invoke(initial_state)
        return final_state

if __name__ == "__main__":
    agent = ZerePyAgent()
    final_state = agent.run()
    print(f"Final state: {final_state}")