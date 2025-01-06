# ZerePy

ZerePy is an open-source Python framework designed to let you deploy your own agents on X, powered by OpenAI or Anthropic LLMs.

ZerePy is built from a modularized version of the Zerebro backend. With ZerePy, you can launch your own agent with 
similar core functionality as Zerebro. For creative outputs, you'll need to fine-tune your own model.

## Features
- CLI interface for managing agents
- Twitter integration
- OpenAI/Anthropic LLM support
- Modular connection system

## Quickstart

The quickest way to start using ZerePy is to use our Replit template:

https://replit.com/@blormdev/ZerePy?v=1

1. Fork the template (you will need you own Replit account)
2. Click the run button on top
3. Voila! your CLI should be ready to use, you can jump to the configuration section

## Requirements

System:
- Python 3.10 or higher
- Poetry 1.5 or higher

API keys:
  - LLM: make an account and grab an API key 
      + OpenAI: https://platform.openai.com/api-keys.
      + Anthropic: https://console.anthropic.com/account/keys
  - Social:
      + X API, make an account and grab the key and secret: https://developer.x.com/en/docs/authentication/oauth-1-0a/api-key-and-secret

## Installation

1. First, install Poetry for dependency management if you haven't already:

Follow the steps here to use the official installation: https://python-poetry.org/docs/#installing-with-the-official-installer

2. Clone the repository:
```bash
git clone https://github.com/blorm-network/ZerePy.git
```

3. Go to the `zerepy` directory:
```bash
cd zerepy
```

4. Install dependencies:
```bash
poetry install --no-root
```

This will create a virtual environment and install all required dependencies.

## Usage

1. Activate the virtual environment:
```bash
poetry shell
```

2. Run the application:
```bash
poetry run python main.py
```

## Configure connections & launch an agent

1. Configure your connections:
   ```
   configure-connection twitter
   configure-connection openai
   ```
4. Load your agent (usually one is loaded by default, which can be set using the CLI or in agents/general.json):
   ```
   load-agent example
   ```
5. Start your agent:
   ```
   start
   ```

## Create your own agent

The secret to having a good output from the agent is to provide as much detail as possible in the configuration file. Craft a story and a context for the agent, and pick very good examples of tweets to include.

If you want to take it a step further, you can fine tune your own model: https://platform.openai.com/docs/guides/fine-tuning.

Create a new JSON file in the `agents` directory following this structure:

```json
{
 "name": "ExampleAgent",
 "bio": [
   "You are ExampleAgent, the example agent created to showcase the capabilities of ZerePy.",
   "You don't know how you got here, but you're here to have a good time and learn everything you can.",
   "You are naturally curious, and ask a lot of questions."
  ],
  "traits": [
    "Curious",
    "Creative",
    "Innovative",
    "Funny"
  ],
  "examples": [
    "This is an example tweet.",
    "This is another example tweet."
  ],
  "loop_delay": 60,
  "config": [
    {
      "name": "twitter",
      "timeline_read_count": 10,
      "tweet_interval": 900,
      "own_tweet_replies_count":2
    },
    {
      "name": "openai",
      "model": "gpt-3.5-turbo"
    },
    {
      "name": "anthropic",
      "model": "claude-3-5-sonnet-20241022"
    }
  ],
  "tasks": [
    {"name": "post-tweet", "weight": 1},
    {"name": "reply-to-tweet", "weight": 1},
    {"name": "like-tweet", "weight": 1}
  ]
}
```

## Multi-Agent Swarms

ZerePy now supports running multiple agents simultaneously in "swarms". Agents in a swarm can:
- Run concurrently in separate threads
- Communicate autonomously via a shared message bus
- Process messages using their configured LLMs
- Maintain their individual task loops while communicating

### Creating Swarm-Ready Agents

Create agent configuration files that include message handling capabilities:

```json
{
  "name": "SwarmAgent1",
  "bio": [
    "You are SwarmAgent1, an AI that engages in deep discussions.",
    "You process incoming messages and generate thoughtful responses."
  ],
  "traits": [
    "Analytical",
    "Communicative",
    "Collaborative"
  ],
  "examples": [
    "That's an interesting perspective on AI consciousness...",
    "Your point about emergent behavior reminds me of..."
  ],
  "loop_delay": 10,
  "config": [
    {
      "name": "openai",
      "model": "gpt-3.5-turbo"
    }
  ],
  "tasks": [
    {"name": "message-loop", "weight": 1},
    {"name": "post-tweet", "weight": 1}
  ]
}
```

### Running a Swarm

1. Configure your LLM connections, for example:
```bash
configure-connection openai
```

2. Start a swarm from the CLI:
```bash
swarm agent1 agent2 agent3
```

The swarm will run autonomously with agents:
- Processing their individual task loops
- Collecting messages from the shared message bus
- Generating responses using their LLM configurations
- Publishing responses back to the message bus
- Running until interrupted with Ctrl+C

### Architecture

The swarm system consists of three main components:

1. **SwarmManager**: Orchestrates multiple agents and manages their lifecycle
2. **MessageBus**: Handles inter-agent communication and message routing

```
┌─────────────────────────────────────────┐
│              SwarmManager               │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────┐        ┌──────────┐       │
│  │ Agent 1  │◄─────► │ Agent 2  │       │
│  └──────────┘        └──────────┘       │
│        ▲                   ▲            │
│        │                   │            │
│        └───────┬───────────┘            │
│                │                        │
│           ┌──────────┐                  │
│           │MessageBus│                  │
│           └──────────┘                  │
│                                         │
└─────────────────────────────────────────┘
```

### Message Bus System

The MessageBus enables autonomous inter-agent communication:
- Thread-safe message publishing and collection
- Automatic message routing between agents
- Support for direct and broadcast messages
- Integrated with agent task loops

### Additional Features

- **Concurrent Execution**: Each agent runs in its own thread
- **Resource Management**: Shared connection pools and resources
- **Graceful Shutdown**: Clean shutdown with proper resource cleanup
- **Autonomous Operation**: No manual intervention needed after launch
- **Task Integration**: Messages processed alongside regular agent tasks

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=blorm-network/ZerePy&type=Date)](https://star-history.com/#blorm-network/ZerePy&Date)

---
Made with ♥ @Blorm.xyz
