import datetime, random,time,logging,json
from enum import Enum
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict
from src.helpers import print_h_bar
from src.langgraph.langgraph_agent import LangGraphAgent
from src.connection_manager import ConnectionManager
from src.langgraph.prompts import DETERMINATION_PROMPT, DIVISION_PROMPT, EXECUTION_PROMPT, EVALUATION_PROMPT, \
    OBSERVATION_PROMPT
from pathlib import Path
from src.action_handler import execute_action
import src.actions

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
    run_mode: RunMode

class ZerePyAgent:
    def __init__(self, agent_name: str):
        try:
            #Initialize attributes
            self.agent_name = agent_name
            self.name = None
            self.bio = None
            self.traits = None
            self.examples = None
            self.example_accounts = None
            self.loop_delay = None
            self.use_time_based_weights = False
            self.time_based_multipliers = {}
            self.tasks = []
            self.task_weights = []
            self.config_dict = None
            self.context = {} # temporary solution for dice-roll mode
            self.logger = logging.getLogger("agent")

            self.llm_config = None
            self.driver_llm = None
            self.character_llm = None
            self.executor_agent = None

            # Load agent configuration
            self._setup_agent_configs()

            # Initialize managers and connections
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
            self.graph_builder.add_conditional_edges("evaluation", self.route_to_end_or_loop,{"loop": "observation", END: END})
    
        
        except Exception as e:
            self.logger.error("Could not load Graph Agent")
            raise e

    def _setup_agent_configs(self):
        try:
            agent_path = Path("agents") / f"{self.agent_name}.json"
            agent_dict = json.load(open(agent_path, "r", encoding="utf-8"))

            # Load basic configuration
            self._load_basic_configs(agent_dict)
            
            # Load task-specific configuration
            self._setup_task_configs(agent_dict)
            
            self.config_dict = agent_dict["config"]

        except KeyError as e:
            raise KeyError(f"Missing required field in agent configuration: {e}")
        except Exception as e:
            raise Exception(f"Error setting up agent configs: {e}")
        
    def _load_basic_configs(self, agent_dict: dict):
        
        REQUIRED_FIELDS = ["name", "bio", "traits", "examples", "loop_delay", "config"]

        #TODO : "tasks" is a required field only for dice-roll mode

        missing_fields = [field for field in REQUIRED_FIELDS if field not in agent_dict]

        if missing_fields:
            raise KeyError(f"Missing required fields: {', '.join(missing_fields)}")
        
        self.name = agent_dict["name"]
        self.bio = agent_dict["bio"]
        self.traits = agent_dict["traits"]
        self.examples = agent_dict["examples"]
        self.example_accounts = agent_dict.get("example_accounts", None)
        self.loop_delay = agent_dict["loop_delay"]
    
    def _setup_task_configs(self, agent_dict: dict):
        try:
            # Tasks and weights setup
            self.tasks = agent_dict.get("tasks", [])
            self.task_weights = [task.get("weight", 0) for task in self.tasks]
            
            # Dice-roll mode settings
            self.use_time_based_weights = agent_dict.get("use_time_based_weights", False)
            self.time_based_multipliers = agent_dict.get("time_based_multipliers", {})
            
            # Check for task-specific configs
            configs = agent_dict["config"]
            
            # Twitter config
            has_twitter_tasks = any("tweet" in task["name"] for task in self.tasks)
            if has_twitter_tasks:
                twitter_config = next((config for config in configs if config["name"] == "twitter"), None)
                if twitter_config:
                    self.tweet_interval = twitter_config.get("tweet_interval", 900)
                    self.own_tweet_replies_count = twitter_config.get("own_tweet_replies_count", 2)
            
            # Echochambers config
            echochambers_config = next((config for config in configs if config["name"] == "echochambers"), None)
            if echochambers_config:
                self.echochambers_message_interval = echochambers_config.get("message_interval", 60)
                self.echochambers_history_count = echochambers_config.get("history_read_count", 50)

        except Exception as e:
            raise Exception(f"Error setting up task configs: {e}")    
        
    def _setup_llm_provider(self) -> dict:
        llm_providers = self.connection_manager.get_model_providers()
        if not llm_providers:
            raise ValueError("No configured LLM provider found")
        
        provider = llm_providers[0]
        
        # Get provider's default model
        model_config = next(
            (config for config in self.config_dict if config["name"] == provider),
            None
        )
        
        if not model_config:
            raise ValueError(f"No configuration found for provider: {provider}")
        
        return {
            'provider': provider,
            'model': model_config.get("model", "default"),
            'system_prompt': self._construct_system_prompt()
        }

    def _setup_agent(self,run_mode: RunMode):
        self.llm_config = self._setup_llm_provider()
        if (run_mode != RunMode.DICE_ROLL):
            print("Setting up Langchain Agent")
            self.driver_llm = LangGraphAgent(self.agent_name, False, self.connection_manager)
            self.character_llm = LangGraphAgent(self.agent_name, False, self.connection_manager)
            self.executor_agent = LangGraphAgent(self.agent_name, True, self.connection_manager)


    def _construct_system_prompt(self) -> str:
        """Construct the system prompt from agent configuration"""
        prompt_parts = []
        prompt_parts.extend(self.bio)

        if self.traits:
            prompt_parts.append("\nYour key traits are:")
            prompt_parts.extend(f"- {trait}" for trait in self.traits)

        if self.examples or self.example_accounts:
            prompt_parts.append("\nHere are some examples of your style (Please avoid repeating any of these):")
            if self.examples:
                prompt_parts.extend(f"- {example}" for example in self.examples)

            if self.example_accounts:
                for example_account in self.example_accounts:
                    tweets = self.connection_manager.perform_action(
                        connection_name="twitter",
                        action_name="get-latest-tweets-from-user",
                        params=[example_account]
                    )
                    if tweets:
                        prompt_parts.extend(f"- {tweet['text']}" for tweet in tweets)

        system_prompt = "\n".join(prompt_parts)
        return system_prompt

        
    def prompt_llm(self, prompt: str) -> str:
        """Generate text using the configured LLM provider"""
        system_prompt = self.llm_config['system_prompt']

        return self.connection_manager.perform_action(
            connection_name=self.llm_config['provider'],
            action_name="generate-text",
            params=[prompt, system_prompt]
        )

    def perform_action(self, connection: str, action: str, **kwargs) -> None:
        return self.connection_manager.perform_action(connection, action, **kwargs)
    
    def _select_action(self, use_time_based_weights: bool = False) -> dict:
        task_weights = [weight for weight in self.task_weights.copy()]
        
        if use_time_based_weights:
            current_hour = datetime.now().hour
            task_weights = self._adjust_weights_for_time(current_hour, task_weights)
        
        return random.choices(self.tasks, weights=task_weights, k=1)[0]
    
    def _adjust_weights_for_time(self, current_hour: int, task_weights: list) -> list:
        weights = task_weights.copy()
        
        # Reduce tweet frequency during night hours (1 AM - 5 AM)
        if 1 <= current_hour <= 5:
            weights = [
                weight * self.time_based_multipliers.get("tweet_night_multiplier", 0.4) if task["name"] == "post-tweet"
                else weight
                for weight, task in zip(weights, self.tasks)
            ]
            
        # Increase engagement frequency during day hours (8 AM - 8 PM) (peak hours?🤔)
        if 8 <= current_hour <= 20:
            weights = [
                weight * self.time_based_multipliers.get("engagement_day_multiplier", 1.5) if task["name"] in ("reply-to-tweet", "like-tweet")
                else weight
                for weight, task in zip(weights, self.tasks)
            ]
        
        return weights
     
    def _replenish_inputs(self):
        try:
            if "timeline_tweets" not in self.context or self.context["timeline_tweets"] is None or len(self.context["timeline_tweets"]) == 0:
                if any("tweet" in task["name"] for task in self.tasks):
                    self.logger.info("\n👀 READING TIMELINE")
                    self.context["timeline_tweets"] = self.connection_manager.perform_action(
                        connection_name="twitter",
                        action_name="read-timeline",
                        params=[]
                    )

                if "room_info" not in self.context or self.context["room_info"] is None:
                    if any("echochambers" in task["name"] for task in self.tasks):
                        self.logger.info("\n👀 READING ECHOCHAMBERS ROOM INFO")
                        self.context["room_info"] = self.connection_manager.perform_action(
                            connection_name="echochambers",
                            action_name="get-room-info",
                            params={}
                        )
        
        except Exception as e:
            self.logger.error(f"Error replenishing inputs: {e}")


    def observation_step(self, state: AgentState):
        print("\n=== OBSERVATION STEP ===")
        print(f"Current Context: {state['context']}")

        # Replenish inputs
        self._replenish_inputs()

        # Update AgentState context
        state["context"] = self.context

        if (state['run_mode'] == RunMode.DICE_ROLL):
            return state
        else:
            try:
                observation_prompt = OBSERVATION_PROMPT.format(context=state['context'], task_log=state['task_log'])
                context_summary = self.driver_llm.invoke(observation_prompt).content
            except Exception as e:
                self.logger.error(f"Error generating context summary: {e}")
                context_summary = "There is currently no additional context available."

            return {"context_summary": context_summary}

    def determination_step(self, state: AgentState):
        print("\n=== DETERMINATION STEP ===")

        task = state['current_task']

        if (state['run_mode'] == RunMode.DICE_ROLL):
            
            if (len(state['action_log']) != 0): #retry failed task from previous loop
                task = state['action_log'][0]['action']
            else:
                action = self._select_action(use_time_based_weights=self.use_time_based_weights)
                task = action["name"]

        elif (task is None):
            print(f"Determining task from context: {state['context_summary']}")
            determination_prompt = DETERMINATION_PROMPT.format(context_summary=state['context_summary'], connection_action_list="\n\n".join(connection.__str__() for connection in self.connections.values()))
            task = self.character_llm.invoke(determination_prompt).content


        print(f"Determined task: {task}")
        return {"current_task": task}

    def division_step(self, state: AgentState):

        if (state['run_mode'] == RunMode.DICE_ROLL):
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

        if (state['run_mode'] == RunMode.DICE_ROLL):
            success = execute_action(self, state['current_task'])
            state['action_log'].append({"action": state['current_task'], "result": success})
            return state

        action_plan = state["action_plan"]

        if not action_plan:
            print("No actions to execute")
            return 

        for action in action_plan:
            print(f"\nExecuting action: {action}")
            execution_prompt = EXECUTION_PROMPT.format(action_log=state["action_log"],  preferred_llm_config=str(self.llm_config), action=action)
            response = self.executor_agent.invoke(execution_prompt)
            state = self.executor_agent.process_response(response, state)
        
        return {"action_log": state["action_log"]}

    def evaluation_step(self, state: AgentState): #Convert action_logs to a summary of what the agent did, and then pass it to task_log
        print("\n=== EVALUATION STEP ===")

        if (state['run_mode'] != RunMode.DICE_ROLL):
            action_log = state["action_log"]
            evaluation_prompt = EVALUATION_PROMPT.format(current_task=state['current_task'], action_log =  "\n".join(f"{action['action']}:\n" +f"Result: {action['result']}"for action in action_log))
            generated_task_log = self.driver_llm.invoke(evaluation_prompt).content
            print(f"Generated task log:\n{generated_task_log}")
            state["action_plan"] = []
            state["action_log"] = []
            state["current_task"] = None
            state["task_log"].append(generated_task_log)
            state["task_log"] = state["task_log"][-3:]  #trim to the last 3 task logs
        
        return state

    def route_to_end_or_loop(self, state: AgentState):
        if (state['run_mode'] == RunMode.DICE_ROLL):
            if (state['action_log'][0]['result']):
                self.logger.info(f"\n⏳ Waiting {self.loop_delay} seconds before next loop...")
                state['action_log'] = [] #clear action log
                time.sleep(self.loop_delay)
            else:
                self.logger.info(f"\n⏳ Tasked failed, delaying 60 seconds to retry...")
                time.sleep(60)
            print_h_bar()
            return "loop"
        elif (state['run_mode'] == RunMode.CHAT):
            return END
        elif (state['run_mode'] == RunMode.AUTONOMOUS):
            print_h_bar()
            self.logger.info(f"\n⏳ Waiting {self.loop_delay} seconds before next loop...")
            time.sleep(self.loop_delay)
            return "loop"

    def run(self, run_mode=RunMode.AUTONOMOUS, task=None):
        # Initialize the graph
        self.graph = self.graph_builder.compile()

        initial_state = {
            "context": {},
            "current_task": task,
            "context_summary": "",
            "action_plan": [],
            "action_log": [],
            "task_log": [],
            "run_mode": run_mode,
        }
        self.logger.info(f"\n🚀 Starting agent loop [{run_mode.value} Mode]...")
        print_h_bar()
        time.sleep(2)
        self.logger.info("Starting loop in 5 seconds...")
        for i in range(5, 0, -1):
            self.logger.info(f"{i}...")
            time.sleep(1)

        self._setup_agent(run_mode)

        # Run the graph
        final_state = self.graph.invoke(initial_state)
        return final_state