# [Langtrace](https://www.langtrace.ai)

## Open Source & Open Telemetry(OTEL) Observability for LLM applications

![Static Badge](https://img.shields.io/badge/License-Apache--2.0-blue) ![Static Badge](https://img.shields.io/badge/npm_@langtrase/typescript--sdk-1.2.9-green) ![Static Badge](https://img.shields.io/badge/pip_langtrace--python--sdk-1.2.8-green) ![Static Badge](https://img.shields.io/badge/Development_status-Active-green)

---

Langtrace is an open source observability software which lets you capture, debug and analyze traces and metrics from all your applications that leverages LLM APIs, Vector Databases and LLM based Frameworks.

## Open Telemetry Support

The traces generated by Langtrace adhere to [Open Telemetry Standards(OTEL)](https://opentelemetry.io/docs/concepts/signals/traces/). We are developing [semantic conventions](https://opentelemetry.io/docs/concepts/semantic-conventions/) for the traces generated by this project. You can checkout the current definitions in [this repository](https://github.com/Scale3-Labs/langtrace-trace-attributes/tree/main/schemas). Note: This is an ongoing development and we encourage you to get involved and welcome your feedback.

---

## Langtrace Cloud ☁️

To use the managed SaaS version of Langtrace, follow the steps below:

1. Sign up by going to [this link](https://langtrace.ai).
2. Create a new Project after signing up. Projects are containers for storing traces and metrics generated by your application. If you have only one application, creating 1 project will do.
3. Generate an API key by going inside the project.
4. In your application, install the Langtrace SDK and initialize it with the API key you generated in the step 3.
5. The code for installing and setting up the SDK is shown below

## Getting Started

Get started by adding simply three lines to your code!

```python
pip install langtrace-python-sdk
```

```python
from langtrace_python_sdk import langtrace # Must precede any llm module imports
langtrace.init(api_key=<your_api_key>)
```

OR

```python
from langtrace_python_sdk import langtrace # Must precede any llm module imports
langtrace.init() # LANGTRACE_API_KEY as an ENVIRONMENT variable
```

## FastAPI Quick Start

Initialize FastAPI project and add this inside the `main.py` file

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
        messages=[{"role": "user", "content": "Say this is a test three times"}],
        stream=False,
    )
    return {"Hello": "World"}
```

## Django Quick Start

Initialize django project and add this inside the `__init.py__` file

```python
from langtrace_python_sdk import langtrace
from openai import OpenAI


langtrace.init()
client = OpenAI()

client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Say this is a test three times"}],
    stream=False,
)

```

## Flask Quick Start

Initialize flask project and this inside `app.py` file

```python
from flask import Flask
from langtrace_python_sdk import langtrace
from openai import OpenAI

langtrace.init()
client = OpenAI()
app = Flask(__name__)


@app.route("/")
def main():
    client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Say this is a test three times"}],
        stream=False,
    )
    return "Hello, World!"
```

## Langtrace Self Hosted

Get started by adding simply two lines to your code and see traces being logged to the console!

```python
pip install langtrace-python-sdk
```

```python
from langtrace_python_sdk import langtrace # Must precede any llm module imports
langtrace.init(write_spans_to_console=True)
```

## Langtrace self hosted custom exporter

Get started by adding simply three lines to your code and see traces being exported to your remote location!

```python
pip install langtrace-python-sdk
```

```python
from langtrace_python_sdk import langtrace # Must precede any llm module imports
langtrace.init(custom_remote_exporter=<your_exporter>, batch=<True or False>)
```

### Configure Langtrace

| Parameter                  | Type                                | Default Value                 | Description                                                                                                                       |
| -------------------------- | ----------------------------------- | ----------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| `api_key`                  | `str`                               | `LANGTRACE_API_KEY` or `None` | The API key for authentication.                                                                                                   |
| `batch`                    | `bool`                              | `True`                        | Whether to batch spans before sending them.                                                                                       |
| `write_spans_to_console`   | `bool`                              | `False`                       | Whether to write spans to the console.                                                                                            |
| `custom_remote_exporter`   | `Optional[Exporter]`                | `None`                        | Custom remote exporter. If `None`, a default `LangTraceExporter` will be used.                                                    |
| `api_host`                 | `Optional[str]`                     | `https://langtrace.ai/`       | The API host for the remote exporter.                                                                                             |
| `disable_instrumentations` | `Optional[DisableInstrumentations]` | `None`                        | You can pass an object to disable instrumentation for specific vendors ex: `{'only': ['openai']}` or `{'all_except': ['openai']}` |

