import json
from idlelib.iomenu import encoding

from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict
from src.langgraph.langgraph_agent import LangGraphAgent
from src.connection_manager import ConnectionManager
from pathlib import Path


class AgentState(TypedDict):
    context: dict
    current_task: str | None
    action_plan: list
    current_action: str | None
    execution_log: list

class GraphAgent:
    def __init__(self, agent_name: str):
        # Load agent configuration

        agent_path = Path("agents") / f"{agent_name}.json"
        agent_dict = json.load(open(agent_path, "r", encoding="utf-8"))
        self.config_dict = agent_dict['config']


        self.connection_manager = ConnectionManager(self.config_dict)
        self.connections = self.connection_manager.get_connections()

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
        '''self.llms = self.config_dict.get("llms", [])
        for llm in self.llms:
            if llm["model_provider"] == "openai":
                llm["object"] = ChatOpenAI(model=llm["model"], api_key=OPENAI_API_KEY)

            # Store special LLMs as instance variables
            if llm["name"] == "driver":
                self.driver_llm = llm["object"]
            elif llm["name"] == "character":
                self.character_llm = llm["object"]
        
        llm = {}
        llm["object"] = ChatOpenAI(model="gpt-4", api_key=OPENAI_API_KEY)
        self.driver_llm = llm["object"]
        self.character_llm = llm["object"]'''
       
        #set up agents 
        self.driver_llm = LangGraphAgent(agent_name, False, self.connection_manager)
        self.character_llm = LangGraphAgent(agent_name, False, self.connection_manager)
        self.executor_agent = LangGraphAgent(agent_name, True, self.connection_manager)



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
        division_prompt = (f"Based on the given task and available actions, generate an action plan for the agent. Only respond with the list of steps needed (with the corresponding actions mentioned), and put each step on a new line. Only include actions that involve making requests—do not include actions like editing dialog boxes, clicking buttons, or other UI interactions. Assume the agent has the necessary connections to perform these actions, so do not include any steps related to establishing connections\n\n"
                   f"TASK:\n{state['current_task']}"
                   f"\n\nAVAILABLE ACTIONS FOR EACH CONNECTION:\n\n" +
                   "\n\n".join(connection.__str__() for connection in self.connections.values()) +
                   "\n\nEXAMPLE:\n\nExample Task: Make a funny tweet\n\nAction Plan:\n1.Generate a witty joke or humorous statement using OpenAI by leveraging the generate-text function with an appropriate system prompt and input prompt. 2. Post the generated joke on Twitter using the post-tweet function, setting the message parameter to the joke from step 1.")
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
            return 

        for action in action_plan:
            print(f"\nExecuting action: {action}")
            state = self.executor_agent.invoke_executor(action, state)
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
            "current_task": "Increase Twitter followers",
            "action_plan": [],
            "current_action": None,
            "execution_log": []
        }

        print(f"Initial state: {initial_state}")
        final_state = self.graph.invoke(initial_state)
        return final_state

