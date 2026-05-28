# AI-103 — Azure AI Foundry Practice Questions
### Based on 14 Lab Practices | 50 Questions with Answers & Explanations

---

## Topic 1: ChatCompletions API
> Practices covered: 01, 09, 10, 11

---

**Q1.** In ChatCompletions API, which role sets the AI's persona and behaviour?

- A) user
- B) assistant
- C) **system ✅**
- D) developer

> **Explanation:** The `system` role message defines the AI's behaviour, tone, and persona. It is typically the first message in the messages array.

---

**Q2.** What property contains the model's reply in a ChatCompletions response?

- A) response.output_text
- B) **completion.choices[0].message.content ✅**
- C) completion.text
- D) response.content

> **Explanation:** `completion.choices[0].message.content` holds the assistant's reply text in the ChatCompletions API.

---

**Q3.** Which client class is used for synchronous ChatCompletions in the OpenAI SDK?

- A) AsyncOpenAI
- B) **OpenAI ✅**
- C) AzureOpenAI
- D) AIProjectClient

> **Explanation:** The synchronous `OpenAI` client is used. `AsyncOpenAI` is used for async operations.

---

**Q4.** In ChatCompletions, how do you manually retain conversation context across turns?

- A) Use previous_response_id
- B) Use session_id
- C) **Append messages to the messages array ✅**
- D) Use store=True

> **Explanation:** ChatCompletions is stateless. You must manually append each user and assistant message to the messages array before each API call.

---

**Q5.** Which import provides Azure AD token authentication for the OpenAI client?

- A) from azure.identity import AzureKeyCredential
- B) **from azure.identity import get_bearer_token_provider ✅**
- C) from azure.auth import TokenProvider
- D) from openai import TokenCredential

> **Explanation:** `get_bearer_token_provider` from `azure.identity` creates a callable token provider used as the `api_key` parameter.

---

**Q6.** When creating an OpenAI client pointing to Azure, which parameter specifies the Azure endpoint?

- A) endpoint
- B) api_base
- C) **base_url ✅**
- D) azure_endpoint

> **Explanation:** The OpenAI client uses `base_url` to point to Azure's endpoint. `api_base` is a legacy parameter.

---

**Q7.** What is the correct order of roles in a typical ChatCompletions messages array?

- A) user → system → assistant
- B) assistant → user → system
- C) **system → user → assistant ✅**
- D) system → assistant → user

> **Explanation:** Convention is system first to set context, then user question, then assistant reply. This pattern repeats for multi-turn conversations.

---

**Q8.** ChatCompletions API is described as "stateless". What does this mean?

- A) It cannot handle async requests
- B) **It does not remember previous turns automatically ✅**
- C) It does not support streaming
- D) It cannot use system messages

> **Explanation:** Stateless means each API call is independent. The model has no memory of prior turns unless you include previous messages in the messages array.

---

**Q9.** In Practice10, why is the assistant message appended back to conversation_messages?

- A) To count tokens used
- B) **To maintain context for the next turn ✅**
- C) To enable streaming
- D) To set the model temperature

> **Explanation:** Appending the assistant's reply keeps the conversation history intact so the model can reference prior turns in subsequent calls.

---

**Q10.** Which Azure scope is used with get_bearer_token_provider for AI Foundry endpoints?

- A) https://cognitiveservices.azure.com/.default
- B) https://openai.azure.com/.default
- C) **https://ai.azure.com/.default ✅**
- D) https://management.azure.com/.default

> **Explanation:** The scope `https://ai.azure.com/.default` is used for Azure AI Foundry endpoints in recent practices. Some older labs use `cognitiveservices.azure.com/.default`.

---

## Topic 2: Responses API
> Practices covered: 02, 03, 05, 06

---

**Q11.** What parameter in the Responses API replaces manually passing conversation history?

- A) session_id
- B) conversation_id
- C) **previous_response_id ✅**
- D) thread_id

