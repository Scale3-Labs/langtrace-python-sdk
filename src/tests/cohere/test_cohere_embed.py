from langtrace_python_sdk.constants.instrumentation.cohere import APIS
from langtrace_python_sdk.constants.instrumentation.common import SERVICE_PROVIDERS
import pytest
from importlib_metadata import version as v

from langtrace_python_sdk.constants import LANGTRACE_SDK_NAME
from langtrace.trace_attributes import SpanAttributes


@pytest.mark.vcr
def test_cohere_embed(cohere_client, exporter):
    llm_model_value = "embed-english-v3.0"
    texts = ["hello", "goodbye"]
    input_type = "classification"

    kwargs = {
        "model": llm_model_value,
        "texts": texts,
        "input_type": input_type,
    }

    cohere_client.embed(**kwargs)
    spans = exporter.get_finished_spans()
    cohere_span = spans[-1]
    assert cohere_span.name == APIS["EMBED"]["METHOD"]
    attributes = cohere_span.attributes

    assert attributes.get(SpanAttributes.LANGTRACE_SDK_NAME) == LANGTRACE_SDK_NAME
    assert (
        attributes.get(SpanAttributes.LANGTRACE_SERVICE_NAME)
        == SERVICE_PROVIDERS["COHERE"]
    )
    assert attributes.get(SpanAttributes.LANGTRACE_SERVICE_TYPE) == "llm"
    assert attributes.get(SpanAttributes.LANGTRACE_SERVICE_VERSION) == v("cohere")
    assert attributes.get(SpanAttributes.LANGTRACE_VERSION) == v(LANGTRACE_SDK_NAME)
    assert attributes.get(SpanAttributes.LLM_URL) == APIS["EMBED"]["URL"]
    assert attributes.get(SpanAttributes.LLM_PATH) == APIS["EMBED"]["ENDPOINT"]
    assert attributes.get(SpanAttributes.LLM_REQUEST_MODEL) == llm_model_value
