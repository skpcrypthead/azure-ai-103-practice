# AI-103 Azure AI Foundry — Complete Study & Revision Reference

> **Module:** Develop a Generative AI Chat App with Microsoft Foundry
> **Source:** MS Learn + 14 Personal Lab Practices
> **Scope:** ChatCompletions API · Responses API · Streaming · Async · AI Agents · Foundry SDK

---

## Table of Contents

1. [Azure AI Foundry — Overview](#1-azure-ai-foundry--overview)
2. [Authentication — DefaultAzureCredential](#2-authentication--defaultazurecredential)
3. [ChatCompletions API](#3-chatcompletions-api)
4. [Responses API](#4-responses-api)
5. [Streaming](#5-streaming)
6. [Async Programming](#6-async-programming)
7. [Azure AI Foundry SDK — AIProjectClient](#7-azure-ai-foundry-sdk--aiprojectclient)
8. [AI Agents](#8-ai-agents)
9. [Calling Existing Agents](#9-calling-existing-agents)
10. [API Comparison — Quick Reference](#10-api-comparison--quick-reference)
11. [Environment Setup](#11-environment-setup)
12. [Common Errors & Fixes](#12-common-errors--fixes)

---

## 1. Azure AI Foundry — Overview

### What is Azure AI Foundry?

Azure AI Foundry (formerly Azure AI Studio) is Microsoft's unified platform for building, deploying, and managing AI applications. It provides:

- A **project-based workspace** that connects to models, data, and services
- **Model catalog** — OpenAI models (GPT-4.1, GPT-4o) and non-OpenAI models (Phi-4, Mistral, Meta Llama)
- **Agent framework** — build autonomous AI agents with tools
- **Evaluation and monitoring** — test and track AI app performance
- **SDK access** — via `azure-ai-projects` and standard `openai` Python packages

### Key Concepts

| Concept | Description |
|---|---|
| **Hub** | Top-level Azure resource — shared infrastructure, security, networking |
| **Project** | Child of a hub — your working environment for a specific app or team |
| **Deployment** | A specific model version deployed within your project (e.g. `gpt-4.1`) |
| **Connection** | Links to external services (Azure OpenAI, AI Search, storage) configured in your project |
| **Agent** | An AI entity with instructions, tools, and persistent threads |
| **Thread** | A persistent conversation session for an agent |
| **Run** | One execution of an agent against a thread |

### Two Ways to Access Models

```
Option A: Direct OpenAI client → client.responses.create() or client.chat.completions.create()
Option B: Foundry SDK      → AIProjectClient → project_client.get_openai_client()
```

Both ultimately call the same Azure OpenAI endpoints, but Option B gives you full access to Foundry project features (agents, connections, evaluations).

---

## 2. Authentication — DefaultAzureCredential

### Why Not Use API Keys?

- API keys are static secrets — if leaked, your entire resource is compromised
- Keys require manual rotation
- Azure AD tokens are short-lived (1 hour), auto-rotating, and scope-limited

### The Standard Pattern (Synchronous)

```python
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import OpenAI

# Creates a callable that returns a fresh token when called
token_provider = get_bearer_token_provider(
    DefaultAzureCredential(),
    "https://ai.azure.com/.default"   # scope for AI Foundry endpoints
)

client = OpenAI(
    base_url=azure_openai_endpoint,
    api_key=token_provider   # pass the callable, NOT token_provider()
)
```

> **Important:** Pass `token_provider` (the callable), not `token_provider()` (the token string).
> The SDK calls it internally before each request to ensure a fresh token.

### The Standard Pattern (Async)

```python
from azure.identity.aio import DefaultAzureCredential, get_bearer_token_provider
from openai import AsyncOpenAI

credential = DefaultAzureCredential()
token_provider = get_bearer_token_provider(credential, "https://ai.azure.com/.default")

async_client = AsyncOpenAI(
    base_url=azure_openai_endpoint,
    api_key=token_provider
)

# Always close the credential in finally block
try:
    ...
finally:
    await credential.close()  # releases the async HTTP session
```

> **Note the import difference:**
> - Sync: `from azure.identity import DefaultAzureCredential`
> - Async: `from azure.identity.aio import DefaultAzureCredential` (`.aio` submodule)

### Authentication Scope Reference

| Endpoint Type | Scope |
|---|---|
| Azure AI Foundry (new) | `https://ai.azure.com/.default` |
| Azure Cognitive Services (older) | `https://cognitiveservices.azure.com/.default` |
| Azure Management | `https://management.azure.com/.default` |

### DefaultAzureCredential — Authentication Chain

`DefaultAzureCredential` tries these in order, using the first that succeeds:

1. Environment variables (`AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`, `AZURE_TENANT_ID`)
2. Workload Identity (Kubernetes)
3. Managed Identity
4. Azure CLI (`az login`)
5. Azure PowerShell
6. Visual Studio Code (Azure extension)
7. Interactive browser (last resort)

In local development, Azure CLI login (`az login`) is typically used. In production, Managed Identity is preferred.

---

## 3. ChatCompletions API

### What is it?

The ChatCompletions API (`client.chat.completions.create()`) is the classic, stateless OpenAI-compatible interface. It takes a list of messages and returns a completion. It is widely supported across all OpenAI-compatible services.

**Key characteristic: Stateless.** The model has no memory between calls. You must include all prior conversation turns in every request.

### Roles in the Messages Array

| Role | Purpose |
|---|---|
| `system` | Sets AI persona, behaviour, constraints. Usually first message. |
| `user` | The human's input/question |
| `assistant` | The AI's previous reply (used when building conversation history) |

### Basic Single-Turn Chat (Practice01, Practice09)

```python
import os
from dotenv import load_dotenv
from openai import OpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

load_dotenv()
azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
model_deployment = os.getenv("MODEL_DEPLOYMENT")

token_provider = get_bearer_token_provider(
    DefaultAzureCredential(),
    "https://ai.azure.com/.default"
)

openai_client = OpenAI(
    base_url=azure_openai_endpoint,
    api_key=token_provider
)

completion = openai_client.chat.completions.create(
    model=model_deployment,
    messages=[
        {"role": "system", "content": "You are a helpful AI assistant."},
        {"role": "user",   "content": "When was Microsoft founded?"}
    ]
)

print(completion.choices[0].message.content)
```

### Interactive Loop — Single Turn per Prompt (Practice01)

```python
while True:
    input_text = input('\nEnter a prompt (or type "quit" to exit): ')
    if input_text.lower() == "quit":
        break
    if len(input_text) == 0:
        print("Please enter a prompt.")
        continue

    completion = openai_client.chat.completions.create(
        model=model_deployment,
        messages=[
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user",   "content": input_text}
        ]
    )
    print(completion.choices[0].message.content)
```

> **Limitation:** Each iteration is independent. The model does not remember the previous prompt.

### Multi-Turn Conversation — Manual History (Practice05, Practice10)

To retain context, you must manually build and maintain the `conversation_messages` list.

```python
# Initialize with system message
conversation_messages = [
    {"role": "system", "content": "You are a helpful AI assistant."}
]

while True:
    input_text = input('\nEnter a prompt (or type "quit" to exit): ')
    if input_text.lower() == "quit":
        break

    # Step 1: Append user message to history
    conversation_messages.append(
        {"role": "user", "content": input_text}
    )

    # Step 2: Send full history to model
    completion = openai_client.chat.completions.create(
        model=model_deployment,
        messages=conversation_messages
    )

    assistant_message = completion.choices[0].message.content
    print("\nAssistant:", assistant_message)

    # Step 3: Append assistant reply to history for next turn
    conversation_messages.append(
        {"role": "assistant", "content": assistant_message}
    )
```

**How the messages array grows over 2 turns:**

```
Turn 1 sent:  [system, user_1]
Turn 1 back:  assistant_1
Turn 2 sent:  [system, user_1, assistant_1, user_2]   ← full history
Turn 2 back:  assistant_2
```

### Hardcoded Two-Turn Example (Practice10)

```python
# Turn 1
conversation_messages = [
    {"role": "system",    "content": "You are a helpful AI assistant."},
    {"role": "user",      "content": "When was Microsoft founded?"}
]
completion = openai_client.chat.completions.create(model="gpt-4.1", messages=conversation_messages)
assistant_message = completion.choices[0].message.content
print("Assistant:", assistant_message)
conversation_messages.append({"role": "assistant", "content": assistant_message})

# Turn 2 — model knows context from Turn 1
conversation_messages.append({"role": "user", "content": "Who founded it?"})
completion = openai_client.chat.completions.create(model="gpt-4.1", messages=conversation_messages)
print("Assistant:", completion.choices[0].message.content)
```

### Response Object Structure

```
completion
  └── choices[]
        └── [0]
              └── message
                    ├── role     → "assistant"
                    └── content  → "The response text..."
```

---

## 4. Responses API

### What is it?

The Responses API (`client.responses.create()`) is Azure AI Foundry's newer, stateful interface. It stores conversation history server-side and links turns via `previous_response_id`. It is the **preferred API for new Azure AI Foundry applications**.

**Key characteristic: Stateful.** Azure remembers the conversation. You only need to pass the last response's ID.

### Basic Single Call (Practice03)

```python
import os
import dotenv
from openai import OpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

dotenv.load_dotenv()
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
model = os.getenv("MODEL_DEPLOYMENT")

token_provider = get_bearer_token_provider(
    DefaultAzureCredential(), "https://ai.azure.com/.default"
)
client = OpenAI(base_url=endpoint, api_key=token_provider)

response = client.responses.create(
    model=model,
    input="What is quantum computing?",
    instructions="You are a helpful AI assistant that answers questions clearly.",
    temperature=0.2,
    max_output_tokens=100,
    top_p=0.5
)

print(f"Response:  {response.output_text}")
print(f"ID:        {response.id}")
print(f"Tokens:    {response.usage.total_tokens}")
print(f"Status:    {response.status}")
```

### Response Object Structure

```
response
  ├── id              → "resp_04d13fbc..."  (use as previous_response_id)
  ├── output_text     → "The response text..."
  ├── status          → "completed"
  ├── model           → "gpt-4.1"
  └── usage
        ├── input_tokens   → 18
        ├── output_tokens  → 412
        └── total_tokens   → 430
```

### Stateful Multi-Turn Conversation (Practice05)

```python
# Turn 1
response1 = client.responses.create(
    model="gpt-4.1",
    instructions="You are a helpful AI assistant that explains technology concepts.",
    input="What is machine learning?"
)
print("Assistant:", response1.output_text)

# Turn 2 — linked to Turn 1 via previous_response_id
response2 = client.responses.create(
    model="gpt-4.1",
    instructions="You are a helpful AI assistant that explains technology concepts.",
    input="Can you give me an example?",
    previous_response_id=response1.id    # ← this is the key
)
print("Assistant:", response2.output_text)
```

> The model in Turn 2 automatically knows the context of Turn 1 because Azure stored it server-side.

### Interactive Loop with State (Practice02, Practice03)

```python
last_response_id = None

while True:
    input_text = input('\nEnter a prompt (or type "quit" to exit): ')
    if input_text.lower() == "quit":
        break

    response = client.responses.create(
        model=model_deployment,
        instructions="You are a helpful AI assistant.",
        input=input_text,
        previous_response_id=last_response_id   # None on first turn
    )
    print(response.output_text)
    last_response_id = response.id   # carry forward for next turn
```

### Manual Conversation Chaining (Practice06)

An alternative approach — build the full input history manually without relying on `previous_response_id`:

```python
# Start with initial message list
conversation_history = [
    {"type": "message", "role": "user", "content": "What is machine learning?"}
]

# First response
response1 = client.responses.create(model="gpt-4.1", input=conversation_history)
print("Assistant:", response1.output_text)

# Append the assistant output objects to history
conversation_history += response1.output

# Add next user message
conversation_history.append({
    "type": "message", "role": "user", "content": "Can you give me an example?"
})

# Second response with full history
response2 = client.responses.create(model="gpt-4.1", input=conversation_history)
print("Assistant:", response2.output_text)
```

### Retrieve a Past Response

```python
response_id = "resp_06fd96309858634e..."
previous_response = client.responses.retrieve(response_id)
print(f"Previous response: {previous_response.output_text}")
```

### Responses API Key Parameters

| Parameter | Type | Description |
|---|---|---|
| `model` | str | Model deployment name |
| `input` | str or list | User's message or full conversation list |
| `instructions` | str | System-level persona/behaviour (replaces system role) |
| `previous_response_id` | str | ID of the prior response — enables stateful conversation |
| `temperature` | float | Randomness 0.0–2.0 (default 1.0) |
| `max_output_tokens` | int | Cap on response length |
| `top_p` | float | Nucleus sampling 0.0–1.0 |
| `stream` | bool | Enable streaming (see Section 5) |

### Using Non-OpenAI Models (Practice04)

Azure AI Foundry can serve models beyond GPT — the Phi family, Mistral, Meta Llama, and others. The API call is identical:

```python
model = "Phi-4-mini-reasoning"   # Microsoft's small reasoning model

response = client.responses.create(
    model=model,
    instructions="You are a helpful AI assistant that answers clearly.",
    input="What are the benefits of small language models?"
)
print(response.output_text)
```

---

## 5. Streaming

### What is Streaming?

Streaming sends the model's response token by token as it is generated, instead of waiting for the complete response. This creates the familiar "typing" effect seen in ChatGPT.

**Benefits:**
- Perceived faster response — user sees output immediately
- Better UX for long responses
- Allows early cancellation if the answer is already sufficient

### How Streaming Works — Event Lifecycle

When `stream=True`, the API returns a sequence of events instead of a single response object.

```
Event 1:  response.created          → response object initialized
Event 2:  response.in_progress      → streaming started
Event 3:  response.output_item.added → message item created
Event 4:  response.content_part.added → text content part opened
Event 5+: response.output_text.delta → incremental text chunks (repeated N times)
Event N:  response.output_text.done  → full text finalized
Event N+1:response.content_part.done → content part closed
Event N+2:response.output_item.done  → message item completed
Event N+3:response.completed         → final response object with usage stats
```

### Basic Streaming (Practice07)

```python
last_response_id = None

stream = client.responses.create(
    model="gpt-4.1",
    input="Write a short story about a robot learning to paint.",
    stream=True,
    previous_response_id=last_response_id
)

for event in stream:
    if event.type == "response.output_text.delta":
        print(event.delta, end="")          # print each chunk, no newline
    elif event.type == "response.completed":
        last_response_id = event.response.id # capture ID for next turn

print()   # final newline to move cursor to next line
```

### Interactive Streaming Loop (Practice03)

```python
last_response_id = None

while True:
    input_text = input('\nEnter a prompt (or type "quit" to exit): ')
    if input_text.lower() == "quit":
        break
    if len(input_text) == 0:
        continue

    stream = client.responses.create(
        model=model_deployment,
        instructions="You are a helpful AI assistant.",
        input=input_text,
        previous_response_id=last_response_id,
        stream=True
    )

    for event in stream:
        if event.type == "response.output_text.delta":
            print(event.delta, end="")
        elif event.type == "response.completed":
            last_response_id = event.response.id

    print()  # newline after each response
```

### Async Streaming (Practice06)

```python
import asyncio
from openai import AsyncOpenAI
from azure.identity.aio import DefaultAzureCredential, get_bearer_token_provider

async def main():
    credential = DefaultAzureCredential()
    token_provider = get_bearer_token_provider(credential, "https://ai.azure.com/.default")
    async_client = AsyncOpenAI(base_url=endpoint, api_key=token_provider)
    last_response_id = None

    while True:
        input_text = input('\nEnter a prompt (or type "quit" to exit): ')
        if input_text.lower() == "quit":
            break

        stream_response = await async_client.responses.create(
            model=model_deployment,
            instructions="You are a helpful AI assistant.",
            input=input_text,
            previous_response_id=last_response_id,
            stream=True
        )

        async for event in stream_response:    # note: async for
            if event.type == "response.output_text.delta":
                print(event.delta, end="")
            elif event.type == "response.completed":
                last_response_id = event.response.id
        print()

    await credential.close()

asyncio.run(main())
```

### Streaming Event Object Properties

```
event.type           → string identifying the event type
event.delta          → the text chunk (on output_text.delta events only)
event.response       → full response object (on response.completed only)
event.response.id    → response ID for chaining
event.sequence_number → order of events (0, 1, 2, ...)
```

### Content Filters in Streaming

Azure applies content filters automatically to both prompt and completion:

```python
# Available in the response.completed event:
event.response.content_filters[1]['content_filter_results']
# Returns: {hate, sexual, violence, self_harm, protected_material_text, protected_material_code}
# Each: {filtered: bool, severity: 'safe'|'low'|'medium'|'high'}
```

---

## 6. Async Programming

### Why Use Async?

Synchronous API calls block the entire Python thread while waiting for the response. In a web server, CLI app, or UI, this freezes everything. Async allows other code to run while the API call is in flight.

```
Sync:  [send request] -------- wait -------- [receive response] → next line
Async: [send request] → [do other things] → [receive response] → next line
```

### Async Single Call (Practice08)

```python
import os
import asyncio
from dotenv import load_dotenv
from openai import AsyncOpenAI
from azure.identity.aio import DefaultAzureCredential, get_bearer_token_provider

async def main():
    load_dotenv()
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    model = os.getenv("MODEL_DEPLOYMENT")

    token = get_bearer_token_provider(DefaultAzureCredential(), "https://ai.azure.com/.default")
    async_client = AsyncOpenAI(base_url=endpoint, api_key=token)

    response = await async_client.responses.create(   # await the coroutine
        model="gpt-4.1",
        input="Explain quantum computing briefly."
    )
    print(response.output_text)

if __name__ == '__main__':
    asyncio.run(main())   # entry point for async programs
```

### Async Interactive Loop with State (Practice04)

```python
async def main():
    credential = DefaultAzureCredential()
    token_provider = get_bearer_token_provider(credential, "https://ai.azure.com/.default")
    async_client = AsyncOpenAI(base_url=endpoint, api_key=token_provider)
    last_response_id = None

    while True:
        input_text = input('\nEnter a prompt (or type "quit" to exit): ')
        if input_text.lower() == "quit":
            break
        if len(input_text) == 0:
            print("Please enter a prompt.")
            continue

        response = await async_client.responses.create(
            model=model_deployment,
            instructions="You are a helpful AI assistant.",
            input=input_text,
            previous_response_id=last_response_id
        )
        print("Assistant:", response.output_text)
        last_response_id = response.id

    await credential.close()   # important — clean up the async session

asyncio.run(main())
```

### Async vs Sync Comparison

| Aspect | Sync (`OpenAI`) | Async (`AsyncOpenAI`) |
|---|---|---|
| Import | `from openai import OpenAI` | `from openai import AsyncOpenAI` |
| Credential | `from azure.identity import ...` | `from azure.identity.aio import ...` |
| API call | `response = client.responses.create(...)` | `response = await client.responses.create(...)` |
| Stream iteration | `for event in stream` | `async for event in stream` |
| Entry point | Normal function call | `asyncio.run(main())` |
| Credential cleanup | Not needed | `await credential.close()` |
| Use case | Scripts, simple CLI | Web apps, concurrent tasks, production |

### Common Async Mistakes

```python
# WRONG — missing await returns coroutine object, not response
response = async_client.responses.create(model=model, input="Hello")
print(response.output_text)   # AttributeError: coroutine object has no attribute output_text

# CORRECT
response = await async_client.responses.create(model=model, input="Hello")
print(response.output_text)   # works

# WRONG — using sync credential in async context
from azure.identity import DefaultAzureCredential      # sync version
# CORRECT
from azure.identity.aio import DefaultAzureCredential  # async version (.aio)
```

---

## 7. Azure AI Foundry SDK — AIProjectClient

### What is AIProjectClient?

`AIProjectClient` is the main client in the `azure-ai-projects` package. Unlike the raw OpenAI client, it connects to your entire Azure AI Foundry **project environment** and provides:

- OpenAI-compatible inference client
- Agent management (create, run, manage threads)
- Connection listing (linked Azure services)
- Evaluation capabilities
- Model routing to any model in your project catalog

### Installation

```bash
pip install azure-ai-projects
pip install azure-ai-projects==1.0.0b12   # specific version for beta features
```

### Initializing AIProjectClient (Practice02, Practice11)

```python
import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

load_dotenv()
project_endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")

project_client = AIProjectClient(
    endpoint=project_endpoint,
    credential=DefaultAzureCredential()
)
```

The `FOUNDRY_PROJECT_ENDPOINT` format is:
```
https://<resource-name>.services.ai.azure.com/api/projects/<project-name>
```

### Getting an OpenAI-Compatible Client (Practice11)

```python
# Derive an authenticated OpenAI client from the project client
openai_client = project_client.get_openai_client()

# Use it exactly like a regular OpenAI client
response = openai_client.chat.completions.create(
    model=model,
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user",   "content": "What is Azure AI?"}
    ]
)
print(response.choices[0].message.content)
```

### Listing Project Connections (Practice02)

```python
# List all services connected to your project
connections = project_client.connections.list()

for conn in connections:
    print(f"Name:     {conn.name}")
    print(f"Type:     {conn.type}")
    print(f"Endpoint: {conn.endpoint_url if hasattr(conn, 'endpoint_url') else 'N/A'}")
    print("-" * 40)
```

Typical connection types: `AzureOpenAI`, `AzureAISearch`, `AzureBlob`, `AzureContentSafety`

### Direct Responses API via Foundry SDK (Practice02)

```python
openai_client = project_client.get_openai_client()

response = openai_client.responses.create(
    model="gpt-4.1",
    input="What is quantum computing?",
    max_output_tokens=500
)
print(response.output_text)
```

---

## 8. AI Agents

### What is an AI Agent?

An AI Agent is an autonomous AI entity that can:
- Follow custom instructions
- Use tools (code interpreter, file search, custom functions)
- Maintain persistent conversations via threads
- Execute multi-step tasks

### Agent Concepts

| Concept | Description | Analogy |
|---|---|---|
| **Agent** | The AI entity with instructions and tools | An employee with a job description |
| **Thread** | A persistent conversation session | A Slack channel |
| **Message** | A single user or assistant turn in a thread | A Slack message |
| **Run** | One execution of the agent against a thread | The agent reading and responding |

### Agent Lifecycle

```
1. Create Agent  → defines WHO the agent is (instructions, tools, model)
2. Create Thread → creates WHERE the conversation happens
3. Add Message   → adds WHAT the user said
4. Create Run    → tells the agent to READ and RESPOND
5. Poll Run      → wait for status = "completed"
6. List Messages → retrieve WHAT the agent replied
```

### Complete Agent Flow (Practice12)

```python
import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

def main():
    load_dotenv()
    project_endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
    model_deployment = os.getenv("MODEL_DEPLOYMENT")

    # 1. Initialize Foundry project client
    project_client = AIProjectClient(
        endpoint=project_endpoint,
        credential=DefaultAzureCredential()
    )

    # 2. Create the agent
    print("Creating agent...")
    agent = project_client.agents.create_agent(
        model=model_deployment,
        name="Foundry-Syncronous-Agent",
        instructions="You are a helpful assistant that provides concise and accurate answers."
    )
    print(f"Agent created with ID: {agent.id}")

    # 3. Create a conversation thread
    print("Creating thread...")
    thread = project_client.agents.threads.create()
    print(f"Thread ID: {thread.id}")

    # 4. Add a user message to the thread
    print("Sending message...")
    project_client.agents.messages.create(
        thread_id=thread.id,
        role="user",
        content="What is Azure OpenAI projects?"
    )

    # 5. Execute the agent (create run + poll until complete)
    print("Processing...")
    run = project_client.agents.runs.create_and_process(
        thread_id=thread.id,
        agent_id=agent.id
    )
    print(f"Run status: {run.status}")

    # 6. Retrieve the assistant's reply
    messages = project_client.agents.messages.list(thread_id=thread.id)
    for message in messages:
        if message.role == "assistant":
            print("\n--- Agent Response ---")
            print(message.content[0].text.value)
            break

if __name__ == "__main__":
    main()
```

### Interactive Agent Chat with Manual Polling (Practice14)

For more control, you can create the run and poll manually:

```python
import os
import time
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

endpoint = "https://<resource>.services.ai.azure.com/api/projects/<project>"
project_client = AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())

# Fetch an existing named agent
agent = project_client.agents.get_agent(assistant_id="Foundry-Syncronous-Agent1")

# Create a thread for this session
thread = project_client.agents.create_thread()
print(f"Thread ID: {thread.id}")

while True:
    input_text = input('\nEnter a prompt (or type "quit" to exit): ')
    if input_text.lower() == "quit":
        break
    if len(input_text.strip()) == 0:
        continue

    # Add user message
    project_client.agents.create_message(
        thread_id=thread.id,
        role="user",
        content=input_text
    )

    # Create run
    run = project_client.agents.create_run(
        thread_id=thread.id,
        assistant_id=agent.id
    )

    # Poll until complete
    while run.status in ["queued", "in_progress"]:
        time.sleep(1)
        run = project_client.agents.get_run(
            thread_id=thread.id,
            run_id=run.id
        )

    # Retrieve response
    if run.status == "completed":
        messages = project_client.agents.list_messages(thread_id=thread.id)
        latest = messages.data[0]   # most recent message first
        if latest.role == "assistant":
            for block in latest.content:
                if block.type == "text":
                    print(f"\nAgent: {block.text.value}")
    else:
        print(f"\nRun ended with status: {run.status}")
```

### Run Status Values

| Status | Meaning |
|---|---|
| `queued` | Run created, waiting to start |
| `in_progress` | Agent is actively processing |
| `completed` | Successfully finished — retrieve messages |
| `failed` | An error occurred |
| `cancelled` | Run was cancelled |
| `expired` | Run timed out |

### create_and_process() vs create_run() + poll

| Method | Behaviour | When to Use |
|---|---|---|
| `create_and_process()` | Creates run + blocks until complete | Simple scripts, synchronous workflows |
| `create_run()` + poll loop | Manual control over polling | Interactive apps, custom timeout logic |

---

## 9. Calling Existing Agents

### Method 1 — Via Responses API with agent_reference (Practice13)

If you have already created an agent in Azure AI Foundry portal or via SDK, you can call it through the Responses API using `extra_body`:

```python
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

endpoint = "https://<resource>.services.ai.azure.com/api/projects/<project>"
project_client = AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())

openai_client = project_client.get_openai_client()

response = openai_client.responses.create(
    input=[{"role": "user", "content": "What is quantum computing?"}],
    extra_body={
        "agent_reference": {
            "name": "Foundry-Syncronous-Agent1",
            "version": "1",
            "type": "agent_reference"
        }
    }
)
print(f"Response: {response.output_text}")
```

### Method 2 — Native SDK Agents API (Practice14)

Full thread-based interaction using the native agents SDK (shown in Section 8 above). This approach gives you access to thread history, run details, and message pagination.

---

## 10. API Comparison — Quick Reference

### ChatCompletions vs Responses API

| Feature | ChatCompletions API | Responses API |
|---|---|---|
| Method | `chat.completions.create()` | `responses.create()` |
| State | Stateless | Stateful |
| History | Manual — pass full `messages[]` | Automatic — `previous_response_id` |
| System message | `{"role": "system", "content": "..."}` | `instructions="..."` parameter |
| Response text | `completion.choices[0].message.content` | `response.output_text` |
| Response ID | Not available | `response.id` |
| Token usage | `completion.usage.total_tokens` | `response.usage.total_tokens` |
| Streaming | Via `stream=True` + `for chunk in ...` | Via `stream=True` + event types |
| Best for | Standard OpenAI-compatible apps | New Azure AI Foundry apps |

### All APIs at a Glance

```python
# 1. ChatCompletions — stateless
completion = client.chat.completions.create(model=model, messages=[...])
text = completion.choices[0].message.content

# 2. Responses API — stateful
response = client.responses.create(model=model, input="...", instructions="...",
                                   previous_response_id=last_id)
text = response.output_text

# 3. Streaming Responses
stream = client.responses.create(model=model, input="...", stream=True)
for event in stream:
    if event.type == "response.output_text.delta":
        print(event.delta, end="")

# 4. Async Responses
response = await async_client.responses.create(model=model, input="...")
text = response.output_text

# 5. Async Streaming
stream = await async_client.responses.create(model=model, input="...", stream=True)
async for event in stream:
    if event.type == "response.output_text.delta":
        print(event.delta, end="")

# 6. AIProjectClient → OpenAI client
project_client = AIProjectClient(endpoint=..., credential=DefaultAzureCredential())
openai_client = project_client.get_openai_client()
response = openai_client.chat.completions.create(model=model, messages=[...])

# 7. Agents — full flow
agent  = project_client.agents.create_agent(model=model, name="...", instructions="...")
thread = project_client.agents.threads.create()
project_client.agents.messages.create(thread_id=thread.id, role="user", content="...")
run    = project_client.agents.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
msgs   = project_client.agents.messages.list(thread_id=thread.id)
```

---

## 11. Environment Setup

### .env File Structure

```env
AZURE_OPENAI_ENDPOINT=https://<resource>.openai.azure.com/openai/deployments/<deployment>/
MODEL_DEPLOYMENT=gpt-4.1
FOUNDRY_PROJECT_ENDPOINT=https://<resource>.services.ai.azure.com/api/projects/<project-name>
```

### Loading Environment Variables

```python
from dotenv import load_dotenv
import os

load_dotenv()   # reads .env file in current directory

endpoint   = os.getenv("AZURE_OPENAI_ENDPOINT")
model      = os.getenv("MODEL_DEPLOYMENT")
project_ep = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
```

### Required Python Packages

```bash
pip install openai
pip install azure-identity
pip install azure-ai-projects
pip install python-dotenv

# Specific version for beta agent features
pip install azure-ai-projects==1.0.0b12
```

### Standard Boilerplate Template

```python
import os
from dotenv import load_dotenv
from openai import OpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

def main():
    os.system('cls' if os.name == 'nt' else 'clear')   # clear console

    try:
        load_dotenv()
        endpoint         = os.getenv("AZURE_OPENAI_ENDPOINT")
        model_deployment = os.getenv("MODEL_DEPLOYMENT")

        token_provider = get_bearer_token_provider(
            DefaultAzureCredential(), "https://ai.azure.com/.default"
        )
        client = OpenAI(base_url=endpoint, api_key=token_provider)

        # --- your code here ---

    except Exception as ex:
        print(ex)

if __name__ == '__main__':
    main()
```

---

## 12. Common Errors & Fixes

### Error: `AttributeError: 'coroutine' object has no attribute 'output_text'`

```python
# Cause: missing await on async call
response = async_client.responses.create(...)   # WRONG

# Fix: add await
response = await async_client.responses.create(...)   # CORRECT
```

### Error: `TypeError: object is not callable` on api_key

```python
# Cause: called token_provider() instead of passing the callable
client = OpenAI(base_url=endpoint, api_key=token_provider())   # WRONG — string result

# Fix: pass the callable
client = OpenAI(base_url=endpoint, api_key=token_provider)     # CORRECT — callable
```

### Error: `AuthenticationError` or 401

```python
# Cause 1: Wrong scope
token_provider = get_bearer_token_provider(DefaultAzureCredential(),
    "https://cognitiveservices.azure.com/.default")   # old scope — may not work

# Fix: use AI Foundry scope
token_provider = get_bearer_token_provider(DefaultAzureCredential(),
    "https://ai.azure.com/.default")

# Cause 2: Not logged into Azure CLI
# Fix:
# az login
# az account set --subscription <subscription-id>
```

### Error: Using sync credential in async context

```python
# WRONG — sync credential imported in async code
from azure.identity import DefaultAzureCredential      # sync

# CORRECT — use the .aio submodule
from azure.identity.aio import DefaultAzureCredential  # async
```

### Error: `ResourceNotFoundError` on agent ID

```python
# Cause: passing agent name instead of agent ID
agent = project_client.agents.get_agent(assistant_id="Foundry-Agent-Name")   # may fail

# Fix: pass the actual agent.id (UUID string)
agent = project_client.agents.get_agent(assistant_id="asst_abc123xyz...")
```

### Error: Stream events printing on separate lines

```python
# Cause: using print(event.delta) — adds newline after each chunk
print(event.delta)          # WRONG — adds newline

# Fix: suppress newline with end=""
print(event.delta, end="")  # CORRECT — streams on same line

# Also add bare print() after the loop to end the line
print()
```

---

## Summary — The Mental Model

```
┌─────────────────────────────────────────────────────────────────┐
│                    AZURE AI FOUNDRY                             │
│                                                                 │
│  ┌──────────────┐    ┌──────────────────┐    ┌──────────────┐  │
│  │  ChatComp.   │    │  Responses API   │    │  AI Agents   │  │
│  │  API         │    │                  │    │              │  │
│  │  stateless   │    │  stateful        │    │  autonomous  │  │
│  │  manual hist │    │  auto history    │    │  thread-based│  │
│  │  messages[]  │    │  prev_resp_id    │    │  create_run  │  │
│  └──────────────┘    └──────────────────┘    └──────────────┘  │
│         ↕                    ↕                      ↕          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Authentication Layer                        │   │
│  │  DefaultAzureCredential + get_bearer_token_provider      │   │
│  │  Scope: https://ai.azure.com/.default                    │   │
│  └──────────────────────────────────────────────────────────┘   │
│         ↕                    ↕                      ↕          │
│  ┌────────────┐    ┌──────────────────┐    ┌──────────────┐    │
│  │  OpenAI    │    │  AsyncOpenAI     │    │AIProjectClient│    │
│  │  sync      │    │  + asyncio       │    │  Foundry SDK  │    │
│  └────────────┘    └──────────────────┘    └──────────────┘    │
└─────────────────────────────────────────────────────────────────┘

Key Rules:
  • Responses API   → preferred for NEW apps → use previous_response_id
  • ChatCompletions → widely compatible   → manage messages[] yourself
  • Streaming       → stream=True + handle response.output_text.delta
  • Async           → AsyncOpenAI + azure.identity.aio + await + asyncio.run()
  • Agents          → thread → message → run → poll → list messages
  • Auth            → NEVER hardcode keys → DefaultAzureCredential always
```

---

*AI-103 Azure AI Engineer Certification — Personal Study Reference*
*Module: Develop a Generative AI Chat App with Microsoft Foundry*
*Practices: 01 through 14 | Azure AI Foundry SDK | GPT-4.1 | Phi-4*
