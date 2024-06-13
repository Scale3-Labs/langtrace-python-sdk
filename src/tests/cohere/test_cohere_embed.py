from langtrace_python_sdk.constants.instrumentation.cohere import APIS
from langtrace_python_sdk.constants.instrumentation.common import SERVICE_PROVIDERS
import pytest
from importlib_metadata import version as v

from langtrace_python_sdk.constants import LANGTRACE_SDK_NAME


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

    assert attributes.get("langtrace.sdk.name") == "langtrace-python-sdk"
    assert attributes.get("langtrace.service.name") == SERVICE_PROVIDERS["COHERE"]
    assert attributes.get("langtrace.service.type") == "llm"
    assert attributes.get("langtrace.service.version") == v("cohere")

    assert attributes.get("langtrace.version") == v(LANGTRACE_SDK_NAME)
    assert attributes.get("url.full") == APIS["EMBED"]["URL"]
    assert attributes.get("llm.api") == APIS["EMBED"]["ENDPOINT"]
    assert attributes.get("llm.model") == llm_model_value
