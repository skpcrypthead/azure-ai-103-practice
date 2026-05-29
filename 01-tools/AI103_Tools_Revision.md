# AI-103 Exam Revision: Tools in Generative AI Models
> **Module:** Tools enable models to perform tasks and interact with external systems
> **Platform:** Microsoft Azure AI Foundry (OpenAI Responses API)

---

## 🧠 Core Theory

### What Are Tools?
Tools extend a generative AI model's capabilities **beyond basic chat interactions**. They allow models to perform real-world tasks, retrieve live data, execute code, or call developer-defined functions.

### Key Principle: Tool Selection
> By default, the **model chooses when to use a tool (and which one)** based on the prompt. You can configure tool selection rules and use the `instructions` (system prompt) parameter to guide this choice.

### How Tools Are Specified
Tools are passed in the `tools=[]` array inside a `client.responses.create()` call using the **OpenAI Responses API**.

```python
response = client.responses.create(
    model={model_deployment},
    instructions="You are a helpful AI assistant.",
    input="Find me some information about vintage computers.",
    tools=[
        {"type": "{tool_type}", "{tool-specific-setting}": "{value}"},
    ]
)
```

---

## 🔧 The Four Core Tools

### 1. `code_interpreter` — Run Python Code Dynamically

#### Theory
- Provides a **sandboxed Python runtime** to the model
- Model writes and runs Python code to solve problems, not just describe them
- Transforms the model from a "thinker" into a "doer"

#### Key Features
| Feature | Description |
|---|---|
| Dynamic Execution | Model writes & runs Python in a sandbox |
| File Handling | Upload/process/download CSV, JSON, images |
| Data Analysis | Calculations, statistics, transformations |
| Real-time Feedback | Model sees execution output; can iterate/fix errors |
| Complex Solving | Math, simulations, logic puzzles via executable code |

#### Process Flow
1. Include `code_interpreter` in the `tools` array
2. Model analyzes if code execution is needed
3. Model generates Python code
4. Code runs in sandboxed env (pandas, numpy, math pre-installed)
5. Results returned and incorporated into response

#### API Usage
```python
tools=[{"type": "code_interpreter", "container": {"type": "auto"}}]
```

#### Best Practices
- Be specific about data format and expected output
- Use "python tool" language in instructions (models internally use this name)
- Validate AI-generated code before production use
- Monitor costs — code execution adds tokens
- Leverage pre-installed libs: `pandas`, `numpy`, `matplotlib`

#### Limitations ⚠️
- No external network access from sandbox
- Not all libraries available
- Timeout limits apply
- Memory constraints — large datasets need chunking

---

### 2. `web_search` — Retrieve Live Internet Data

#### Theory
- Gives model access to **current, external information at runtime**
- Overcomes training data cutoff limitation
- Model issues a search query, reviews sources, and grounds its answer

#### Key Features
| Feature | Description |
|---|---|
| Live Retrieval | Recent info not in static training data |
| Source-Grounded Responses | Answers built from retrieved web content |
| Reduced Hallucination | Reliability improved via external source check |
| Automatic Query Generation | Model decides when and how to search |

#### Use Cases
| Scenario | Example |
|---|---|
| Current Events | Breaking tech announcements |
| Market Research | Product features / pricing comparison |
| Policy Monitoring | Regulation changes |
| Fact Verification | Validate against reputable sources |

#### Process Flow
1. Include `web_search` in the `tools` array
2. Model evaluates if fresh web data is needed
3. Model issues one or more search queries
4. Relevant pages selected and summarized
5. Model generates final answer from search findings

#### API Usage
```python
tools=[{"type": "web_search"}]
```

#### Best Practices
- Use time-aware keywords: "latest", "current", or date ranges
- Prompt for reputable/official sources when accuracy matters
- Request concise summaries to reduce noise
- Independently validate critical facts
- Track usage — web retrieval increases latency and tokens

#### Limitations ⚠️
- Depends on publicly available and indexable content
- Source quality varies — output may need human review
- Repeated runs can produce different answers (content changes)
- Regional, policy, or network restrictions may apply

---

### 3. `file_search` — Search Uploaded Private Documents

#### Theory
- Lets model answer from **private/domain-specific files** (PDFs, docs, manuals)
- Uses **semantic retrieval** (meaning-based, not just keyword match)
- Requires a **vector store** — files must be indexed before searching

