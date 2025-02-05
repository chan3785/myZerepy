
DETERMINATION_PROMPT = ("Based on the given context and available actions, generate a complex task that you desire to perform. Only respond with the task, and do not include any other text in your response. Your task can involve multiple chained actions. You do not need to provide any reasoning for the task. If you are given context, you may choose whether or not to use it. If you do not have context, you must still choose a task to perform.\n\n"
                        "CONTEXT SUMMARY:\n{context_summary}"
                        "\n\nAVAILABLE ACTIONS FOR EACH CONNECTION:\n\n" 
                        "{connection_action_list}")

DIVISION_PROMPT = ("Based on the given task and available actions, generate an action plan for the agent. Only respond with the list of steps needed (with the corresponding actions mentioned), and put each step on a new line. Only include actions that involve making requests—do not include actions like editing dialog boxes, clicking buttons, or other UI interactions. Assume the agent has the necessary connections to perform these actions, so do not include any steps related to establishing connections\n\n"
                    "TASK:\n{current_task}"
                    "\n\nAVAILABLE ACTIONS FOR EACH CONNECTION:\n\n" 
                    "{connection_action_list}"
                    "\nExample:\n Task: Make a funny tweet\n\nAction Plan:\n1.Generate a witty joke or humorous statement using OpenAI by leveraging the generate-text function with an appropriate system prompt and input prompt. 2. Post the generated joke on Twitter using the post-tweet function, setting the message parameter to the joke from step 1."
                   "\nDo not combine multiple actions into one step. Each step should represent a single action.")

EXECUTION_PROMPT =  ("Before executing the following action, consider the previous action log:\n\n"
                    "ACTION LOG:\n{action_log}\n\n"
                    "Refer to the 'final_response' field in the tool action log to quickly see the final response from the agent\n\n"
                     "Now, execute this action based on the prior results: {action}")

EVALUATION_PROMPT = ("Based on the action log, provide a summary of what the agent did based on the main task given. Only include the most important actions and the results of those actions. Do not include any actions that are irrelevant to the task or that did not produce a meaningful result.\n\n"
                   "Task:\n{current_task}"
                   "Action Log:\n" 
                   "{action_log}"
                   "\nExample Generated summary:\n Task: Make a funny tweet:\n1. Generated a witty joke using OpenAI : 'funny tweet generated'. 2. Posted 'funny tweet generated' joke on Twitter.")


