# What is Langtrace?

Langtrace stands as a developer-centric, open-source solution, fully compatible with OpenTelemetry. It enables developers to effortlessly trace, monitor, and debug their LLM applications, offering robust support for automatic instrumentation.

## Supported LLM Modules

Langtrace supports a comprehensive range of LLMs, VectorDBs, and frameworks, ensuring wide coverage for your development needs:

### LLMs

1. OpenAI
2. Anthropic
3. Azure OpenAI

### VectorDBs

1. Pinecone
2. Chromadb

### Frameworks

1. LangChain
2. LlamaIndex
3. Haystack

We are actively working to extend our support to additional libraries!

## Getting Started

To begin utilizing Langtrace, follow these straightforward steps:

1. Install the package using `pip install langtrace-python-sdk`.
2. Incorporate Langtrace into your project with `from langtrace_python_sdk import langtrace`.
   - This import should precede any other LLM module imports (such as OpenAI, LlamaIndex, etc.) to ensure proper functionality.
3. Initialize Langtrace by adding `langtrace.init(write_to_langtrace_cloud=false)` to your code.
4. Congratulations, you've completed the basic setup! You will now begin to see traces from your LLM modules logged directly to the console.


## Exporting Traces to Langtrace

To configure trace exporting, you have two options:

You'll need a Langtrace `api_key`, which can be acquired by logging into your Langtrace account.

1. Direct Initialization: Utilize `langtrace.init(api_key=<YOUR_API_KEY>)`.
2. Environment Variables: Set `LANGTRACE_API_KEY`, then add `langtrace.init()` at the beginning of your file.

### Additional Customization

- `@with_langtrace_root_span` - this decorator is designed to organize and relate different spans, in a hierarchical manner. When you're performing multiple operations that you want to monitor together as a unit, this function helps by establishing a "parent" (`LangtraceRootSpan` or whatever is passed to `name`) span. Then, any calls to the LLM APIs made within the given function (fn) will be considered "children" of this parent span. This setup is especially useful for tracking the performance or behavior of a group of operations collectively, rather than individually.

```python
from langtrace_python_sdk.utils.with_root_span import with_langtrace_root_span

@with_langtrace_root_span()
def example():
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Say this is a test three times"}],
        stream=False,
    )
    return response
```


- `with_additional_attributes` - this function is designed to enhance the traces by adding custom attributes to the current context. These custom attributes provide extra details about the operations being performed, making it easier to analyze and understand their behavior.

```python
from langtrace_python_sdk.utils.with_root_span import (
    with_langtrace_root_span,
    with_additional_attributes,
)

@with_additional_attributes({"user.id": "1234", "user.feedback.rating": 1})
def api_call1():
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Say this is a test three times"}],
        stream=False,
    )
    return response


@with_additional_attributes({"user.id": "5678", "user.feedback.rating": -1})
def api_call2():
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Say this is a test three times"}],
        stream=False,
    )
    return response


@with_langtrace_root_span()
def chat_completion():
   api_call1()
   api_call2()
```

## Langtrace Cloud

Currently under development 🚧