#### Key Features
| Feature | Description |
|---|---|
| Document-Grounded Answers | Based on your uploaded files, not general training |
| Semantic Retrieval | Finds relevant passages by meaning |
| Vector Store Integration | Search across indexed document collections |
| Citations & Transparency | Include matched results for traceability |

#### Use Cases
| Scenario | Example |
|---|---|
| Policy Q&A | HR policy PDFs |
| Support Assistants | Troubleshooting guides |
| Legal Review | Contract clause lookup |
| Knowledge Discovery | Technical documentation sets |

#### Process Flow
1. Upload documents to a **vector store**
2. Include `file_search` with `vector_store_ids` in the `tools` array
3. Model performs retrieval — searches indexed chunks
4. Matching passages injected into model context
5. Model answers using retrieved document context

#### API Usage
```python
# Step 1: Create vector store and upload file
vector_store = client.vector_stores.create(name="policy-docs")
client.vector_stores.files.upload_and_poll(
    vector_store_id=vector_store.id,
    file=open("expenses_policy.pdf", "rb")
)

# Step 2: Use file_search in response
tools=[{
    "type": "file_search",
    "vector_store_ids": [vector_store.id]
}],
include=["file_search_call.results"]
```

#### Best Practices
- Use clean, current documents for better retrieval accuracy
- Write focused, specific prompts
- Separate vector stores by domain (HR, legal, finance)
- Use `include=["file_search_call.results"]` during development for debugging
- Keep human validation in high-stakes scenarios

#### Limitations ⚠️
- Answer quality depends on document quality and chunk relevance
- Large or mixed-domain stores can return less focused context
- Updated files require **re-indexing** before new content is searchable

> 💡 **Enterprise Note:** For large-scale agents needing access to multiple large data stores, use **Foundry IQ knowledge store** with a Microsoft Foundry agent.

---

### 4. `function` — Call Custom Developer-Defined Functions

#### Theory
- Lets model decide when to call **your application's business logic**
- Model does NOT run your code directly — it **emits a structured function call request**
- Your app runs the function and **passes result back** to the model (multi-turn)
- Ideal for connecting model reasoning to APIs, databases, workflows

#### Key Features
| Feature | Description |
|---|---|
| Structured Tool Calls | Model emits explicit function-call requests |
| Developer-Controlled Execution | Your app runs functions, not the model |
| Multi-Turn Orchestration | Return tool output; model continues reasoning |
| Grounded Responses | Answers include live, system-generated data |

#### Use Cases
| Scenario | Example |
|---|---|
| System Integration | Call internal API for order/account details |
| Task Automation | Trigger workflows (tickets, notifications) |
| Data Lookup | Query business rules before answering |

#### Process Flow
1. You define tool(s) with function name and description in `tools` array
2. Model evaluates prompt — determines if function call needed
3. Model emits a `function_call` with name and `call_id`
4. **Your application code runs the function**
5. You return `function_call_output` with the result
6. Model incorporates result into final response

#### API Usage
```python
# Define the tool
function_tools = [
    {"type": "function", "name": "get_time", "description": "Get the current time"}
]

# First call — model may emit function_call
response = client.responses.create(model=..., input=messages, tools=function_tools)

# Check for function call in output
for item in response.output:
    if item.type == "function_call" and item.name == "get_time":
        result = get_time()  # Your code runs the function
        messages.append({
            "type": "function_call_output",
            "call_id": item.call_id,
            "output": result
        })

# Second call — model uses function output to answer
response = client.responses.create(model=..., input=messages, tools=function_tools)
```

#### Best Practices
- Keep functions small and single-purpose
- **Always validate function inputs** — never trust tool arguments blindly in production
- Return clear error outputs the model can reason about
- Log tool usage (calls, latency, failures) for governance
- Require explicit authorization for high-impact actions

#### Limitations ⚠️
- Model requests functions — **your app must run them**
- Unexpected/incorrect tool arguments can occur — must be validated
- Tool latency increases end-to-end response time

---

## 📊 Tool Comparison Summary

| Tool | Data Source | Execution | Best For |
|---|---|---|---|
| `code_interpreter` | None (generates code) | Sandboxed Python runtime | Math, data analysis, file conversion |
| `web_search` | Live internet | External search engine | Current events, fact checking |
| `file_search` | Your uploaded files (vector store) | Semantic retrieval | Private docs, enterprise knowledge |
| `function` | Your application logic | Your app code | APIs, databases, custom workflows |

