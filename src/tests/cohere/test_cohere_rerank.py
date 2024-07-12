from langtrace_python_sdk.constants import LANGTRACE_SDK_NAME
from langtrace_python_sdk.constants.instrumentation.common import SERVICE_PROVIDERS
import pytest
import json
from langtrace_python_sdk.constants.instrumentation.cohere import APIS
from tests.utils import assert_token_count
from importlib_metadata import version as v
from langtrace.trace_attributes import SpanAttributes


@pytest.mark.vcr
def test_cohere_rerank(cohere_client, exporter):
    llm_model_value = "rerank-english-v2.0"
    query = "What is the capital of the United States?"
    docs = [
        "Carson City is the capital city of the American state of Nevada.",
        "The Commonwealth of the Northern Mariana Islands is a group of islands in the Pacific Ocean. Its capital is Saipan.",
        "Washington, D.C. (also known as simply Washington or D.C., and officially as the District of Columbia) is the capital of the United States. It is a federal district.",
        "Capital punishment (the death penalty) has existed in the United States since beforethe United States was a country. As of 2017, capital punishment is legal in 30 of the 50 states.",
    ]

    kwargs = {
        "model": llm_model_value,
        "query": query,
        "documents": docs,
        "top_n": 3,
    }

    results = cohere_client.rerank(**kwargs)
    spans = exporter.get_finished_spans()
    cohere_span = spans[-1]
    assert cohere_span.name == APIS["RERANK"]["METHOD"]
    attributes = cohere_span.attributes

    assert attributes.get(SpanAttributes.LANGTRACE_SDK_NAME) == LANGTRACE_SDK_NAME

    assert (
        attributes.get(SpanAttributes.LANGTRACE_SERVICE_NAME)
        == SERVICE_PROVIDERS["COHERE"]
    )
    assert attributes.get(SpanAttributes.LANGTRACE_SERVICE_TYPE) == "llm"
    assert attributes.get(SpanAttributes.LANGTRACE_SERVICE_VERSION) == v("cohere")
    assert attributes.get(SpanAttributes.LANGTRACE_VERSION) == v(LANGTRACE_SDK_NAME)
    assert attributes.get(SpanAttributes.LLM_URL) == APIS["RERANK"]["URL"]
    assert attributes.get(SpanAttributes.LLM_PATH) == APIS["RERANK"]["ENDPOINT"]
    assert attributes.get(SpanAttributes.LLM_REQUEST_MODEL) == llm_model_value

    langtrace_results = json.loads(
        attributes.get(SpanAttributes.LLM_COHERE_RERANK_RESULTS)
    )
    for idx, res in enumerate(results.results):
        lang_res = json.loads(langtrace_results[idx])
        assert lang_res["index"] == res.index
        assert lang_res["relevance_score"] == res.relevance_score

    assert_token_count(attributes)
