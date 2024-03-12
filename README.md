<h1>LangTrace</h1>

<p>
LangTrace is a Python package designed to instrument traces of various Language Model as a Service (LLMS) products, such as OpenAI and Anthropic, as well as vector databases like Pinecone. This package provides functionalities to capture and analyze traces, allowing users to gain insights into the behavior and performance of these systems.
</p>

<h3>Features</h3>
<li><b>Trace Instrumentation:</b> LangTrace enables the instrumentation of LLMS products and vector databases to capture detailed traces of their operations.</li>

<li><b>Compatibility:</b> LangTrace is compatible with various LLMS products, including OpenAI and Anthropic, as well as vector databases like Pinecone and Chroma which adhere to <a href="https://opentelemetry.io/">OpenTelemetry</a> standards</li>

<h3>
Install the SDK
</h3>

```bash
pip install langtrace-python-sdk
```

<h3>Usage</h3>

```python
from langtrace_python_sdk import langtrace

langtrace.init()
```

<p>Voila! now you're all set.</p>


<h3>Examples</h3>

<p>Log Traces</p>

```python
from langtrace_python_sdk import langtrace

langtrace.init(log_spans_to_console=True)
```

<p>Export traces to an external endpoint.</p>

Add the endpoint url inside ```.env``` as ```LANGTRACE_URL```


```python
from langtrace_python_sdk import langtrace

langtrace.init(write_to_remote_url=True)
```


<h3>
Support


</h3>

<li>
OpenAI</li>

<li>
Anthropic</li>

<li>
Chroma</li>

<li>
PineCone</li>

<li>
LangChain</li>

<li>
LlamaIndex</li>




<!-- <h1 align="center">LangTrace</h1>

Looking for the Typescript version? Check out [langtrace-typescript](https://github.com/Scale3-Labs/langtrace-typescript-sdk).

LangTrace is a set of extensions built on top of [OpenTelemetry](https://opentelemetry.io/) that gives you complete observability over your LLM application. Because it uses OpenTelemetry under the hood.


The repo contains standard OpenTelemetry instrumentations for LLM providers and Vector DBs, while still outputting standard OpenTelemetry data that can be connected to your observability stack.
If you already have OpenTelemetry instrumented, you can just add any of our instrumentations directly.

## 🚀 Getting Started

The easiest way to get started is to use our SDK.

Install the SDK:

```bash
pip install langtrace-python-sdk
```

Then, to start instrumenting your code, just add this line to your code:

```python
from langtrace_python_sdk import langtrace

langtrace.init()
```

That's it. You're now tracing your code with LangTrace!
If you want to see the traces you can enable logging

```python
langtrace.init(log_spans_to_console=True)
```

If you want to export traces to an external endpoint, you will need to add ```LANGTRACE_URL``` to ```.env``` file.
```python
langtrace.init(write_to_remote_url=True)
```



## 🪗 What do we instrument?

LangTrace can instrument everything that [OpenTelemetry already instruments](https://github.com/open-telemetry/opentelemetry-python-contrib/tree/main/instrumentation) - so things like your DB, API calls, and more. On top of that, we built a set of custom extensions that instrument things like your calls to OpenAI or Anthropic, or your Vector DB like Chroma, Pinecone

### LLM Providers

- ✅ OpenAI / Azure OpenAI
- ✅ Anthropic




### Vector DBs

- ✅ Chroma
- ✅ Pinecone

### Frameworks

- ✅ LangChain
- ✅ LlamaIndex



 -->