---

## 🔑 Key Terminology for AI-103 Exam

| Term | Definition |
|---|---|
| **Responses API** | OpenAI API used to submit prompts with tool support in Azure AI Foundry |
| **`responses.create()`** | Python method to call the model with optional tools, instructions, and input |
| **`tools=[]`** | Parameter in `responses.create()` listing available tools for the model |
| **`instructions`** | System prompt parameter that guides model behavior and tool selection |
| **Sandboxed environment** | Isolated Python runtime for `code_interpreter` — no external network access |
| **Vector store** | Indexed document collection used by `file_search` for semantic retrieval |
| **`vector_store_ids`** | Parameter linking `file_search` tool to specific vector stores |
| **`upload_and_poll()`** | Method to upload files to a vector store and wait for indexing to complete |
| **Semantic retrieval** | Finding relevant content by meaning, not just exact keyword matches |
| **`function_call`** | Response item emitted by model when it wants to invoke a developer function |
| **`function_call_output`** | Message item sent back to model with result of the executed function |
| **`call_id`** | Unique identifier linking a function call request to its output |
| **`previous_response_id`** | Parameter used to maintain multi-turn conversation state |
| **`include=["file_search_call.results"]`** | Parameter to expose retrieval results for debugging |
| **Grounding** | Basing model responses on retrieved/real data rather than training memory |
| **Hallucination** | Model generating plausible but incorrect facts — tools help reduce this |
| **Multi-turn orchestration** | Pattern where model and app exchange function calls across multiple steps |
| **Azure AI Foundry** | Microsoft's platform for deploying and using AI models |
| **Foundry IQ** | Enterprise-scale knowledge store solution for agents in Azure AI Foundry |
| **`DefaultAzureCredential`** | Azure Identity class for managed, credential-free authentication |
| **`get_bearer_token_provider`** | Utility to generate auth tokens for Azure AI endpoints |

---

## ⚡ Quick Reference: Tool Configuration Patterns

```python
# code_interpreter
{"type": "code_interpreter", "container": {"type": "auto"}}

# web_search
{"type": "web_search"}

# file_search
{"type": "file_search", "vector_store_ids": ["vs_abc123"]}

# function
{"type": "function", "name": "my_func", "description": "What this function does"}
```

---

## 🎯 Exam Tips

1. **Tool selection is automatic** — model decides which tool to use; `instructions` can guide it
2. **`code_interpreter` = sandbox** — no internet, limited libraries, handles data/math
3. **`file_search` needs a vector store first** — upload → index → then query
4. **`function` tool is two-step** — model requests → your app runs it → you return result
5. **`web_search` is for real-time data** — reduces hallucination from stale training data
6. **Multiple tools can be combined** — `file_search` + `web_search` in one call is valid
7. **`previous_response_id`** maintains conversation context across turns
8. **Always validate function tool inputs** — model-generated args may be unexpected
9. **Re-index vector stores** when source documents are updated
10. **Foundry IQ** is the enterprise-scale alternative to `file_search` for large data sets

---

## 📝 Practice Questions — AI-103 Exam Style

> **Instructions:** Choose the best answer for each question. Answers and explanations are at the end of this section.

---

### Section A: Multiple Choice

**Q1.** You are building a generative AI application using Azure AI Foundry. A user asks the model a question about current stock prices. Which tool should the model use to provide an accurate answer?

- A) `code_interpreter`
- B) `file_search`
- C) `web_search`
- D) `function`

---

**Q2.** A developer wants to enable a model to execute Python code during a conversation to solve complex mathematical equations. Which tool should be specified in the `tools` array?

- A) `{"type": "web_search"}`
- B) `{"type": "function", "name": "python_exec"}`
- C) `{"type": "code_interpreter", "container": {"type": "auto"}}`
- D) `{"type": "file_search", "vector_store_ids": []}`

---

**Q3.** You have uploaded a set of HR policy PDF files and want the model to answer employee questions based only on those documents. What must you do BEFORE using the `file_search` tool?

- A) Enable web search so the model can index the documents
- B) Create a vector store and upload the documents to it
- C) Convert the PDFs to plain text files
- D) Define a custom function that reads the PDF files

---

**Q4.** A model response contains an item of type `function_call`. What should your application do next?

- A) Display the function call details to the end user
- B) Submit a new prompt asking the model to run the function itself
- C) Execute the referenced function in your application code and return a `function_call_output` message
- D) Ignore it — the model will automatically execute the function in the background