> **Explanation:** `previous_response_id` links responses together server-side, so Azure manages conversation history automatically without you building a messages array.

---

**Q12.** Which method is called to create a response using the Responses API?

- A) client.chat.completions.create()
- B) **client.responses.create() ✅**
- C) client.completions.generate()
- D) client.responses.send()

> **Explanation:** `client.responses.create()` is the Responses API method, distinct from `client.chat.completions.create()` used in ChatCompletions.

---

**Q13.** In the Responses API, which parameter sets the AI's behaviour (equivalent to the system role)?

- A) system
- B) persona
- C) **instructions ✅**
- D) context

> **Explanation:** The `instructions` parameter in `responses.create()` sets the AI's persona and behaviour, equivalent to the system role message in ChatCompletions.

---

**Q14.** What property holds the text output of a Responses API response?

- A) response.choices[0].text
- B) response.content
- C) **response.output_text ✅**
- D) response.message.content

> **Explanation:** `response.output_text` is the convenient property that returns the assistant's text directly from a Responses API response object.

---

**Q15.** In Practice05, how is the second turn of a conversation linked to the first?

- A) By passing the same thread_id
- B) **By passing response1.id as previous_response_id ✅**
- C) By including the full message history
- D) By using session_id=response1.session

> **Explanation:** `response2` passes `previous_response_id=response1.id`, which tells Azure to build on the context of the first response.

---

**Q16.** What does response.usage.total_tokens represent?

- A) Output tokens only
- B) Input tokens only
- C) **Combined input + output tokens ✅**
- D) Cached tokens

> **Explanation:** `total_tokens = input_tokens + output_tokens`. It represents the total token consumption for that API call.

---

**Q17.** In Practice06, what does `conversation_history += response1.output` do?

- A) Adds the assistant message string to history
- B) **Appends the structured output objects from the response to the history list ✅**
- C) Stores the response ID
- D) Converts history to JSON

> **Explanation:** `response1.output` returns a list of output objects. Using `+=` appends them to `conversation_history`, building a manual history without `previous_response_id`.

---

**Q18.** Which method retrieves a previously stored response by its ID?

- A) client.responses.get()
- B) client.responses.fetch()
- C) **client.responses.retrieve() ✅**
- D) client.responses.load()

> **Explanation:** `client.responses.retrieve(response_id)` fetches a stored response object from Azure using its unique ID.

---

**Q19.** The Responses API is described as "stateful". What advantage does this provide?

- A) Faster response times
- B) **Server-side conversation history — no manual tracking needed ✅**
- C) Support for more models
- D) Lower token costs

> **Explanation:** Stateful means Azure stores conversation history server-side. You only pass `previous_response_id`, making code cleaner and reducing payload size.

---

**Q20.** Which parameter controls output length in the Responses API?

- A) max_tokens
- B) max_length
- C) **max_output_tokens ✅**
- D) output_limit

> **Explanation:** `max_output_tokens` controls the maximum number of tokens in the response output. The ChatCompletions equivalent is `max_tokens`.

---

## Topic 3: Streaming
> Practices covered: 03, 06, 07

---

**Q21.** Which parameter enables streaming in responses.create()?

- A) async=True
- B) **stream=True ✅**
- C) realtime=True
- D) delta=True

> **Explanation:** Setting `stream=True` in `responses.create()` switches from a single blocking response to a stream of incremental events.

---

**Q22.** Which event type carries the incremental text in a streaming response?

- A) response.output_text.chunk
- B) response.delta
- C) **response.output_text.delta ✅**
- D) response.text.update

> **Explanation:** `response.output_text.delta` events carry each incremental text chunk. Access the text via `event.delta`.

---

**Q23.** Why is `print(event.delta, end='')` used instead of `print(event.delta)` in streaming?

- A) To avoid encoding errors
- B) **To suppress the newline so words print on the same line as they arrive ✅**
- C) To improve performance
- D) To buffer output

