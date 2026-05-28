# LinkedIn Post — Azure AI Foundry (AI-103 Journey)

---

🚀 **Just completed hands-on practice with Azure AI Foundry — and it genuinely changed how I think about building AI apps!**

As part of my **AI-103: Microsoft Azure AI Engineer** certification journey, I worked through the **"Develop a Generative AI Chat App with Microsoft Foundry"** module on MS Learn — and instead of just reading, I wrote **14 practice programs** from scratch to make every concept stick.

Here's what I built and learned 👇

---

## 🔑 The 5 Big Concepts I Practiced (with real code)

### 1️⃣ ChatCompletions API — The Classic Way
The foundation. Send a `system` role message to set the AI's persona, then a `user` message with the question. Get a response from `completion.choices[0].message.content`. Simple, stateless, and reliable.

```python
completion = openai_client.chat.completions.create(
    model=model_deployment,
    messages=[
        {"role": "system", "content": "You are a helpful AI assistant."},
        {"role": "user", "content": input_text}
    ]
)
```

---

### 2️⃣ Responses API — Azure's Smarter Approach
This is where things got interesting. Unlike ChatCompletions, the **Responses API is stateful** — it tracks conversation history server-side via `previous_response_id`. No more manually managing message arrays!

```python
response = client.responses.create(
    model="gpt-4.1",
    instructions="You are a helpful AI assistant.",
    input=input_text,
    previous_response_id=last_response_id   # ← magic line
)
last_response_id = response.id
```

---

### 3️⃣ Streaming — Real-time Token-by-Token Output
Instead of waiting for the full response, streaming lets you print each word as it arrives — just like ChatGPT's typing effect. The key is handling `response.output_text.delta` events in a loop.

```python
stream = client.responses.create(
    model="gpt-4.1",
    input=input_text,
    stream=True
)
for event in stream:
    if event.type == "response.output_text.delta":
        print(event.delta, end="")   # word by word, no newline
    elif event.type == "response.completed":
        last_response_id = event.response.id
```

---

### 4️⃣ Async + Streaming — Non-blocking Production Pattern
For real applications, blocking the main thread is not acceptable. I combined `AsyncOpenAI` with `async for` to handle streaming responses without freezing the app.

```python
stream_response = await async_client.responses.create(
    model="gpt-4.1",
    input=input_text,
    stream=True
)
async for event in stream_response:
    if event.type == "response.output_text.delta":
        print(event.delta, end="")
```

---

### 5️⃣ AI Agents via Azure AI Foundry SDK — The Real Power
This was the most exciting part. Using `azure-ai-projects`, I created persistent **AI Agents** in Azure AI Foundry and called them programmatically — complete with thread management and run polling.

```python
# Create agent
agent = project_client.agents.create_agent(
    model=model_deployment,
    name="Foundry-Syncronous-Agent",
    instructions="You are a helpful assistant."
)
# Create thread and send message
thread = project_client.agents.threads.create()
project_client.agents.messages.create(
    thread_id=thread.id, role="user", content="What is Azure OpenAI?"
)
# Run and collect response
run = project_client.agents.runs.create_and_process(
    thread_id=thread.id, agent_id=agent.id
)
```

---

## 📊 The Full Learning Path — 14 Practices in Order

| # | Practice File | Key Concept |
|---|---|---|
| 01 | Chat App — Self Practice | ChatCompletions API basics |
| 02 | Foundry SDK Test | `AIProjectClient` + listing connections |
| 03 | Responses API Sample | `responses.create()` with parameters |
| 04 | Foundry Direct Models | Using non-OpenAI models (e.g. Phi-4) |
| 05 | Conversational Experience | Multi-turn via `previous_response_id` |
| 06 | Manual Conversation Chaining | Building history array manually |
| 07 | Streaming Chat | `stream=True` + delta event handling |
| 08 | Async Responses API | `AsyncOpenAI` + `await` |
| 09 | ChatCompletion API Demo | Single-turn completion demo |
| 10 | Retaining Context | Manual message history with ChatCompletions |
| 11 | Foundry SDK Usage | `AIProjectClient` → `get_openai_client()` |
| 12 | Agent Creation | Creating agents via Foundry SDK `1.0.0b12` |
| 13 | Call Existing Agent | `agent_reference` via Responses API |
| 14 | Interactive Agent Chat | Full polling loop with thread management |

---

## 💡 Key Lessons Learned

**Responses API vs ChatCompletions API:**
- ChatCompletions = stateless, you manage history yourself
- Responses API = stateful, Azure manages history via `previous_response_id`
- Responses API is the preferred choice for new Azure AI Foundry apps

**Authentication — always use DefaultAzureCredential:**
```python
token_provider = get_bearer_token_provider(
    DefaultAzureCredential(), "https://ai.azure.com/.default"
)
client = OpenAI(base_url=endpoint, api_key=token_provider)
```
No hardcoded keys. Ever.

**Streaming event lifecycle (9 stages):**
`response.created` → `response.in_progress` → `output_item.added` → `content_part.added` → `output_text.delta` (×N) → `output_text.done` → `content_part.done` → `output_item.done` → `response.completed`

**AI Agents = threads + runs + messages:**
- Thread = a persistent conversation session
- Run = one execution of the agent against the thread
- Poll `run.status` until `"completed"`

---

## 🛠️ Tech Stack Used

`Python` · `Azure OpenAI` · `Azure AI Foundry` · `azure-ai-projects SDK` · `DefaultAzureCredential` · `AsyncOpenAI` · `GPT-4.1` · `Phi-4-mini-reasoning`

---

## 🎯 What's Next

Continuing toward **AI-103 certification** with:
- RAG (Retrieval Augmented Generation) with Azure AI Search
- Function calling and tool use in agents
- Multi-agent orchestration patterns
- LangGraph + Azure AI integration

---

If you're on the AI Engineer path or just exploring Azure AI Foundry — drop a comment or connect. Happy to share notes and code!

**#AzureAI #AI103 #MicrosoftAzure #AzureOpenAI #GenerativeAI #AIEngineering #Python #AzureAIFoundry #MachineLearning #CloudAI #MicrosoftLearn #AIArchitect #LearningInPublic #100DaysOfCode**