---

**Q5.** Which of the following statements about the `code_interpreter` tool is TRUE?

- A) It can access external websites to fetch real-time data during code execution
- B) It runs Python code in a sandboxed environment with no external network access
- C) It requires the developer to provide a pre-written Python script
- D) It only supports mathematical operations; file handling is not supported

---

**Q6.** You are using the `function` tool and the model emits a `function_call` in its response. Which field must you include when returning the result back to the model?

- A) `function_id`
- B) `call_id`
- C) `tool_name`
- D) `response_token`

---

**Q7.** An organization wants to use `file_search` to search across HR documents, legal contracts, and finance reports. What is the recommended approach for organizing vector stores?

- A) Upload all documents into a single large vector store for simplicity
- B) Create one vector store per file to ensure precise retrieval
- C) Separate vector stores by domain (HR, legal, finance) for more focused retrieval
- D) Use `web_search` instead, as `file_search` does not support multiple document types

---

**Q8.** By default, how does a model decide which tool to use when multiple tools are specified?

- A) The developer must always explicitly set `tool_choice` to select the tool
- B) The model chooses the tool automatically based on the prompt
- C) Tools are invoked in the order they appear in the `tools` array
- D) The first tool in the `tools` array is always used by default

---

**Q9.** After updating a policy document that was previously uploaded to a vector store, a user reports that the model is still returning outdated information. What is the most likely cause?

- A) The `web_search` tool is overriding the `file_search` results
- B) The `include` parameter was not set to `file_search_call.results`
- C) The updated document has not been re-indexed in the vector store
- D) The model's training data contains the old policy and cannot be overridden

---

**Q10.** Which parameter in `responses.create()` is used to maintain conversation history across multiple turns?

- A) `conversation_id`
- B) `session_token`
- C) `previous_response_id`
- D) `memory_context`

---

**Q11.** A developer needs to build a travel assistant that answers questions from uploaded brochures AND retrieves current travel advisories from the internet. Which tool configuration should they use?

- A) `file_search` only — it can search both internal files and the web
- B) `web_search` only — it covers all information needs
- C) `code_interpreter` — it can read files and connect to the internet
- D) Both `file_search` and `web_search` specified in the same `tools` array

---

**Q12.** For enterprise-scale agents that need to access large quantities of data across multiple data stores, what does Microsoft recommend instead of the standard `file_search` tool?

- A) Azure Cognitive Search
- B) Foundry IQ knowledge store
- C) Azure Blob Storage with direct file access
- D) A custom `function` tool that queries each data store

---

**Q13.** Which of the following is a key limitation of the `web_search` tool?

- A) It cannot search for information published after the model's training cutoff
- B) Results depend on publicly available content and may vary between runs
- C) It requires a vector store to be created before it can be used
- D) It only works when combined with the `code_interpreter` tool

---

**Q14.** A model is configured with a `function` tool named `get_weather`. The user asks "What is the weather in Dubai?" The model emits a `function_call` for `get_weather`. What happens if your application code does NOT return a `function_call_output`?

- A) The model automatically retries by calling `web_search` instead
- B) The model generates a response based on its training data only
- C) The conversation flow breaks — the model cannot complete its response without the function output
- D) The function tool is disabled for the rest of the session

---

**Q15.** Which authentication class is used in the exercise code to connect to Azure AI Foundry without hardcoding credentials?

- A) `AzureKeyCredential`
- B) `ClientSecretCredential`
- C) `DefaultAzureCredential`
- D) `ManagedIdentityCredential`

---

### Section B: True / False

**Q16.** The model always uses every tool listed in the `tools` array for every response.
`True / False`

**Q17.** The `code_interpreter` tool can automatically fix Python errors it encounters during execution.
`True / False`

**Q18.** The `function` tool directly executes the developer's application code inside the model runtime.
`True / False`

**Q19.** Semantic retrieval finds relevant content based on meaning, not just exact keyword matches.
`True / False`

**Q20.** You can combine `file_search` and `web_search` in a single `responses.create()` call.
`True / False`

---

### Section C: Short Answer / Scenario

**Q21.** A data analyst asks a model: *"Parse this CSV file and give me the average sales per region."* Which tool is most appropriate and why? What are two limitations to be aware of?

**Q22.** Describe the complete 6-step flow when a model uses the `function` tool to call a custom `get_order_status` function. What does your application code need to do between steps 3 and 5?