> **Explanation:** `end=''` suppresses Python's default newline after each print, creating the continuous typing effect as each delta chunk arrives.

---

**Q24.** In Practice07, when is last_response_id updated?

- A) At response.output_text.delta
- B) At response.created
- C) **At response.completed ✅**
- D) At response.output_item.added

> **Explanation:** `last_response_id = event.response.id` is set when the `response.completed` event fires, ensuring you capture the final response ID for chaining.

---

**Q25.** What is the first event in the streaming lifecycle?

- A) response.in_progress
- B) response.output_item.added
- C) **response.created ✅**
- D) response.content_part.added

> **Explanation:** `response.created` is the first event, fired when the response object is initialized on the server before any content is streamed.

---

**Q26.** How many distinct event types appear in a complete streaming lifecycle (from Practice07 output)?

- A) 5
- B) 7
- C) **9 ✅**
- D) 12

> **Explanation:** 9 distinct event types: `created`, `in_progress`, `output_item.added`, `content_part.added`, `output_text.delta` (×N), `output_text.done`, `content_part.done`, `output_item.done`, `completed`.

---

**Q27.** In Practice06 async streaming, which loop iterates over the stream?

- A) for event in stream
- B) await for event in stream
- C) **async for event in stream_response ✅**
- D) foreach event in stream

> **Explanation:** `async for event in stream_response` is used with `AsyncOpenAI` to asynchronously iterate over streaming events without blocking.

---

**Q28.** What is the obfuscation field seen on each streaming delta event?

- A) An error code
- B) **An Azure-specific watermarking identifier per token chunk ✅**
- C) A compression key
- D) A debug identifier

> **Explanation:** The `obfuscation` field is an Azure-specific token-level identifier. It appears on each delta event and is used internally for content tracing and watermarking.

---

**Q29.** What does the bare `print()` after the stream loop do and why is it important?

- A) print('Done') — to signal completion
- B) **print() — to output a final newline after all delta chunks ✅**
- C) print(last_response_id) — to log the ID
- D) print(stream.status) — to confirm success

> **Explanation:** A bare `print()` after the loop outputs a newline character, moving the cursor to the next line cleanly after all delta chunks have printed on the same line.

---

**Q30.** Which content filter category appeared at "low" severity in the Practice07 streaming output?

- A) violence
- B) hate
- C) **sexual ✅**
- D) self_harm

> **Explanation:** The `content_filter_results` in the Practice07 completed response showed `sexual` content filtered as `low` severity (not blocked). All other categories were `safe`.

---

## Topic 4: Async & Authentication
> Practices covered: 04, 06, 08

---

**Q31.** Which import is needed to use async OpenAI calls?

- A) from openai import OpenAI
- B) **from openai import AsyncOpenAI ✅**
- C) from openai.async import OpenAI
- D) import asyncio.openai

> **Explanation:** `AsyncOpenAI` from the `openai` package provides the async client. Regular `OpenAI` is synchronous only.

---

**Q32.** Which import provides the async version of DefaultAzureCredential?

- A) from azure.identity import DefaultAzureCredential
- B) **from azure.identity.aio import DefaultAzureCredential ✅**
- C) from azure.identity.async import DefaultAzureCredential
- D) from azure.aio import DefaultAzureCredential

> **Explanation:** The async version lives in `azure.identity.aio` — note the `.aio` submodule. The synchronous version is in `azure.identity` directly.

---

**Q33.** Why must `credential.close()` be awaited in `finally` in async programs?

- A) To save tokens
- B) To flush logs
- C) **To properly close the async HTTP session and release resources ✅**
- D) To commit the response to storage

> **Explanation:** `AsyncDefaultAzureCredential` maintains an HTTP session. Awaiting `credential.close()` in `finally` ensures the session is properly closed even if an exception occurs.

---

**Q34.** What does `asyncio.run(main())` do?