### Additional Customization

- `@with_langtrace_root_span` - this decorator is designed to organize and relate different spans, in a hierarchical manner. When you're performing multiple operations that you want to monitor together as a unit, this function helps by establishing a "parent" (`LangtraceRootSpan` or whatever is passed to `name`) span. Then, any calls to the LLM APIs made within the given function (fn) will be considered "children" of this parent span. This setup is especially useful for tracking the performance or behavior of a group of operations collectively, rather than individually.

```python
from langtrace_python_sdk import with_langtrace_root_span

@with_langtrace_root_span()
def example():
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Say this is a test three times"}],
        stream=False,
    )
    return response
```

- `inject_additional_attributes` - this function is designed to enhance the traces by adding custom attributes to the current context. These custom attributes provide extra details about the operations being performed, making it easier to analyze and understand their behavior.

```python
from langtrace_python_sdk import inject_additional_attributes



def do_llm_stuff(name=""):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Say this is a test three times"}],
        stream=False,
    )
    return response


def main():
  response = inject_additional_attributes(lambda: do_llm_stuff(name="llm"), {'user.id': 'userId'})

  # if the function do not take arguments then this syntax will work
  response = inject_additional_attributes(do_llm_stuff, {'user.id': 'userId'})
```

- `with_additional_attributes` - is behaving the same as `inject_additional_attributes` but as a decorator, this will be deprecated soon.

```python
from langtrace_python_sdk import with_langtrace_root_span, with_additional_attributes


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

- `get_prompt_from_registry` - this function is designed to fetch the desired prompt from the `Prompt Registry`. You can pass two options for filtering `prompt_version` & `variables`.

```python
from langtrace_python_sdk import get_prompt_from_registry

prompt = get_prompt_from_registry(<Registry ID>, options={"prompt_version": 1, "variables": {"foo": "bar"} })
```

## Supported integrations

Langtrace automatically captures traces from the following vendors:

| Vendor       | Type            | Typescript SDK     | Python SDK         |
| ------------ | --------------- | ------------------ | ------------------ |
| OpenAI       | LLM             | :white_check_mark: | :white_check_mark: |
| Anthropic    | LLM             | :white_check_mark: | :white_check_mark: |
| Azure OpenAI | LLM             | :white_check_mark: | :white_check_mark: |
| Cohere       | LLM             | :white_check_mark: | :white_check_mark: |
| Groq         | LLM             | :x:                | :white_check_mark: |
| Langchain    | Framework       | :x:                | :white_check_mark: |
| LlamaIndex   | Framework       | :white_check_mark: | :white_check_mark: |
| Pinecone     | Vector Database | :white_check_mark: | :white_check_mark: |
| ChromaDB     | Vector Database | :white_check_mark: | :white_check_mark: |
| QDrant       | Vector Database | :x:                | :white_check_mark: |

---

## Feature Requests and Issues

- To request for features, head over [here to start a discussion](https://github.com/Scale3-Labs/langtrace/discussions/categories/feature-requests).
- To raise an issue, head over [here and create an issue](https://github.com/Scale3-Labs/langtrace/issues).

---

## Contributions

We welcome contributions to this project. To get started, fork this repository and start developing. To get involved, join our [Discord](https://discord.langtrace.ai) workspace.

If you want to run any of the examples go to `run_example.py` file, you will find `ENABLED_EXAMPLES`. choose the example you want to run and just toggle the flag to `True` and run the file using `python src/run_example.py`

---

## Security

To report security vulnerabilites, email us at <security@scale3labs.com>. You can read more on security [here](https://github.com/Scale3-Labs/langtrace/blob/development/SECURITY.md).

---

## License

- Langtrace application is [licensed](https://github.com/Scale3-Labs/langtrace/blob/development/LICENSE) under the AGPL 3.0 License. You can read about this license [here](https://www.gnu.org/licenses/agpl-3.0.en.html).
- Langtrace SDKs are licensed under the Apache 2.0 License. You can read about this license [here](https://www.apache.org/licenses/LICENSE-2.0).