**Q23.** A developer sets up `file_search` with a vector store containing 500 mixed-domain documents (HR, legal, technical manuals). Users report that answers are sometimes irrelevant. What is the likely cause and how should the developer fix it?

**Q24.** Why is it important to validate function inputs when using the `function` tool in a production system? Give one example of what could go wrong if validation is skipped.

---

## ✅ Answers & Explanations

| Q | Answer | Explanation |
|---|--------|-------------|
| 1 | **C** | `web_search` retrieves live, current data. Stock prices change in real time and are not in the model's training data. |
| 2 | **C** | `code_interpreter` requires `{"type": "code_interpreter", "container": {"type": "auto"}}`. Option B invents a non-existent tool type. |
| 3 | **B** | `file_search` requires a vector store to be created and documents uploaded and indexed before it can retrieve anything. |
| 4 | **C** | The application must run the function and return a `function_call_output` message. The model does not execute code itself. |
| 5 | **B** | `code_interpreter` runs in a sandboxed environment — no external network, pre-installed libraries, memory constraints. |
| 6 | **B** | `call_id` links the function call request to its output. The model uses it to match results to the correct function call. |
| 7 | **C** | Separating stores by domain (HR, legal, finance) reduces retrieval noise and improves relevance of results. |
| 8 | **B** | By default, the model autonomously decides which tool to use based on the prompt. The `instructions` parameter can guide this. |
| 9 | **C** | Updated documents must be re-indexed in the vector store before new content becomes searchable. |
| 10 | **C** | `previous_response_id` maintains multi-turn conversation context across calls. |
| 11 | **D** | Both tools can be specified together. `file_search` handles brochure content; `web_search` retrieves current travel advisories. |
| 12 | **B** | Microsoft recommends **Foundry IQ** for enterprise-scale agents with large, multi-source data requirements. |
| 13 | **B** | `web_search` results depend on publicly available indexed content and can vary between runs as content changes. |
| 14 | **C** | The conversation flow breaks — the model is waiting for function output to complete its reasoning; without it, the turn cannot be finished correctly. |
| 15 | **C** | `DefaultAzureCredential` is used for credential-free, managed authentication to Azure AI services. |
| 16 | **False** | The model chooses which tool(s) to use based on the prompt. Not every tool is called on every turn. |
| 17 | **True** | The model sees execution errors and will attempt to fix and re-run the code automatically. |
| 18 | **False** | The model emits a structured `function_call` request. The developer's application code must execute the function and return the result. |
| 19 | **True** | Semantic retrieval uses vector embeddings to find relevant content by meaning, enabling it to match paraphrased or conceptually similar queries. |
| 20 | **True** | Multiple tools can be combined in a single `tools` array. The model will use whichever is appropriate for the query. |

**Q21 — Sample Answer:**
`code_interpreter` is most appropriate. It can load the uploaded CSV file, run Python (using pandas) to parse the data, compute averages by region, and return actual results — not just describe the process. Two limitations: (1) it has no external network access, so the CSV must be uploaded directly to the session; (2) very large files may hit memory constraints and may need to be chunked.

**Q22 — Sample Answer:**
1. Developer defines `get_order_status` function in the `tools` array with name and description.
2. Model evaluates the user prompt and determines a function call is needed.
3. Model emits a `function_call` item in its response output, containing the function name and a `call_id`.
4. *(Application step)* Your code detects the `function_call`, runs the `get_order_status` logic (e.g., queries a database), and appends a `function_call_output` message with the result and `call_id` to the conversation messages.
5. Application sends a second `responses.create()` call with the full updated message history.
6. Model reads the function output and generates the final response for the user.

**Q23 — Sample Answer:**
The likely cause is a mixed-domain vector store — when 500 documents from different domains are indexed together, retrieval can surface chunks from the wrong domain. The fix is to separate the documents into domain-specific vector stores (one for HR, one for legal, one for technical) and configure `file_search` with only the relevant `vector_store_ids` for each use case.

**Q24 — Sample Answer:**
The model generates function arguments based on its interpretation of the prompt — these can be malformed, out of range, or unexpected. In a production system, unvalidated inputs could cause errors, expose vulnerabilities, or trigger unintended actions. Example: if a `delete_record` function expects a numeric ID but the model passes a string like `"all"`, skipping validation could cause a catastrophic deletion. Always sanitize and validate tool arguments before execution.
