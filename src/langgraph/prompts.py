OBSERVATION_PROMPT = ("TASK:\nSummarize the provided context and list of previous tasks in a short list of key points. Your summary will be used to help decide what to do next, so include anything relevant to the next task selection.\n\n"
                          "Guidelines:\n- Keep it concise and relevant\n- Avoid generic statements\n- Think critically about what information is useful for deciding which task should be performed next\n\n"
                          "CONTEXT:\n{context}\n\n"
                          "PREVIOUS TASKS:\n{task_log}\n\n"
                          "SUMMARY:\n")

DETERMINATION_PROMPT = """Based on the given context and available actions, generate a complex task that you desire to perform. Only respond with the task, and do not include any other text in your response. Your task can involve multiple chained actions. You do not need to provide any reasoning for the task. If you are given context, you may choose whether or not to use it. If you do not have context, you must still choose a task to perform.\n\n"
                        "CONTEXT SUMMARY:\n{context_summary}"
                        "\n\nAVAILABLE ACTIONS FOR EACH CONNECTION:\n\n" 
                        "{connection_action_list}"
                        "Example : Create a funny tweet and post it on Twitter"""


DIVISION_PROMPT = """Based on the given task and available actions, generate an action plan for the agent. Only respond with the list of steps needed (with the corresponding actions mentioned), and put each step on a new line. Only include actions that involve making requests—do not include actions like editing dialog boxes, clicking buttons, or other UI interactions.
                    
                    TASK:
                    {current_task}

                    AVAILABLE ACTIONS FOR EACH CONNECTION:
                    {connection_action_list}

                    IMPORTANT: When generating text using an LLM, you MUST use the exact configuration provided below for the `generate-text` action. Copy the entire configuration, including the complete system prompt:

                    LLM Configuration:
                    {preferred_llm_config}

                    Example :
                    TASK: Create a funny tweet and post it on Twitter
                    LLM Configuration: {{'provider': 'openai', 'model': 'gpt-3.5', 'system_prompt': 'Your key traits are: - Funny - Witty - Engaging\nHere are some examples of your style (Please avoid repeating any of these): - Joke 1 - Joke 2 - Joke 3'}}

                    Output: 
                    1. Generate text using openai `generate-text` with model : gpt-3.5 , system prompt: 'Your key traits are: - Funny - Witty - Engaging\nHere are some examples of your style (Please avoid repeating any of these): - Joke 1 - Joke 2 - Joke 3'
                    2. Post the generated text using `post-tweet` with the output from step 1

                    Rules:
                    - Do not combine multiple actions into one step
                    - Do not escape to a new line for a single step, until the step is complete
                    - Each step should represent a single action
                    - When using `generate-text`, include the complete system prompt from the LLM configuration
                    - Be explicit about which parameters are required for each action"""

EXECUTION_PROMPT =  ("Before executing the following action, consider the previous action log:\n\n"
                    "ACTION LOG:\n{action_log}\n\n"
                    "Refer to the 'final_response' field in the tool action log to quickly see the final response from the agent\n\n"
                     "Now, execute this action based on the prior results: {action}")

EVALUATION_PROMPT = ("Based on the action log, provide a summary of what the agent did based on the main task given. Only include the most important actions and the results of those actions. Do not include any actions that are irrelevant to the task or that did not produce a meaningful result.\n\n"
                   "Task:\n{current_task}"
                   "Action Log:\n" 
                   "{action_log}"
                   "\nExample Generated summary:\n Task: Make a funny tweet:\n1. Generated a witty joke using OpenAI : 'funny tweet generated'. 2. Posted 'funny tweet generated' joke on Twitter.")
