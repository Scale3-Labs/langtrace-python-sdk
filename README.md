<h1 align="center">LangTrace</h1>

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

OpenLLMetry can instrument everything that [OpenTelemetry already instruments](https://github.com/open-telemetry/opentelemetry-python-contrib/tree/main/instrumentation) - so things like your DB, API calls, and more. On top of that, we built a set of custom extensions that instrument things like your calls to OpenAI or Anthropic, or your Vector DB like Chroma, Pinecone, Qdrant or Weaviate.

### LLM Providers

- ✅ OpenAI / Azure OpenAI
- ✅ Anthropic




### Vector DBs

- ✅ Chroma
- ✅ Pinecone

### Frameworks

- ✅ LangChain
- ✅ [LlamaIndex](https://docs.llamaindex.ai/en/stable/module_guides/observability/observability.html#openllmetry)