- A) Runs main() in a background thread
- B) **Creates an event loop and runs the async main coroutine to completion ✅**
- C) Imports async dependencies
- D) Schedules main() for later execution

> **Explanation:** `asyncio.run()` is the entry point for async programs. It creates a new event loop, runs the coroutine, and closes the loop when done.

---

**Q35.** In DefaultAzureCredential, what authentication methods does it try automatically?

- A) Only environment variables
- B) Only Managed Identity
- C) **Environment variables, Workload Identity, Managed Identity, Azure CLI, and more in sequence ✅**
- D) Only Service Principal

> **Explanation:** `DefaultAzureCredential` tries multiple methods in order: environment variables, workload identity, managed identity, Azure CLI, Visual Studio Code, and others — whichever succeeds first.

---

**Q36.** Why is get_bearer_token_provider preferred over hardcoded API keys?

- A) It is faster
- B) **It provides rotating, short-lived tokens using Azure AD — no secret stored in code ✅**
- C) It supports more models
- D) It reduces latency

> **Explanation:** Bearer tokens from Azure AD are short-lived and auto-rotating. No secret is hardcoded in code or config files, making it enterprise-safe and compliant.

---

**Q37.** In async streaming (Practice06), what keyword combination iterates over stream events?

- A) for event in await stream
- B) **async for event in stream_response ✅**
- C) await for event in stream
- D) for await event in stream_response

> **Explanation:** `async for event in stream_response` is the correct Python async iteration syntax for iterating over an async generator like a streaming response.

---

**Q38.** What is the key difference between synchronous and asynchronous API calls in a chat app?

- A) Sync is faster
- B) **Async allows other code to run while waiting for the API response, preventing UI freeze ✅**
- C) Async uses less memory
- D) Sync supports streaming, async does not

> **Explanation:** Async (non-blocking) calls allow the event loop to handle other tasks while waiting for the API. Sync calls block the entire thread until the response arrives.

---

**Q39.** Which scope is used for authenticating to Azure Cognitive Services endpoints (as seen in Practice01)?

- A) https://ai.azure.com/.default
- B) **https://cognitiveservices.azure.com/.default ✅**
- C) https://openai.azure.com/.default
- D) https://management.azure.com/.default

> **Explanation:** `https://cognitiveservices.azure.com/.default` is used for Azure Cognitive Services endpoints. Newer AI Foundry endpoints use `https://ai.azure.com/.default`.

---

**Q40.** What is the minimum correct pattern for a single async Responses API call?

- A) response = async_client.responses.create(...)
- B) **response = await async_client.responses.create(...) ✅**
- C) async response = async_client.responses.create(...)
- D) response = asyncio.call(async_client.responses.create(...))

> **Explanation:** `await` is required before `async_client.responses.create()` to pause execution until the response is ready. Missing `await` returns a coroutine object, not a response.

---

## Topic 5: AI Agents & Foundry SDK
> Practices covered: 02, 04, 12, 13, 14

---

**Q41.** Which package provides the AIProjectClient?

- A) azure-openai
- B) openai
- C) **azure-ai-projects ✅**
- D) azure-cognitiveservices-openai

> **Explanation:** `azure-ai-projects` is the package that provides `AIProjectClient`, the main entry point for the Azure AI Foundry SDK.

---

**Q42.** In Practice12, what does project_client.agents.create_agent() return?

- A) A thread object
- B) **An agent object with an ID ✅**
- C) A run object
- D) A message object

> **Explanation:** `create_agent()` returns an agent object. The most important property is `agent.id`, which is used when creating runs.

---

**Q43.** What is a "thread" in the context of AI Agents?

- A) A CPU execution thread
- B) **A persistent conversation session that holds messages and runs ✅**
- C) A background task
- D) A token stream

> **Explanation:** A thread is a persistent conversation container. Messages are added to it, and runs execute the agent against those messages. One thread can hold many turns.

