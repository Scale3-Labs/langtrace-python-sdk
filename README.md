<div align="center">
  <h1>Langtrace Python SDK</h1>
  <p>Open Source & Open Telemetry(OTEL) Observability for LLM Applications</p>

  ![Static Badge](https://img.shields.io/badge/License-Apache--2.0-blue)
  ![Static Badge](https://img.shields.io/badge/pip_langtrace--python--sdk-1.2.8-green)
  ![Static Badge](https://img.shields.io/badge/Development_status-Active-green)
  [![Downloads](https://static.pepy.tech/badge/langtrace-python-sdk)](https://static.pepy.tech/badge/langtrace-python-sdk)
  [![Deploy](https://railway.app/button.svg)](https://railway.app/template/8dNq1c?referralCode=MA2S9H)
</div>

---

## 📚 Table of Contents
- [✨ Features](#-features)
- [🚀 Quick Start](#-quick-start)
- [🔗 Integrations](#-supported-integrations)
- [🌐 Getting Started](#-getting-started)
- [⚙️ Configuration](#-configuration)
- [🔧 Advanced Features](#-advanced-features)
- [📐 Examples](#-examples)
- [🏠 Self Hosting](#-langtrace-self-hosted)
- [🤝 Contributing](#-contributions)
- [🔒 Security](#-security)
- [❓ FAQ](#-frequently-asked-questions)
- [📜 License](#-license)

Langtrace is an open source observability software which lets you capture, debug and analyze traces and metrics from all your applications that leverages LLM APIs, Vector Databases and LLM based Frameworks.

## ✨ Features

- 📊 **Open Telemetry Support**: Built on OTEL standards for comprehensive tracing
- 🔄 **Real-time Monitoring**: Track LLM API calls, vector operations, and framework usage
- 🎯 **Performance Insights**: Analyze latency, costs, and usage patterns
- 🔍 **Debug Tools**: Trace and debug your LLM application workflows
- 📈 **Analytics**: Get detailed metrics and visualizations
- 🛠️ **Framework Support**: Extensive integration with popular LLM frameworks
- 🔌 **Vector DB Integration**: Support for major vector databases
- 🎨 **Flexible Configuration**: Customizable tracing and monitoring options

## 🚀 Quick Start

```bash
pip install langtrace-python-sdk
```

```python
from langtrace_python_sdk import langtrace
langtrace.init(api_key='<your_api_key>') # Get your API key at langtrace.ai
```

## 🔗 Supported Integrations

Langtrace automatically captures traces from the following vendors:

### LLM Providers
| Provider | TypeScript SDK | Python SDK |
|----------|:-------------:|:----------:|
| OpenAI | ✅ | ✅ |
| Anthropic | ✅ | ✅ |
| Azure OpenAI | ✅ | ✅ |
| Cohere | ✅ | ✅ |
| Groq | ✅ | ✅ |
| Perplexity | ✅ | ✅ |
| Gemini | ❌ | ✅ |
| Mistral | ❌ | ✅ |
| AWS Bedrock | ✅ | ✅ |
| Ollama | ❌ | ✅ |
| Cerebras | ❌ | ✅ |

### Frameworks
| Framework | TypeScript SDK | Python SDK |
|-----------|:-------------:|:----------:|
| Langchain | ❌ | ✅ |
| LlamaIndex | ✅ | ✅ |
| Langgraph | ❌ | ✅ |
| LiteLLM | ❌ | ✅ |
| DSPy | ❌ | ✅ |
| CrewAI | ❌ | ✅ |
| VertexAI | ✅ | ✅ |
| EmbedChain | ❌ | ✅ |
| Autogen | ❌ | ✅ |
| HiveAgent | ❌ | ✅ |
| Inspect AI | ❌ | ✅ |
| Graphlit | ❌ | ✅ |
| Phidata | ❌ | ✅ |
| Arch | ❌ | ✅ |

### Vector Databases
| Database | TypeScript SDK | Python SDK |
|----------|:-------------:|:----------:|
| Pinecone | ✅ | ✅ |
| ChromaDB | ✅ | ✅ |
| QDrant | ✅ | ✅ |
| Weaviate | ✅ | ✅ |
| PGVector | ✅ | ✅ (SQLAlchemy) |
| MongoDB | ❌ | ✅ |
| Milvus | ❌ | ✅ |

## 🌐 Getting Started

### Langtrace Cloud ☁️

<!-- Original cloud setup instructions -->
1. Sign up by going to [this link](https://langtrace.ai).
2. Create a new Project after signing up. Projects are containers for storing traces and metrics generated by your application. If you have only one application, creating 1 project will do.
3. Generate an API key by going inside the project.
4. In your application, install the Langtrace SDK and initialize it with the API key you generated in the step 3.
5. The code for installing and setting up the SDK is shown below

### Framework Quick Starts

#### FastAPI
```python
from fastapi import FastAPI
from langtrace_python_sdk import langtrace
from openai import OpenAI

langtrace.init()
app = FastAPI()
client = OpenAI()

@app.get("/")
def root():
    client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Say this is a test"}],
        stream=False,
    )
    return {"Hello": "World"}
```

#### Django
```python
# settings.py
from langtrace_python_sdk import langtrace
langtrace.init()

# views.py
from django.http import JsonResponse
from openai import OpenAI

client = OpenAI()

def chat_view(request):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": request.GET.get('message', '')}]
    )
    return JsonResponse({"response": response.choices[0].message.content})
```

#### Flask
```python
from flask import Flask
from langtrace_python_sdk import langtrace
from openai import OpenAI

app = Flask(__name__)
langtrace.init()
client = OpenAI()

@app.route('/')
def chat():
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Hello!"}]
    )
    return {"response": response.choices[0].message.content}
```

#### LangChain
```python
from langtrace_python_sdk import langtrace
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

langtrace.init()

# LangChain operations are automatically traced
chat = ChatOpenAI()
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("user", "{input}")
])
chain = prompt | chat
response = chain.invoke({"input": "Hello!"})
```

#### LlamaIndex
```python
from langtrace_python_sdk import langtrace
from llama_index import VectorStoreIndex, SimpleDirectoryReader

langtrace.init()

# Document loading and indexing are automatically traced
documents = SimpleDirectoryReader('data').load_data()
index = VectorStoreIndex.from_documents(documents)

# Queries are traced with metadata
query_engine = index.as_query_engine()
response = query_engine.query("What's in the documents?")
```

#### DSPy
```python
from langtrace_python_sdk import langtrace
import dspy
from dspy.teleprompt import BootstrapFewShot

langtrace.init()

# DSPy operations are automatically traced
lm = dspy.OpenAI(model="gpt-4")
dspy.settings.configure(lm=lm)

class SimpleQA(dspy.Signature):
    """Answer questions with short responses."""
    question = dspy.InputField()
    answer = dspy.OutputField(desc="short answer")

compiler = BootstrapFewShot(metric=dspy.metrics.Answer())
program = compiler.compile(SimpleQA)
```

#### CrewAI
```python
from langtrace_python_sdk import langtrace
from crewai import Agent, Task, Crew

langtrace.init()

# Agents and tasks are automatically traced
researcher = Agent(
    role="Researcher",
    goal="Research and analyze data",
    backstory="Expert data researcher",
    allow_delegation=False
)

task = Task(
    description="Analyze market trends",
    agent=researcher
)

crew = Crew(
    agents=[researcher],
    tasks=[task]
)

result = crew.kickoff()
```

For more detailed examples and framework-specific features, visit our [documentation](https://docs.langtrace.ai).

## ⚙️ Configuration

### Initialize Options

The SDK can be initialized with various configuration options to customize its behavior:

```python
langtrace.init(
    api_key: Optional[str] = None,          # API key for authentication
    batch: bool = True,                     # Enable/disable batch processing
    write_spans_to_console: bool = False,   # Console logging
    custom_remote_exporter: Optional[Any] = None,  # Custom exporter
    api_host: Optional[str] = None,         # Custom API host
    disable_instrumentations: Optional[Dict] = None,  # Disable specific integrations
    service_name: Optional[str] = None,     # Custom service name
    disable_logging: bool = False,          # Disable all logging
    headers: Dict[str, str] = {},           # Custom headers
)
```

#### Configuration Details

| Parameter | Type | Default Value | Description |
|-----------|------|---------------|-------------|
| `api_key` | `str` | `LANGTRACE_API_KEY` or `None` | The API key for authentication. Can be set via environment variable |
| `batch` | `bool` | `True` | Whether to batch spans before sending them to reduce API calls |
| `write_spans_to_console` | `bool` | `False` | Enable console logging for debugging purposes |
| `custom_remote_exporter` | `Optional[Exporter]` | `None` | Custom exporter for sending traces to your own backend |
| `api_host` | `Optional[str]` | `https://langtrace.ai/` | Custom API endpoint for self-hosted deployments |
| `disable_instrumentations` | `Optional[Dict]` | `None` | Disable specific vendor instrumentations (e.g., `{'only': ['openai']}`) |
| `service_name` | `Optional[str]` | `None` | Custom service name for trace identification |
| `disable_logging` | `bool` | `False` | Disable SDK logging completely |
| `headers` | `Dict[str, str]` | `{}` | Custom headers for API requests |

### Environment Variables

Configure Langtrace behavior using these environment variables:

| Variable | Description | Default | Impact |
|----------|-------------|---------|---------|
| `LANGTRACE_API_KEY` | Primary authentication method | Required* | Required if not passed to init() |
| `TRACE_PROMPT_COMPLETION_DATA` | Control prompt/completion tracing | `true` | Set to 'false' to opt out of prompt/completion data collection |
| `TRACE_DSPY_CHECKPOINT` | Control DSPy checkpoint tracing | `true` | Set to 'false' to disable checkpoint tracing |
| `LANGTRACE_ERROR_REPORTING` | Control error reporting | `true` | Set to 'false' to disable Sentry error reporting |
| `LANGTRACE_API_HOST` | Custom API endpoint | `https://langtrace.ai/` | Override default API endpoint for self-hosted deployments |

> **Performance Note**: Setting `TRACE_DSPY_CHECKPOINT=false` is recommended in production environments as checkpoint tracing involves state serialization which can impact latency.

> **Security Note**: When `TRACE_PROMPT_COMPLETION_DATA=false`, no prompt or completion data will be collected, ensuring sensitive information remains private.

## 🔧 Advanced Features

### Root Span Decorator

Use the root span decorator to create custom trace hierarchies:

```python
from langtrace_python_sdk import langtrace

@langtrace.with_langtrace_root_span(name="custom_operation")
def my_function():
    # Your code here
    pass
```

### Additional Attributes

Inject custom attributes into your traces:

```python
# Using decorator
@langtrace.with_additional_attributes({"custom_key": "custom_value"})
def my_function():
    pass

# Using context manager
with langtrace.inject_additional_attributes({"custom_key": "custom_value"}):
    # Your code here
    pass
```

### Prompt Registry

Register and manage prompts for better traceability:

```python
from langtrace_python_sdk import langtrace

# Register a prompt template
langtrace.register_prompt("greeting", "Hello, {name}!")

# Use registered prompt
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": langtrace.get_prompt("greeting", name="Alice")}]
)
```

### User Feedback System

Collect and analyze user feedback:

```python
from langtrace_python_sdk import langtrace

# Record user feedback for a trace
langtrace.record_feedback(
    trace_id="your_trace_id",
    rating=5,
    feedback_text="Great response!",
    metadata={"user_id": "123"}
)
```

### DSPy Checkpointing

Manage DSPy checkpoints for workflow tracking:

```python
from langtrace_python_sdk import langtrace

# Enable checkpoint tracing (disabled by default in production)
langtrace.init(
    api_key="your_api_key",
    dspy_checkpoint_tracing=True
)
```

### Vector Database Operations

Track vector database operations:

```python
from langtrace_python_sdk import langtrace

# Vector operations are automatically traced
with langtrace.inject_additional_attributes({"operation_type": "similarity_search"}):
    results = vector_db.similarity_search("query", k=5)
```

For more detailed examples and use cases, visit our [documentation](https://docs.langtrace.ai).

<!-- Will be expanded in step 007 with comprehensive documentation of advanced features -->

## 📐 Examples

<!-- Will be added in step 008: Framework-specific examples and usage patterns -->

## 🏠 Langtrace Self Hosted

<!-- Original self-hosted documentation -->
Get started with self-hosted Langtrace:

```python
from langtrace_python_sdk import langtrace
langtrace.init(write_spans_to_console=True)  # For console logging
# OR
langtrace.init(custom_remote_exporter=<your_exporter>, batch=<True or False>)  # For custom exporter
```

## 🤝 Contributing

We welcome contributions! To get started:

1. Fork this repository and start developing
2. Join our [Discord](https://discord.langtrace.ai) workspace
3. Run examples:
   ```python
   # In run_example.py, set ENABLED_EXAMPLES flag to True for desired example
   python src/run_example.py
   ```
4. Run tests:
   ```python
   pip install '.[test]' && pip install '.[dev]'
   pytest -v
   ```

## 🔒 Security

To report security vulnerabilities, email us at <security@scale3labs.com>. You can read more on security [here](https://github.com/Scale3-Labs/langtrace/blob/development/SECURITY.md).

## ❓ Frequently Asked Questions

<!-- Will be populated during content addition steps -->

## 📜 License

Langtrace Python SDK is licensed under the Apache 2.0 License. You can read about this license [here](https://www.apache.org/licenses/LICENSE-2.0).
