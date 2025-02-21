# ZerePy Server Mode Quick Start

## Initial Setup


1. Start the server:
```bash
poetry run python main.py --server
```

2. Check server status:
```bash
curl http://localhost:8000/
```
Response:
```json
{
    "status": "running",
    "agent": null,
    "agent_running": false
}
```

3. Load your agent:
```bash
curl -X POST http://localhost:8000/agents/auto-example/load
```
Response:
```json
{
    "status": "success",
    "agent": "example"
}
```

4. Check connection status:
```bash
curl http://localhost:8000/connections
```

## Making Task Processing Commands

### Request Format

```
POST /agent/action

Headers:
Content-Type: application/json

Request Body:
{
    "task": string,  // Natural language task you want the agent to perform
    "loop": boolean,     // (Optional) Whether or not you want the agent to loop the task
}
```

### Example Request

```bash
curl -X POST http://localhost:8000/agent/task \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Read the timeline, then check my solana balance",
    "loop": false
  }'
```

### Example Response
=== OBSERVATION STEP ===
Summarizing contextual information...
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"

CONTEXT SUMMARY:
- No contextual information provided.
- No previous tasks listed.

NEXT STEPS:
- Clarify the context and objectives to determine relevant tasks.
- Identify any goals or constraints that could inform future task selection.

=== DETERMINATION STEP ===
Determining next task...

DETERMINED TASK: Read the timeline, then check my solana balance

=== DIVISION STEP ===
Creating action plan for task: Read the timeline, then check my solana balance
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"

GENERATED ACTION PLAN:
1. Read the timeline using `read-timeline` with a specified count of tweets.
2. Check Solana balance using `get-balance` without any parameters for token_address.

=== EXECUTION STEP ===
Executing actions...

Executing action: 1. Read the timeline using `read-timeline` with a specified count of tweets.
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
Tool invoked: read-timeline with arguments: {'count': 5}
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
Final Response: Here are the latest tweets from the timeline:

1. **💽 (@gum_mp3)**: "My Cousin Vinny 9/10 real cinema"
   *Created at: 2025-02-21 20:47:45*

2. **. (@MRBLEUFACE)**: "RT @DzzzDayz: @MRBLEUFACE anything u had once u can go get again ski 😂"
   *Created at: 2025-02-21 20:47:24*

3. **Fat Kid Deals (@FatKidDeals)**: "48\" L-Shaped Gaming Desk for $37.99, reg $75.99!\n-- Use Promo Code 50LR1AN6\nhttps://t.co/Gag4e7AvfJ\n\n6pk of Seamless Thong/Underwear for $9.99!!\nhttps://t.co/DMWxQDR4dv"
   *Created at: 2025-02-21 20:47:00*
   ![Media](https://t.co/XkDWEc8acy)

4. **Danielle Fong 🔆 (@DanielleFong)**: "RT @EdKrassen: The DOW is now officially down since Trump took office.\n\nThe market closed at $43,487 on January 17, 2025. It's now at $43,4…"
   *Created at: 2025-02-21 20:47:00*

5. **Content Philosopher (@MoZarrinsadaf)**: "AI will not replace humans. It will replace average humans."
   *Created at: 2025-02-21 20:46:57*

Executing action: 2. Check Solana balance using `get-balance` without any parameters for token_address.
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
Tool invoked: get-balance with arguments: {}
Getting SOL balance
HTTP Request: POST https://api.mainnet-beta.solana.com "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
Final Response: Your current Solana balance is **0.205331117 SOL**.

=== EVALUATION STEP ===
Evaluating action logs...
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
Generated task log:
Task: Check Solana balance
1. Retrieved Solana balance: 0.205331117.

⏳ Waiting 60 seconds before next loop...

## Troubleshooting

If connections aren't configured automatically from your agent.json:

1. Configure Brain connection:
```bash
curl -X POST http://localhost:8000/connections/brain/configure \
  -H "Content-Type: application/json" \
  -d '{
    "params": {
        "llm_provider": "anthropic",
        "model": "claude-3-sonnet-20240229"
    }
  }'
```


2. Check specific connection status:
```bash
curl http://localhost:8000/connections/brain/status
```
Response:
```json
{
    "name": "brain",
    "configured": true,
    "is_llm_provider": false
}
```