import json
from enum import Enum
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict
from src.langgraph.langgraph_agent import LangGraphAgent
from src.connection_manager import ConnectionManager
from src.langgraph.prompts import DETERMINATION_PROMPT, DIVISION_PROMPT, EXECUTION_PROMPT, EVALUATION_PROMPT
from pathlib import Path


class RunMode(Enum):
    AUTONOMOUS = "autonomous"
    CHAT = "chat"
    DICE_ROLL = "dice-roll"

class AgentState(TypedDict):
    context: dict
    context_summary: str
    current_task: str | None
    action_plan: list
    action_log: list
    task_log: list

class GraphAgent:
    def __init__(self, agent_name: str,run_mode: RunMode):
        # Load agent configuration

        agent_path = Path("agents") / f"{agent_name}.json"
        agent_dict = json.load(open(agent_path, "r", encoding="utf-8"))
        self.config_dict = agent_dict['config']
        self.run_mode = run_mode


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

    def _check_inputs_for_tasks(self):
        return None 
    
    def _select_action(self, use_time_based_weights: bool = False) -> dict:
        return "action"
    
    def _execute_action(self, action: dict) -> dict:  
        return "result"
    
    def observation_step(self, state: AgentState):
        print("\n=== OBSERVATION STEP ===")
        print(f"Current Context: {state['context']}")
        # TODO: USE LLM TO SUMMARIZE CONTEXT
        context_summary = "There is currently no additional context available."
        return {"context_summary": context_summary}

    def determination_step(self, state: AgentState):
        print("\n=== DETERMINATION STEP ===")
        
        task = state['current_task']

        if (self.run_mode == RunMode.DICE_ROLL):
            action = self.select_action(use_time_based_weights=self.use_time_based_weights)
            task = action["name"]
        elif (task is None):
            print(f"Determining task from context: {state['context_summary']}")        
            determination_prompt = DETERMINATION_PROMPT.format(context_summary=state['context_summary'], connection_action_list="\n\n".join(connection.__str__() for connection in self.connections.values()))
            task = self.character_llm.invoke(determination_prompt).content
           
            
        print(f"Determined task: {task}")
        return {"current_task": task}

    def division_step(self, state: AgentState):
        
        if (self.run_mode == RunMode.DICE_ROLL):
            return state #skip division, pass task state into execution
        
        print("\n=== DIVISION STEP ===")
        print(f"Creating action plan for task: {state['current_task']}")

        division_prompt = DIVISION_PROMPT.format(current_task=state['current_task'], connection_action_list="\n\n".join(connection.__str__() for connection in self.connections.values()))
        action_plan_text = self.driver_llm.invoke(division_prompt).content
        action_plan = action_plan_text.split("\n")

        print(f"Generated action plan: {action_plan}")
        return {"action_plan": action_plan}

    def execution_step(self, state: AgentState) -> AgentState:
        print("\n=== EXECUTION STEP ===")

        if (self.run_mode == RunMode.DICE_ROLL):
            success = self._execute_action(state['current_task'])
            state['action_log'].append({"action": state['current_task'], "result": success})
            return state 

        print(f"Current action plan: {state['action_plan']}")
        action_plan = state["action_plan"]

        if not action_plan:
            print("No actions to execute")
            return 

        for action in action_plan:
            print(f"\nExecuting action: {action}")
            execution_prompt = EXECUTION_PROMPT.format(action_log=state["action_log"], action=action)
            response = self.executor_agent.invoke(execution_prompt)
            state = self.executor_agent.process_response(response, state)
        
        return {"action_log": state["action_log"]}

    def evaluation_step(self, state: AgentState): #Convert action_logs to a summary of what the agent did, and then pass it to task_log
        print("\n=== EVALUATION STEP ===")
        
        if (self.run_mode == RunMode.DICE_ROLL):
            if (state['action_log'][0]['result']):
                print("Task successful")
            else:
                #retry, go back to execution
                #TODO: Implement retry logic
                pass


        action_log = state["action_log"]
        evaluation_prompt = EVALUATION_PROMPT.format(current_task=state['current_task'], action_log =  "\n".join(f"{action['action']}:\n" +f"Result: {action['result']}"for action in action_log))
        generated_task_log = self.driver_llm.invoke(evaluation_prompt).content
        print(f"Generated task log:\n{generated_task_log}")
        state["action_plan"] = []
        state["action_log"] = [] 
        state["task_log"].append(generated_task_log)
        state["task_log"] = state["task_log"][-3:]  #trim to the last 3 task logs
        return state

    def run(self,task=None):
        # Initialize the graph
        self.graph = self.graph_builder.compile()

        # Run the graph
        initial_state = {
            "context": {},
            "current_task": task,
            "action_plan": [],
            "action_log": [],
            "task_log": []
        }

        print(f"Initial state: {initial_state}")
        final_state = self.graph.invoke(initial_state)
        return final_state