---

**Q44.** What does create_and_process() do in the agents SDK?

- A) Creates an agent and immediately runs it
- B) **Creates a run and polls until it completes — blocking ✅**
- C) Creates a thread and sends a message
- D) Streams the agent's response

> **Explanation:** `create_and_process()` creates a run and waits synchronously for it to complete, combining `create_run` + polling in one convenient call.

---

**Q45.** In Practice14, why is there a while loop checking run.status?

- A) To retry failed runs
- B) **To poll until the run status changes from 'queued' or 'in_progress' to 'completed' ✅**
- C) To handle streaming
- D) To count tokens used

> **Explanation:** Runs are asynchronous. The polling loop calls `get_run()` every second until status is no longer `queued` or `in_progress`, indicating the agent has finished.

---

**Q46.** How do you get an OpenAI-compatible client from AIProjectClient?

- A) **project_client.get_openai_client() ✅**
- B) project_client.openai()
- C) project_client.create_openai()
- D) AIProjectClient.openai_client()

> **Explanation:** `project_client.get_openai_client()` returns an authenticated OpenAI-compatible client that can call `responses.create()` or `chat.completions.create()` through the Foundry project.

---

**Q47.** In Practice13, what does the extra_body agent_reference do?

- A) Creates a new agent
- B) **Routes the Responses API call to an already-deployed named agent in Foundry ✅**
- C) Passes custom headers
- D) Sets the model version

> **Explanation:** `extra_body` with `agent_reference` routes the API call to a specific named agent deployed in Azure AI Foundry, letting you call existing agents via the Responses API.

---

**Q48.** After a run completes, how do you get the agent's reply from a thread?

- A) run.output_text
- B) **project_client.agents.messages.list(thread_id=thread.id) ✅**
- C) project_client.agents.get_response(run.id)
- D) thread.last_message

> **Explanation:** `messages.list()` retrieves all messages on the thread. You then filter for `role == 'assistant'` to find the agent's reply and access `content[0].text.value`.

---

**Q49.** What does AIProjectClient provide beyond AI model calls (as seen in Practice02)?

- A) Only model inference
- B) **Listing project connections, evaluation rules, and infrastructure details ✅**
- C) Only agent management
- D) Only vector search

> **Explanation:** `AIProjectClient` can list infrastructure connections (`project_client.connections.list()`), run evaluations, and manage agents — it is a full project management client, not just a model client.

---

**Q50.** In Practice04, which model was called directly instead of GPT-4.1?

- A) gpt-4o
- B) Phi-3-mini
- C) **Phi-4-mini-reasoning ✅**
- D) Claude-3

> **Explanation:** Practice04 used `model='Phi-4-mini-reasoning'`, demonstrating that Azure AI Foundry can serve non-OpenAI models (like Microsoft's Phi family) through the same Responses API interface.

---

## Quick Reference Summary

| Topic | Questions | Practices Covered |
|---|---|---|
| ChatCompletions API | Q1 – Q10 | 01, 09, 10, 11 |
| Responses API | Q11 – Q20 | 02, 03, 05, 06 |
| Streaming | Q21 – Q30 | 03, 06, 07 |
| Async & Authentication | Q31 – Q40 | 04, 06, 08 |
| AI Agents & Foundry SDK | Q41 – Q50 | 02, 04, 12, 13, 14 |

---

## Key Concepts Cheat Sheet

```
ChatCompletions  →  stateless  →  manage history yourself via messages[]
Responses API    →  stateful   →  Azure manages history via previous_response_id
Streaming        →  stream=True → handle response.output_text.delta events
Async            →  AsyncOpenAI + azure.identity.aio + async for
Agents           →  thread → message → run → poll → messages.list()
Auth             →  DefaultAzureCredential + get_bearer_token_provider (NO hardcoded keys)
```

---

*AI-103 Azure AI Engineer Certification Practice | Azure AI Foundry Module*
