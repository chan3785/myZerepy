import json
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict
from src.langgraph.langgraph_agent import LangGraphAgent
from src.connection_manager import ConnectionManager
from pathlib import Path


class AgentState(TypedDict):
    context: dict
    current_task: str | None
    action_plan: list
    action_log: list
    task_log: list

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
        task = "Make some tweet about rockets"
        print(f"Determined task: {task}")
        return {"current_task": task}

    def division_step(self, state: AgentState):
        print("\n=== DIVISION STEP ===")
        print(f"Creating action plan for task: {state['current_task']}")
        division_prompt = (f"Based on the given task and available actions, generate an action plan for the agent. Only respond with the list of steps needed (with the corresponding actions mentioned), and put each step on a new line. Only include actions that involve making requests—do not include actions like editing dialog boxes, clicking buttons, or other UI interactions. Assume the agent has the necessary connections to perform these actions, so do not include any steps related to establishing connections\n\n"
                   f"TASK:\n{state['current_task']}"
                   f"\n\nAVAILABLE ACTIONS FOR EACH CONNECTION:\n\n" +
                    "\n\n".join(connection.__str__() for connection in self.connections.values()) +
                   f"\nExample:\n Task: Make a funny tweet\n\nAction Plan:\n1.Generate a witty joke or humorous statement using OpenAI by leveraging the generate-text function with an appropriate system prompt and input prompt. 2. Post the generated joke on Twitter using the post-tweet function, setting the message parameter to the joke from step 1."+
                   f"\nDo not combine multiple actions into one step. Each step should represent a single action.")
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
            execution_prompt = (f"Before executing the following action, consider the previous action log:\n\n"
                        f"ACTION LOG:\n{state['action_log']}\n\n"
                        f"Refer to the 'final_response' field in the tool action log to quickly see the final response from the agent\n\n"
                        f"Now, execute this action based on the prior results: {action}")
            
            response = self.executor_agent.invoke(execution_prompt)
            state = self.executor_agent.process_response(response, state)

        
        return {"action_log": state["action_log"]}

    def evaluation_step(self, state: AgentState): #Convert action_logs to a summary of what the agent did , and then pass it to task_log
        print("\n=== EVALUATION STEP ===")
        action_log = state["action_log"]
        evaluation_prompt = (f"Based on the action log, provide a summary of what the agent did based on the main task given. Only include the most important actions and the results of those actions. Do not include any actions that are irrelevant to the task or that did not produce a meaningful result.\n\n"
                   f"Task:\n{state['current_task']}"
                   f"Action Log:\n" +
                   "\n".join(
                       f"{action['action']}:\n" +
                       f"Result: {action['result']}"
                       for action in action_log
                   )+
                   f"\nExample Generated summary:\n Task: Make a funny tweet:\n1. Generated a witty joke using OpenAI : 'funny tweet generated'. 2. Posted 'funny tweet generated' joke on Twitter."
                )
        generated_task_log = self.driver_llm.invoke(evaluation_prompt).content
        print(f"Generated task log:\n{generated_task_log}")
        state["action_plan"] = []
        state["action_log"] = [] 
        state["task_log"].append(generated_task_log)
        state["task_log"] = state["task_log"][-3:]  #trim to the last 3 task logs
        return state

    def run(self):
        # Initialize the graph
        self.graph = self.graph_builder.compile()

        # Run the graph
        initial_state = {
            "context": {},
            "current_task": "Increase Twitter followers",
            "action_plan": [],
            "action_log": [],
            "task_log": []
        }

        print(f"Initial state: {initial_state}")
        final_state = self.graph.invoke(initial_state)
        return final_state

