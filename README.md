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

